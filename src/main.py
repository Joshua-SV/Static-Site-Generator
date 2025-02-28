import textnode
import utils
import os
import shutil
import re

def main():
    # obj = textnode.TextNode("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg) ![](fsaffasf.com)", textnode.TextType.NORMAL)

    create_public_dir()

# function that recursively creates a public directory with folders and subdirectories from a source folder
def create_public_dir():
    path_des = "./public/"
    path_src = "./static/"
    # check if destination and source directories exist based on current working directory
    doesDesExist = os.path.exists(path_des) 
    doesSrcExist = os.path.exists(path_src)

    # if the source folder is not found raise an error
    if not doesSrcExist:
        raise Exception("No Source directory called static was found.")
    # if destination is found then delete it and all its contents
    if doesDesExist:
        shutil.rmtree(path_des)
    # create destination folder with user having full access
    os.mkdir(path_des, mode=0o755)

    # get initial list of items in the source folder
    init_lst = os.listdir("static/")
    # perform recursive to fill des folder with src folder items
    helper_fill_folder(init_lst, path_src, path_des)

def helper_fill_folder(source_lst, src_path, des_path):
    for item in source_lst:
        # if the item is a file then copy it to des folder
        if os.path.isfile(f"{src_path}/{item}"):
            shutil.copy(f"{src_path}/{item}",f"{des_path}")
        # else if it is a folder
        elif os.path.isdir(f"{src_path}/{item}"):
            # get its list of items
            new_src_lst = os.listdir(f"{src_path}/{item}")
            # create folder in the des folder
            os.mkdir(f"{des_path}/{item}")
            # recursively go through the subfolder items
            helper_fill_folder(new_src_lst, f"{src_path}/{item}", f"{des_path}/{item}")
    return

if __name__ == "__main__":
    main()