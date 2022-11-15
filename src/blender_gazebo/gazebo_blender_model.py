"""By Lorenzo Cano Andres
Classes to manipulate gazebo models and their different components, and to manipulate them in
Blender.
"""
# IMPORTS
from xml.etree.ElementTree import ElementTree
import os
import json
import shutil
from subprocess import call


# GLOBAL VARIABLES
SUBT_MODELS_DIRECTORY = "/home/lorenzo/git/subt_gazebo/models"

# FUNCTIONS
# -----------------------------------------------------------------------------------------------------------------------------------
def cp_dir(source, target):
    """
    Copy the source directory and all its contents
    to the target directory. To work as intended, the target 
    directory should not exist
    """
    call(['cp', '-a', source, target]) # Linux


#-----------------------------------------------------------------------------------------------------------------------------------
def models_from_folder(folder: str):
    """
    Given a folder containing gazebo models, iterate
    over elements of folder and create instances of GazeboModel 
    for each
    """
    assert os.path.isdir(folder)
    list_of_models = list()
    for model_name in os.listdir(folder):
        try:
            list_of_models.append(GazeboBlenderModel(
                os.path.join(folder, model_name)))
        except Exception as e:
            print(e)
    return list_of_models
    
#-----------------------------------------------------------------------------------------------------------------------------------
def copy_model_with_different_name(model, new_name, destination_folder  = None):
    '''
    This function takes a GazeboModel object, and copies it to 
    a different folder, changing the name inside the archives
    The things that have to be changed are:
    - The name of the folder
    - The name in the model.sdf file
    - The name in the model.config file
    - The uri of the meshes inside the model.sdf files
    '''
    assert isinstance(model, GazeboBlenderModel)
    # First, copy all the contents fo the model to new folder
    models_folder = os.path.dirname(model.base_folder)
    if destination_folder is None:
        copied_model_path = os.path.join(models_folder, new_name)
    else:
        os.makedirs(destination_folder, exist_ok=True)
        copied_model_path = os.path.join(destination_folder, new_name)
    if os.path.isdir(copied_model_path):
        shutil.rmtree(copied_model_path)
    cp_dir(model.base_folder, copied_model_path)
    # Second change the name in the model.config and model.sdf files
    copied_model = GazeboBlenderModel(copied_model_path)
    copied_model.change_name(new_name)
    # Third, change the base path of the URIs of the meshes
    for mesh in copied_model.meshes:
        assert isinstance(mesh, GazeboModelMesh)
        for xml_reference in mesh.xml_elements:
            original_uri = xml_reference.find("uri").text
            new_uri = change_uri_root(original_uri, new_name)
            xml_reference.find("uri").text = new_uri
            print(xml_reference.find("uri").text)
    copied_model.write_sdf_file()
    
#-----------------------------------------------------------------------------------------------------------------------------------
def is_type_in_folder(folder, type_termination):
    """
    Given a folder containing files and a type of file indicated
    as as the file termination, return the number of files that end on that termination
    """
    number = 0
    l = len(type_termination)
    for filename in os.listdir(folder):
        if filename[-l:] == type_termination:
            number += 1
    return number

#-----------------------------------------------------------------------------------------------------------------------------------
def try_to_fix_xml_file(path):
    """
    This function tries to use all the different fixes, until one reports a positive fix
    """
    if try_fix_xml_for_first_line(path):
        return True
    else:
        return False

# -----------------------------------------------------------------------------------------------------------------------------------
def try_fix_xml_for_first_line(path):
    """
    In case an .xml file starts with an empty line, it deletes it
    """
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

# -----------------------------------------------------------------------------------------------------------------------------------
def load_xml_file(path,  after_fix= False):
    """
    Create an ElementTree form an .xml file, 
    if it fails, try to fix it, and open it again.
    If it fails again, raises an exception.
    """
    try:
        tree = ElementTree(file=path)
    except:
        if not after_fix:
            if try_to_fix_xml_file(path):
                tree = load_xml_file(path, after_fix=True)
        else:
            raise Exception(
                f"Problem reading xml file for {path} and no fix available")
    return tree

