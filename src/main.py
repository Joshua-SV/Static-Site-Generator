import textnode
import utils
import re
import sys

def main():
    # get the second arguement passed by the CLI
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = "/"
    
    # creates a dest folder and also places any Non-Markdown content into the folder such as images and .css files from a static/ folder
    utils.create_public_dir("docs")
    # converts all Md content into html files and places them at the dest path (make sure only md files are present in the source folder)
    utils.generate_pages_recursive(f"content", f"template.html", f"docs", basepath)


if __name__ == "__main__":
    main()