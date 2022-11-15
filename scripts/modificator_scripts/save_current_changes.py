import os
import blender_gazebo.gazebo_blender_model
import blender_gazebo.blender_functions
from importlib import reload
reload(blender_gazebo.blender_functions)
reload(blender_gazebo.gazebo_blender_model)
reload(blender_gazebo.blender_functions)
from blender_gazebo.gazebo_blender_model import GazeboBlenderModel, GazeboModelMesh, BlenderMeshInfo
import blender_gazebo.blender_functions as blender
try:
    path_to_model = os.environ["path_to_model"]
except:
    raise Exception("The 'path_to_model' environmental variable has not been set")

model = GazeboBlenderModel(path_to_model)

blender.save_mesh(model.meshes[0].path)