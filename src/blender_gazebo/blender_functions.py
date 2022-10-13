import os
import bpy
from blender_gazebo.gazebo_model import models_from_folder, GazeboModel, GazeboModelMesh



def clear_workspace():
    """
    Delete all the objects in the current blender instance
    """
    objs = bpy.data.objects
    for k in objs.keys():
        objs.remove(objs[k], do_unlink=True)

def load_model(model: GazeboModel):
    """
    Load all the mesh files in the gazebo model into blender
    """
    assert isinstance(model, GazeboModel)
    for mesh in model.meshes:
        assert isinstance(mesh, GazeboModelMesh)
        load_mesh(mesh)

def load_mesh(mesh: GazeboModelMesh):
    """
    Load the file pointed by the mesh object into blender
    """
    if mesh.file_type in (".obj"):
        bpy.ops.import_scene.obj(filepath=mesh.path)
    elif mesh.file_type in (".dae", ".DAE"):
        bpy.ops.wm.collada_import(filepath=mesh.path)

#-----------------------------------------------------------------------------------------------------------------------------------
def save_mesh(file_path):
    """
    Save the current selected mesh in blender to the specified file,
    if no file is specified, it is saved to the original file of the mesh.
    """
    base, extension = os.path.splitext(file_path)
    if str.lower(extension) == ".obj":
        bpy.ops.export_scene.obj(filepath=file_path)
    elif str.lower(extension) == ".dae":
        bpy.ops.wm.collada_export(filepath=file_path)
