#!/bin/python3
import argparse
import os
from blender_gazebo.gazebo_model import copy_model_with_different_name, GazeboModel

def main():
    parser = argparse.ArgumentParser(prog="HOLA", conflict_handler="resolve")
    parser.add_argument("--models_folder","-f",required="True")
    parser.add_argument("--model_to_copy","-c",required="True")
    parser.add_argument("--new_name","-p",required="True")
    args = parser.parse_known_args()[0]
    print(args)
    
    models_folder = args.models_folder
    model_to_copy = args.model_to_copy
    new_name = args.new_name
    
    path_to_model = os.path.join(models_folder, model_to_copy)
    assert os.path.isdir(path_to_model), f"path {path_to_model} does not exist"
    copy_model_with_different_name(GazeboModel(path_to_model), new_name)

if __name__ == "__main__":
    main()