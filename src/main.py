import textnode
import utils
import re

def main():
    # creates a dest folder and also places any Non-Markdown content into the folder such as images and .css files from a static/ folder
    utils.create_public_dir()
    # converts all Md content into html files and places them at the dest path (make sure only md files are present in the source folder)
    utils.generate_pages_recursive("./content","./template.html","./public")

if __name__ == "__main__":
    main()