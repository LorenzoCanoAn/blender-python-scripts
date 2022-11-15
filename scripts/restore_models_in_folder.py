"""
For all the models in a folder this script 
restores all the files in the models to their 
corresponding backups
"""
from  blender_gazebo.gazebo_blender_model import models_from_folder, GazeboBlenderModel
from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument('--folder', '-f')
    args = parser.parse_known_args()[0]

    models = models_from_folder(args.folder)

    for n, model in enumerate(models):
        assert isinstance(model, GazeboBlenderModel)
        try:
            model.restore_from_backup()
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()