import os

try:
    del os.environ["models_folder"]
    del os.environ["model_number"]
except:
    pass

os.environ["model_number"] = "0"
