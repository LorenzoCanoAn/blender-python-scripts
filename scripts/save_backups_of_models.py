from  blender_gazebo.gazebo_model import models_from_folder, GazeboModel, GazeboModelMesh

SUBT_MODELS_DIRECTORY = "/home/lorenzo/catkin_ws/src/danilo/subt_gazebo/models_"
models = models_from_folder(SUBT_MODELS_DIRECTORY)


for n, model in enumerate(models):
    assert isinstance(model, GazeboModel)
    try:
        model.create_backup()
    except Exception as e:
        print(e)