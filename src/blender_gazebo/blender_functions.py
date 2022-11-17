import os
import bpy
from blender_gazebo.gazebo_blender_model import GazeboBlenderModel, GazeboModelMesh



#-----------------------------------------------------------------------------------------------------------------------------------
def clear_workspace():
    """
    Delete all the objects in the current blender instance
    """
    objs = bpy.data.objects
    for k in objs.keys():
        objs.remove(objs[k], do_unlink=True)

#-----------------------------------------------------------------------------------------------------------------------------------
def load_gazebo_model(model: GazeboBlenderModel):
    """
    Load all the mesh files of a gazebo model into blender
    """
    assert isinstance(model, GazeboBlenderModel)
    for mesh in model.meshes:
        assert isinstance(mesh, GazeboModelMesh)
        load_gazebo_mesh(mesh)

#-----------------------------------------------------------------------------------------------------------------------------------
def load_gazebo_mesh(mesh: GazeboModelMesh):
    """
    Load the file pointed by the mesh object into blender
    """
    if mesh.file_type in (".obj"):
        return bpy.ops.import_scene.obj(filepath=mesh.path)
    elif mesh.file_type in (".dae", ".DAE"):
        return bpy.ops.wm.collada_import(filepath=mesh.path)

#-----------------------------------------------------------------------------------------------------------------------------------
def get_selected_points():
    """Returns a list with the indices of the selected points for a certain mesh"""
    mode = bpy.context.active_object.mode
    # we need to switch from Edit mode to Object mode so the selection gets updated
    bpy.ops.object.mode_set(mode='OBJECT')
    selected_vertices = {}
    for obj_key in bpy.data.objects.keys():
        selected_vertices[obj_key] =  []
        for i in range(bpy.data.objects.get(obj_key).data.vertices.__len__()):
            if bpy.data.objects.get(obj_key).data.vertices[i].select:
                selected_vertices[obj_key].append(i)

    # back to whatever mode we were in
    bpy.ops.object.mode_set(mode=mode)
    return selected_vertices

#-----------------------------------------------------------------------------------------------------------------------------------
def toogle_selected_points():
    mode = bpy.context.active_object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    for obj_key in bpy.data.objects.keys():
        obj = bpy.data.objects.get(obj_key)

        to_select = []
        for i in range(obj.data.vertices.__len__()):
            if not bpy.data.objects.get(obj_key).data.vertices[i].select:
                to_select.append(i) 
        for polygon in obj.data.polygons:
            polygon.select = False
        for edge in obj.data.edges:
            edge.select = False
        for vertex in obj.data.vertices:
            vertex.select = False
        for i in to_select:
            obj.data.vertices[i].select = True
    bpy.ops.object.mode_set(mode=mode)

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
    print("MODEL SAVED")

def deselect_everything():
    """Deselect every vertex, edge and polygon"""
    for key in bpy.data.objects.keys():
        obj = bpy.data.objects[key]
        for polygon in obj.data.polygons:
            polygon.select = False
        for edge in obj.data.edges:
            edge.select = False
        for vertex in obj.data.vertices:
            vertex.select = False

def select_points(points_to_select, deselect_previous = True):
    for key in points_to_select.keys():
        obj = bpy.data.objects.get(key)
        p_indices = points_to_select[key]
        if deselect_previous:
            deselect_everything()
        for i in p_indices:
            obj.data.vertices[i].select = True