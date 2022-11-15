#!/bin/python3
"""
This script takes 
"""
import argparse
import os
from blender_gazebo.gazebo_blender_model import copy_model_with_different_name, GazeboBlenderModel

def main():
    parser = argparse.ArgumentParser(prog="copy_model_with_new_name", conflict_handler="resolve")
    parser.add_argument("--models_folder","-f",required=True, help="Folder that contains the model to be copied")
    parser.add_argument("--model_to_copy","-c",required=True, help="Name of the model to be copied")
    parser.add_argument("--new_name","-p",required=True)
    parser.add_argument("--destination_folder","-d",default=None, help="If none, the new model will be created in the models_folder folder")
    args = parser.parse_known_args()[0]
    
    models_folder = args.models_folder
    model_to_copy = args.model_to_copy
    new_name = args.new_name
    destination_folder = args.destination_folder
    if destination_folder is None and model_to_copy==new_name:
        raise Exception("The new name of the model should be different from the original name, or the copy should be pasted in a different folder") 
    path_to_model = os.path.join(models_folder, model_to_copy)
    assert os.path.isdir(path_to_model), f"path {path_to_model} does not exist"
    copy_model_with_different_name(GazeboBlenderModel(path_to_model), new_name, destination_folder=destination_folder)

if __name__ == "__main__":
    main()