"""By Lorenzo Cano Andres
Classes to manipulate gazebo models and their different components
"""
# IMPORTS
from xml.etree import ElementTree
import os
import shutil


# GLOBAL VARIABLES
SUBT_MODELS_DIRECTORY = "/home/lorenzo/catkin_ws/src/danilo/subt_gazebo/models_"

# FUNCTIONS
# -----------------------------------------------------------------------------------------------------------------------------------


def models_from_folder(folder: str):
    """Given a folder containing gazebo models, iterate
    over elements of folder and create instances of GazeboModel 
    for each"""
    assert os.path.isdir(folder)
    list_of_models = list()
    for model_name in os.listdir(folder):
        try:
            list_of_models.append(GazeboModel(
                os.path.join(folder, model_name)))
        except Exception as e:
            print(e)
    return list_of_models

# -----------------------------------------------------------------------------------------------------------------------------------


def is_type_in_folder(folder, type_termination):
    """Given a folder containing files and a type of file indicated
    as as the file termination, return the number of files that end on that termination"""
    number = 0
    l = len(type_termination)
    for filename in os.listdir(folder):
        if filename[-l:] == type_termination:
            number += 1
    return number

# -----------------------------------------------------------------------------------------------------------------------------------


def try_to_fix_xml_file(path):
    """This function tries to use all the different fixes, until one reports a positive fix"""
    if try_fix_xml_for_first_line(path):
        return True
    else:
        return False


# -----------------------------------------------------------------------------------------------------------------------------------


def try_fix_xml_for_first_line(path):
    """In case an .xml file starts with an empty line, it deletes it"""
    try:
        with open(path, "r") as f:
            lines = f.readlines()
        if lines[0] == "\n":
            lines.pop(0)
            with open(path, "w") as f:
                f.writelines(lines)
            return True
        else:
            return False
    except:
        raise

# CLASSES


class GazeboModel:
    """Basic class to manage the subfolders and files that compose a gazebo model"""

    def __init__(self, path):
        self.base_folder = path
        self.name = os.path.basename(path)
        self._check_contents_of_base_folder()
        self._parse_sdf_file()

    def __str__(self):
        return f"{self.__class__.__name__} of {self.name}"

    def _check_contents_of_base_folder(self):
        """Check that the model contains the files that are expected of it, raise
        an exception if that is not the case"""
        subdirs = os.listdir(self.base_folder)
        try:
            assert "model.config" in subdirs, f"no model.config for {self.base_folder}"
            self.config_file_path = os.path.join(
                self.base_folder, "model.config")
            assert "model.sdf" in subdirs, f"no model.sdf for {self.base_folder}"
            self.sdf_file_path = os.path.join(self.base_folder, "model.sdf")
            assert "meshes" in subdirs, f"no mesh folder for {self.base_folder}"
            self.meshes_folder = os.path.join(self.base_folder, "meshes")
        except AssertionError:
            raise

    def _parse_sdf_file(self, after_fix=False):
        """This function reads the .sdf (which is an .xml) file and tries to find the meshes 
        mentioned in it in the meshes file, in the case that it finds them, 
        it stores the path to the mesh files, and sets the 'local_meshes' to true"""
        # Load the xml_file as an xml_tree
        try:
            self.xml_tree = ElementTree.ElementTree(file=self.sdf_file_path)
        except:
            if not after_fix:
                if try_to_fix_xml_file(self.sdf_file_path):
                    self._parse_sdf_file(after_fix=True)
            else:
                raise Exception(
                    f"Problem reading xml file for {self.name} and no fix available")
        # Get get the meshes from the model
        self.meshes = list()
        for child in self.xml_tree.iter():
            if child.tag == "mesh":
                mesh_data = {}
                for mesh_member in child:
                    mesh_data[mesh_member.tag] = mesh_member.text
                m = GazeboModelMesh(self, mesh_data)
                if not m in self.meshes:
                    self.meshes.append(m)

# -----------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------


class GazeboModelMesh:
    """This class will be used to manipulate the data of the meshes used
    by the gazebo models. All the interaction with the files should be done 
    from this class"""

    def __init__(self, parent: GazeboModel, data: dict):
        self.parent = parent
        self.data = data
        self._parse_data()
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def __str__(self):
        return f"Model mesh: {self.uri}"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __eq__(self, other):
        """A mesh is equal to other mesh if they point to the same file"""
        if isinstance(other, self.__class__):
            return other.path == self.path
        return False

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _parse_data(self):
        '''Process the data dictionary'''
        self.uri = self.data["uri"] if "uri" in self.data.keys() else None
        self.scale = tuple([float(i) for i in self.data["scale"].split(" ")]) if "scale" in self.data.keys() else (
            1.0, 1.0, 1.0)
        if not self.uri is None:
            self.path = os.path.join(
                self.parent.base_folder, "meshes", os.path.basename(self.uri))
            self.folder, self.file_name = os.path.split(self.path)
            _, self.file_type = os.path.splitext(self.path)
            self.backup_file_name = "__bkp__" + self.file_name
            self.backup_path = os.path.join(self.folder, self.backup_file_name)
            if not os.path.exists(self.path):
                raise Exception("The mesh file does not exist")

        else:
            self.path = None

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def save_backup(self):
        '''This function saves the data currently in the file pointed by this instance, 
        in the same folder, with the same name, but with __bkp__ added'''
        shutil.copy(self.path, self.backup_path)
    
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def restore_backup(self):
        '''If there is a backup file, this function restores it'''
        if os.path.exists(self.backup_file_name):
            shutil.copy(self.backup_path,self.path)
        else:
            raise Exception(f"No backup for {self.path} mesh")

        
        
        

# MAIN
def main():
    models = models_from_folder(SUBT_MODELS_DIRECTORY)
    n_dae, n_obj = 0, 0
    for model in models:
        for mesh in model.meshes:
            assert isinstance(mesh, GazeboModelMesh)
            n_dae += int(mesh.file_type in (".dae", ".DAE"))
            n_obj += int(mesh.file_type in (".obj"))
        print(f"N dae: ")

if __name__ == "__main__":
    main()
