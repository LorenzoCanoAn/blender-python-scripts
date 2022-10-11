import bpy
import sys 
print(sys.path)
import matplotlib
from gazebo_model import models_from_folder, GazeboModel, GazeboModelMesh


# -----------------------------------------------------------------------------------------------------------------------------------


def delete_all_models():
    objs = bpy.data.objects
    for k in objs.keys():
        objs.remove(objs[k], do_unlink=True)

def load_model(model: GazeboModel):
    delete_all_models()
    for mesh in model.meshes:
        assert isinstance(mesh, GazeboModelMesh)
        print(mesh.path)
def main():
    models = models_from_folder
    for model in models:
        load_model(model)

if __name__ == "__main__":
    main()
