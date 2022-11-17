"""
The purpose of this script is:
    1) To copy a tile model with a different name
    2) Load the mesh of that model into blender
    3) Randomize the points of the mesh
    4) Save the modified mesh
"""
####################################################################################################################################
#	IMPORTS
####################################################################################################################################
import os
import blender_gazebo.blender_functions
import blender_gazebo.gazebo_blender_model
from importlib import reload
reload(blender_gazebo.blender_functions)
reload(blender_gazebo.gazebo_blender_model)
reload(blender_gazebo.blender_functions)
import blender_gazebo.blender_functions as blender
from blender_gazebo.gazebo_blender_model import GazeboBlenderModel, copy_model_with_different_name, GazeboModelMesh
import bpy
import random
####################################################################################################################################
#	PARAMETERS
####################################################################################################################################
MODIFICATION_TYPES = {0:"only_upper", 1:"only_ground", 3:"all_points"}
TYPE_OF_MODIFICATION = MODIFICATION_TYPES[0]
DO_ONLY_ONE_MODEL = False
MODEL_NAME = "cave_tile_1"
MODELS_FOLDER = "/home/lorenzo/git/subt_gazebo/models/tilable_and_modifiable"
MODIFIED_MODELS_FOLDER = "/home/lorenzo/git/subt_gazebo/models/modified"
NUMBER_OF_MODIFICATIONS = 50
MAGNITUDE_OF_MODIFICATION = 0.5
SEQUENTIAL_MODIFICATIONS = 4

####################################################################################################################################
#	FUNCTIONS
####################################################################################################################################
def modify_model(model, type_of_modification):
    assert isinstance(model, GazeboBlenderModel)
    if type_of_modification == MODIFICATION_TYPES[0]:
        for mesh in model.meshes:
            assert isinstance(mesh, GazeboModelMesh)
            mesh.select_ground_points()
            bpy.ops.object.mode_set(mode='EDIT')
            for _ in range(SEQUENTIAL_MODIFICATIONS):
                bpy.ops.transform.vertex_random(offset=MAGNITUDE_OF_MODIFICATION, seed=random.randint(0,10000))

#-----------------------------------------------------------------------------------------------------------------------------------
def main():
    save_folder = os.path.join(MODIFIED_MODELS_FOLDER, TYPE_OF_MODIFICATION)
    if DO_ONLY_ONE_MODEL:
        if MODEL_NAME is None:
            raise Exception("The model name should be specified")
        else:
            model_names = [MODEL_NAME]
    else:
        model_names = os.listdir(MODELS_FOLDER)
    models = [GazeboBlenderModel(os.path.join(MODELS_FOLDER, name)) for name in model_names] 

    for model in models:
        for n in range(NUMBER_OF_MODIFICATIONS):
            model_type_save_folder = os.path.join(save_folder, model.name)
            new_name = model.name + f"_mod_{n}"
            copied_model = copy_model_with_different_name(model,new_name,destination_folder=model_type_save_folder )
            blender.clear_workspace()
            blender.load_gazebo_model(copied_model)
            modify_model(copied_model,TYPE_OF_MODIFICATION)
            blender.save_mesh(copied_model.meshes[0].path) 
    
if __name__ == "__main__":
    main()