#-----------------------------------------------------------------------------------------------------------------------------------
def change_uri_root(original_gazebo_uri, new_model_name):
    """
    This functiontakes an uri in the format:
    model://MODEL_NAME/INTERNAL_PATH_TO_MESH
    Where MODEL_NAME is the name of a gazebo model
    and the INTERNAL_PATH is the path from the base folder of
    the model to the specific file that the uri references.
    This funciton substitutes the MODEL_NAME for a new one
    """
    uri_elements = original_gazebo_uri.replace("model://","").split("/")
    uri_elements[0] = new_model_name
    new_uri = "model:/"
    for element in uri_elements:
        new_uri += "/" + element
    return new_uri
    
     

# CLASSES

class GazeboBlenderModel:
    """
    Basic class to manage the subfolders and files that compose a gazebo model
    and to handle changes to the model in Blender
    """

    def __init__(self, path):
        self.base_folder = path
        self.name = os.path.basename(path)
        self._check_contents_of_base_folder()
        self._load_files()
        self._parse_sdf_file()

    def __str__(self):
        return f"{self.__class__.__name__} of {self.name}"

    def _check_contents_of_base_folder(self):
        """
        Check that the model contains the files that are expected of it, raise
        an exception if that is not the case
        """
        model_contents = os.listdir(self.base_folder)
        try:
            assert "model.config" in model_contents, f"no model.config for {self.base_folder}"
            self.config_file_path = os.path.join(
                self.base_folder, "model.config")
            assert "model.sdf" in model_contents, f"no model.sdf for {self.base_folder}"
            self.sdf_file_path = os.path.join(self.base_folder, "model.sdf")
            self.sdf_bkp_file_path = os.path.join(self.base_folder, "__bkp__model.sdf")
            assert "meshes" in model_contents, f"no mesh folder for {self.base_folder}"
            self.meshes_folder = os.path.join(self.base_folder, "meshes")
        except AssertionError:
            raise
    
    def _load_files(self, after_fix = False):
        """
        Loadoad the desired .xml file and report return it as a elementtree
        """
        self.config_tree = load_xml_file(self.config_file_path)
        self.sdf_tree = load_xml_file(self.sdf_file_path)

    def _parse_sdf_file(self, after_fix=False):
        """
        Reads the .sdf (which is an .xml) file and tries to find the meshes 
        mentioned in it in the meshes file, in the case that it finds them, 
        it stores the path to the mesh files, and sets the 'local_meshes' to true
        """
        # Extrat the relevant info fromt the sdf file
        self.meshes = list()
        for child in self.sdf_tree.iter():
            if child.tag == "mesh":
                m = GazeboModelMesh(self, child)
                if not m in self.meshes:
                    self.meshes.append(m)
                else:
                    self.meshes[self.meshes.index(m)].add_xml_reference(child)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def write_sdf_file(self):
        '''
        Re-write the info in the model.sdf file
        '''
        self.sdf_tree.write(self.sdf_file_path)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def write_config_file(self):
        '''
        Re-write the info in the model.config file
        '''
        self.config_tree.write(self.config_file_path)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create_backup(self):
        """
        Copy the contents of all the mesh files and the model.sdf file into 
        a backup files
        """
        shutil.copy(self.sdf_file_path,self.sdf_bkp_file_path)
        for mesh in self.meshes:
            assert isinstance(mesh, GazeboModelMesh)
            mesh.create_backup()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def restore_from_backup(self):
        '''
        Restore the contents of the mesh files and the model.sdf file fromthe backup files
        '''
        shutil.copy(self.sdf_bkp_file_path, self.sdf_file_path)
        for mesh in self.meshes:
            assert isinstance(mesh, GazeboModelMesh)
            mesh.restore_from_backup()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def change_name(self, new_name):
        '''
        This function changes the name in the model.sdf and model.config files
        '''
        self.config_tree.find("name").text = new_name
        self.write_config_file()
        self.sdf_tree.find("model").attrib["name"] = new_name
        self.write_sdf_file()
        

