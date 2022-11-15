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
for mesh in model.meshes:
    assert isinstance(mesh, GazeboModelMesh)
    info = mesh.mesh_info
    assert isinstance(info, BlenderMeshInfo)
    info.set_new_upper_points(blender.get_selected_points())
    info.write_data_to_file()
print("UPPER POINTS RECORDED")
