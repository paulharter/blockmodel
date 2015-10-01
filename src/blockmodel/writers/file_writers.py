import os
import shutil



THIS_DIR = os.path.dirname(__file__)
RESOURCE_DIR = os.path.join(THIS_DIR, "..", "resources")

def write_stl(file_path, stl_binary_data):

    file_path = _check_file_path(file_path, "stl")

    with open(file_path, "wb") as f:
        f.write(stl_binary_data)


def write_csv(file_path, csv_string):

    file_path = _check_file_path(file_path, "csv")

    with open(file_path, "w") as f:
        f.write(csv_string)


def write_x3d(file_path, x3d_string):

    dir_path, file_path = _check_file_path(file_path, "x3d", in_folder=True)

    with open(file_path, "w") as f:
        f.write(x3d_string)

    #add the texture
    shutil.copy(os.path.join(RESOURCE_DIR, "terrain_big.png"), dir_path)



def write_collada(file_path, collada_string):

    dir_path, file_path = _check_file_path(file_path, "dae", in_folder=True)

    with open(file_path, "w") as f:
        f.write(collada_string)

    #add the texture
    shutil.copy(os.path.join(RESOURCE_DIR, "terrain.png"), dir_path)


def write_obj(file_path, obj_string):

    dir_path, file_path = _check_file_path(file_path, "obj", in_folder=True)

    with open(file_path, "w") as f:
        f.write(obj_string)

    #add the texture
    shutil.copy(os.path.join(RESOURCE_DIR, "terrain_big.png"), dir_path)
    shutil.copy(os.path.join(RESOURCE_DIR, "printcraft.mtl"), dir_path)


def _check_file_path(file_path, ext, in_folder=False):

    dir, file_name = os.path.split(file_path)

    abspath = os.path.abspath(dir)
    if not os.path.exists(abspath):
        raise Exception("You cannot save a {} file to a non existent folder{}. Create it first".format(ext, abspath))

    if not file_name.endswith(ext):
        file_name = "{}.{}".format(file_name, ext)

    if in_folder:
        base_name = file_name.replace(".", "_")
        dir_path = os.path.join(abspath, base_name)
        file_path = os.path.join(dir_path, file_name)

        if os.path.exists(dir_path):
            raise Exception("This file already exists. Delete it before writing a new one")

        os.makedirs(dir_path)
        return dir_path, file_path
    else:
        full_path = os.path.join(abspath, file_name)

        if os.path.exists(full_path):
            raise Exception("This file already exists. Delete it before writing a new one")

        return full_path