# -----------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------


class GazeboModelMesh:
    """
    This class will be used to manipulate the data of the meshes used
    by the gazebo models. All the interaction with the files should be done 
    from this class
    """

    def __init__(self, parent: GazeboBlenderModel, xml_element):
        self.parent = parent
        self.xml_elements = [xml_element,]
        self._parse_data()
        self.mesh_info = BlenderMeshInfo(self)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
        return f"Model mesh: {self.uri}"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __eq__(self, other):
        """
        A mesh is equal to other mesh if they point to the same file
        """
        if isinstance(other, self.__class__):
            return other.path == self.path
        return False

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _parse_data(self):
        '''Process the data dictionary'''
        self.uri = self.xml_elements[0].find("uri").text
        self.scale = self.xml_elements[0].find("scale")
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
        if self.scale is None:
            self.scale = (1.0,1.0,1.0)
        else: 
            self.scale = tuple([float(i) for i in self.scale.text.split(" ")])

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create_backup(self):
        '''This function saves the data currently in the file pointed by this instance, 
        in the same folder, with the same name, but with __bkp__ added'''
        shutil.copy(self.path, self.backup_path)
    
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def restore_from_backup(self):
        '''If there is a backup file, this function restores it'''
        if os.path.exists(self.backup_path):
            shutil.copy(self.backup_path,self.path)
        else:
            raise Exception(f"{self.backup_path} does not exist")
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add_xml_reference(self, xml_element):
        '''If there is more than one mention of a mesh in a gazebo model,
        this add the mention to this object'''
        self.xml_elements.append(xml_element)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def update_scale_in_xml_references(self, new_scale):
        '''
        The new_scale should be entered as a string of "f f f".
        This method will go through all the mentions to this mesh in 
        the model.sdf file, updating the scale parameter to the desired
        one.
        '''
        for ref in self.xml_elements:
            scale_element = ref.find("scale")
            if not scale_element is None:
                scale_element.text = new_scale

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def update_uri_in_xml_references(self, new_uri):
        '''
        If the model should now load a new mesh file, this must be specified in the model.sdf (.xml)
        file. With this function, the new uri can be specified and it will be modified
        '''
        for ref in self.xml_elements:
            uri_element = ref.find("uri")
            if not uri_element is None:
                uri_element.text = new_uri

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
class BlenderMeshInfo:
    def __init__(self, parent: GazeboModelMesh):
        self.parent = parent
        self.parse_blender_data_file()

    def parse_blender_data_file(self):
        """
        Reads the blender_info.txt file in the model folder, and 
        stores the data inside this class
        """
        self.blender_data_file_path = os.path.splitext(self.parent.path)[0] + "_info.json"
        try:
            with open(self.blender_data_file_path,"r") as f:
                self.data = json.load(f)
        except: 
            self.data = {"UPPER_POINTS":{}, "GROUND_POINTS":{}}
            self.write_data_to_file()
            self.parse_blender_data_file()
 

    def write_data_to_file(self):
        with open(self.blender_data_file_path, "w") as f:
            f.write(json.dumps(self.data,indent=1))

    def set_new_ground_points(self, new_ground_points):
        self.data["GROUND_POINTS"] = new_ground_points 

    def set_new_upper_points(self, new_upper_points):
        self.data["UPPER_POINTS"] = new_upper_points



# MAIN
def main():
    models = models_from_folder(SUBT_MODELS_DIRECTORY)
    for model in models:
        for mesh in model.meshes:
            print(mesh.uri)
    copy_model_with_different_name(models[0], models[0].name+"-1")

if __name__ == "__main__":
    main()
