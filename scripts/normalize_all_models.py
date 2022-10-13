"""
This script should be run from the Blender interpreter.
It will read a folder containing gazebo models and load them as GazeboModel instances, and make the following changes:
-   If the meshes of the model are saved locally, and are in the .obj format, it will save them as .dae, with the corresponding rotation needed
-   If the meshes of the model are imported into gazebo with a scale, it will scale the meshes and save them already scaled, so that they no longer 
    need to be imported with the scale
"""

from  blender_gazebo.gazebo_model import models_from_folder, GazeboModel, GazeboModelMesh
import blender_gazebo.blender_functions as blender
import bpy
import os
import math

SUBT_MODELS_DIRECTORY = "/home/lorenzo/catkin_ws/src/danilo/subt_gazebo/models_"
models = models_from_folder(SUBT_MODELS_DIRECTORY)


for n, model in enumerate(models):
    assert isinstance(model, GazeboModel)
    try:
        model_mesh = model.meshes[0]
        assert isinstance(model_mesh, GazeboModelMesh)
        blender.clear_workspace()
        blender.load_mesh(model_mesh)

        # If the mesh is scaled when imported to gazebo, set it to a scale of 1.
        if model_mesh.scale != (1.0, 1.0, 1.0):
            # Change the scale in blender
            bpy.ops.transform.resize(value=model_mesh.scale)
            # Change the scale in the model.sdf document
            model_mesh.update_scale_in_xml_references("1.0 1.0 1.0")
            # Save the model.sdf document
            model.update_sdf_file()
            # Save the mesh file with the change in scale 
            blender.save_mesh(model_mesh.path)

        # If the mesh is loaded from an .obj, rotate it, export it as a .dae, and modify the reference
        if str.lower(model_mesh.file_type) == ".obj":
            new_path = os.path.splitext(model_mesh.path)[0] + ".dae"
            new_uri = os.path.splitext(model_mesh.uri)[0] + ".dae"
            # Rotate the mesh
            bpy.ops.transform.rotate(value=math.pi/2,orient_axis="X",center_override=(0,0,0))
            # Save the new mesh as dae
            blender.save_mesh(new_path)
            # Save the new model.sdf file with the updated reference
            model_mesh.update_uri_in_xml_references(new_uri)
            model.update_sdf_file()
    except Exception as e:
        print(e)