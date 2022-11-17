####################################################################################################################################
####################################################################################################################################
#		LOAD NEXT MODEL
####################################################################################################################################
####################################################################################################################################

import blender_gazebo.blender_functions
import blender_gazebo.gazebo_blender_model
from importlib import reload
reload(blender_gazebo.blender_functions)
reload(blender_gazebo.gazebo_blender_model)
reload(blender_gazebo.blender_functions)
import os
import bpy

FOLDER = "/home/lorenzo/git/subt_gazebo/models/cave_tiles"
blender_gazebo.blender_functions.clear_workspace()
# Check if the models folder has been changed
try:
    os.environ["models_folder"]
except:
    os.environ["models_folder"] = FOLDER


# Check if it is the first time that this script has been run in a determined session
# If it is, set the model number to 0

try:
    model_number = int(os.environ["model_number"])
except:
    model_number = 0

# Load the models from the folder
models = blender_gazebo.gazebo_blender_model.models_from_folder(FOLDER)
if model_number >= len(models):
    model_number = 0
print(f"Loading model number {model_number}")
model = models[model_number]
assert isinstance(model, blender_gazebo.gazebo_blender_model.GazeboBlenderModel)
os.environ["path_to_model"] = model.base_folder
blender_gazebo.blender_functions.load_gazebo_model(model)
os.environ["model_number"] = str(model_number + 1)
bpy.ops.object.mode_set(mode="EDIT")