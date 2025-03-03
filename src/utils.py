import textnode
import leafnode
import parentnode
import re
import os
import shutil
from enum import Enum

class BlockType(Enum):
	PARAGRAPH = "paragraph"
	HEADING = "heading"
	QUOTE = "quote"
	CODE = "code"
	UNORDERED = "unordered"
	ORDERED = "ordered"

# inline markdown text
def text_node_to_html_node(text_node):
        """
        creates a leafnode from a textnode by using its type
        """
        match text_node.text_type:
            case textnode.TextType.NORMAL:
                return leafnode.LeafNode(None,text_node.text)
            case textnode.TextType.BOLD:
                return leafnode.LeafNode('b',text_node.text)
            case textnode.TextType.ITALIC:
                return leafnode.LeafNode('i',text_node.text)
            case textnode.TextType.CODE:
                return leafnode.LeafNode("code",text_node.text)
            case textnode.TextType.LINKS:
                return leafnode.LeafNode('a',text_node.text,{"href": text_node.url, "target": "_blank"})
            case textnode.TextType.IMAGES:
                return leafnode.LeafNode("img","",{"src": text_node.url, "alt": text_node.text})

def extract_markdown_images(text):
    """
    catches all markdown image urls and alt text and return a list of tuples
    """
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    """
    catches all markdown links urls and text and return a list of tuples
    """
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """
    Splits text nodes in `old_nodes` based on `delimiter`, converting 
    the delimited text into `text_type` (e.g., CODE, BOLD, ITALIC).
    """
    new_nodes = []

    for node in old_nodes:
        # If it's not a TEXT node, add it as-is
        if node.text_type != textnode.TextType.NORMAL:
            new_nodes.append(node)
            continue

        text_parts = node.text.split(delimiter)
        
        # If there's an odd number of parts, there's an unmatched delimiter. Assume it was part of normal string 
        if len(text_parts) % 2 == 0:
            new_nodes.append(node)
            continue
            # raise ValueError(f"Unmatched delimiter '{delimiter}' in text: {node.text}")

        for i, part in enumerate(text_parts):
            if part:  # Only append non-empty parts
                new_nodes.append(
                    textnode.TextNode(part, text_type if i % 2 else textnode.TextType.NORMAL)
                )

    return new_nodes

def splite_node_images(old_nodes):
    new_nodes = []

    for node in old_nodes:
        # If it's not a TEXT node, add it as-is
        if node.text_type != textnode.TextType.NORMAL:
            new_nodes.append(node)
            continue

        image_parts_list = extract_markdown_images(node.text)

        # if no image is found in the text append the node as-is
        if len(image_parts_list) == 0:
            new_nodes.append(node)
            continue

        text = node.text
        sections = []

        # loop all images
        for txt, url in image_parts_list:
            sections = text.split(f"![{txt}]({url})", 1)
            text = sections[1] if len(sections) > 0 else None

            if sections[0] == "":
                new_nodes.append(textnode.TextNode(txt, textnode.TextType.IMAGES, url))
            else:
                new_nodes.append(textnode.TextNode(sections.pop(0), textnode.TextType.NORMAL))
                new_nodes.append(textnode.TextNode(txt, textnode.TextType.IMAGES, url))

        # if all links have been extracted then append what is left from the text as a text node
        for sec in sections:
            if sec == "":
                continue
            else:
                new_nodes.append(textnode.TextNode(sec, textnode.TextType.NORMAL))
        
    return new_nodes

def splite_node_links(old_nodes):
    new_nodes = []

    for node in old_nodes:
        # If it's not a TEXT node, add it as-is
        if node.text_type != textnode.TextType.NORMAL:
            new_nodes.append(node)
            continue

        links_parts_list = extract_markdown_links(node.text)

        # if no image is found in the text append the node as-is
        if len(links_parts_list) == 0:
            new_nodes.append(node)
            continue

        text = node.text
        sections = []

        # loop all images
        for txt, url in links_parts_list:
            sections = text.split(f"[{txt}]({url})", 1)
            text = sections[1] if len(sections) > 0 else None

            if sections[0] == "":
                new_nodes.append(textnode.TextNode(txt, textnode.TextType.LINKS, url))
            else:
                new_nodes.append(textnode.TextNode(sections.pop(0), textnode.TextType.NORMAL))
                new_nodes.append(textnode.TextNode(txt, textnode.TextType.LINKS, url))

        # if all links have been extracted then append what is left from the text as a text node
        for sec in sections:
            if sec == "":
                continue
            else:
                new_nodes.append(textnode.TextNode(sec, textnode.TextType.NORMAL))
        
    return new_nodes

def text_to_textnodes(text):
    """returns a list of text nodes from the inline markdown"""
    new_nodes = []
    # make the raw string text into a text node
    node = textnode.TextNode(text, textnode.TextType.NORMAL)
    
    # Process inline formatting (bold, italic, code)
    new_nodes = split_nodes_delimiter([node], "**", textnode.TextType.BOLD)
    new_nodes = split_nodes_delimiter(new_nodes, "*", textnode.TextType.ITALIC)
    new_nodes = split_nodes_delimiter(new_nodes, "`", textnode.TextType.CODE)
    new_nodes = split_nodes_delimiter(new_nodes, "_", textnode.TextType.ITALIC)

    # finally take care of images and links text
    new_nodes = splite_node_images(new_nodes)
    new_nodes = splite_node_links(new_nodes)

    return new_nodes

def markdown_to_blocks(markdown):
    """Break down the string (full markdown Doc) into seperate blocks which are delimited by two \n\n (newlines)"""

    # strip any leading or trailing blank spaces
    new_markd = markdown.strip()

    # seperate the string based on two newlines which marks a block
    lst_blocks = re.split(r'\n[ \t]*\n', new_markd)
    # strip each block encase of newlines or spaces leading or trainling each block
    lst_blocks = list(map(lambda x: x.strip(), lst_blocks))
    # filter that only non-empty blocks are in the list of blocks
    lst_blocks = list(filter(lambda y: y != "", lst_blocks))

    return lst_blocks

def block_to_block_type(block_txt):
    """Takes a single block of markdown text as input and returns a string representing the type of block it is. Assume all leading and trailing whitespace was already stripped"""

    # Headings start with 1-6 # characters, followed by a space and then the heading text.
    if "# " in block_txt[0:2] or "## " in block_txt[0:3] or "### " in block_txt[0:4] or "#### " in block_txt[0:5] or "##### " in block_txt[0:6] or "###### " in block_txt[0:7]:
        return BlockType.HEADING
    # Code blocks must start with 3 backticks and end with 3 backticks.
    elif "```" in block_txt[0:3] and "```" in block_txt[-3:]:
        return BlockType.CODE
    # Every line in a quote block must start with a > character
    elif ">" in block_txt[0:1]:
        # check every newline item has >
        for line in block_txt.split("\n"):
            line = line.strip()
            if ">" not in line[0:1]:
                raise ValueError("You are missing a > in the front of each newline of text")
        return BlockType.QUOTE
    # Every line in an unordered list block must start with a * or - character, followed by a space.
    elif "* " in block_txt[0:2] or "- " in block_txt[0:2]:
        # check every newline item has * or - 
        for line in block_txt.split("\n"):
            line = line.strip()
            if "* " not in line[0:2] and "- " not in line[0:2]:
                raise ValueError("You are missing a * or - in the front of the unordered item (followed by a space)")
        return BlockType.UNORDERED
    # Every line in an ordered list block must start with a number followed by a . character and a space. The number must start at 1 and increment by 1 for each line.
    elif "1. " in block_txt[0:3]:
        count = 1
        # check every newline item has * or - 
        for line in block_txt.split("\n"):
            line = line.strip()
            if f"{count}. " not in line[0:3]:
                raise ValueError("You are missing a number , a dot(.) , or a space at the start of each ordered item")
            count += 1
        return BlockType.ORDERED
    # If none of the above conditions are met, the block is a normal paragraph.
    else: 
        return BlockType.PARAGRAPH

def block_to_simple_text(text, type):
    match type:
        case BlockType.HEADING:
            matches = re.findall(r'^\#{1,6} ', text)  # Finds # symbols for tag
            tag = f"h{len(matches[0]) - 1}"
            matches = re.findall(r'^\#{1,6} (.*?)$', text) # get the text
            heading_text = matches[0].strip() # strip the text of all spaces leading and ending
            return tag, heading_text # return the tag and the text
        case BlockType.QUOTE:
            tag = "blockquote"
            lst_newline_text = text.splitlines()
            matches = []
            for linetxt in lst_newline_text:
                linetxt = linetxt.strip()
                matches.extend(re.findall(r'^\>{0,1}[ \t]{0,4}(.*?)$', linetxt)) # get the text
            quote_text = "\n".join(matches) # join the list of strings into a single string with newlines
            return tag, quote_text # return the tag and the text
        case BlockType.CODE:
            tag = "code"
            matches = re.findall(r'\`{3}(.*?)\`{3}', text, re.DOTALL) # get the text
            return tag, matches[0].strip() # return the tag and the text
        case BlockType.UNORDERED:
            tag = "ul"
            matches = re.findall(r'[*-]\s{0,4}(.*)', text) # get the text
            for i, txt in enumerate(matches):
                matches[i] = txt.strip() # strip each unordered item of leading and ending spaces
            return tag, "\n".join(matches)
        case BlockType.ORDERED:
            tag = "ol"
            matches = re.findall(r'[\d+]\.\s{0,4}(.*)', text) # get the text
            for i, txt in enumerate(matches):
                matches[i] = txt.strip() # strip each ordered item of leading and ending spaces
            return tag, "\n".join(matches)


def block_to_html_parent_node(block, type):
    """Returns the child (parent node in) for the main parent node"""
    match type:
        case BlockType.PARAGRAPH:
            parent_tag = "p"
            children = []
            # get all different inline type text nodes
            lst_text_nodes = text_to_textnodes(block)
            # a paragraph parent node will only have inline markdown leafnodes
            for node in lst_text_nodes:
                children.append(text_node_to_html_node(node))
            # return the parent node with its children nodes
            return parentnode.ParentNode(parent_tag, children)
        
        case BlockType.HEADING:
            children = []
            parent_tag, block_text = block_to_simple_text(block, type)
            # get all different inline type text nodes
            lst_text_nodes = text_to_textnodes(block_text)
            # a paragraph parent node will only have inline markdown leafnodes
            for node in lst_text_nodes:
                children.append(text_node_to_html_node(node))
            # return the parent node with its children nodes
            return parentnode.ParentNode(parent_tag, children)

        case BlockType.QUOTE:
            children = []
            parent_tag, block_text = block_to_simple_text(block, type)
            # get all different inline type text nodes
            lst_text_nodes = text_to_textnodes(block_text)
            # a paragraph parent node will only have inline markdown leafnodes
            for node in lst_text_nodes:
                children.append(text_node_to_html_node(node))
            # return the parent node with its children nodes
            return parentnode.ParentNode(parent_tag, children)
        
        case BlockType.CODE:
            children = []
            parent_tag, block_text = block_to_simple_text(block, type)
            # get all different inline type text nodes
            lst_text_nodes = text_to_textnodes(block_text)
            # a paragraph parent node will only have inline markdown leafnodes
            for node in lst_text_nodes:
                children.append(text_node_to_html_node(node))
            # return the parent node with its children nodes
            return parentnode.ParentNode(parent_tag, children)
        
        case BlockType.UNORDERED:
            children = []
            parent_tag, block_text = block_to_simple_text(block, type)
            # for each unordered item get its inline children
            for item in block_text.splitlines():
                childrens_children = []
                # get all different inline type text nodes
                lst_text_nodes = text_to_textnodes(item)
                # a paragraph parent node will only have inline markdown leafnodes
                for node in lst_text_nodes:
                    childrens_children.append(text_node_to_html_node(node))
                children.append(parentnode.ParentNode("li", childrens_children))
            # return the parent node with its children nodes
            return parentnode.ParentNode(parent_tag, children)
        
        case BlockType.ORDERED:
            children = []
            parent_tag, block_text = block_to_simple_text(block, type)
            # for each unordered item get its inline children
            for item in block_text.splitlines():
                childrens_children = []
                # get all different inline type text nodes
                lst_text_nodes = text_to_textnodes(item)
                # a paragraph parent node will only have inline markdown leafnodes
                for node in lst_text_nodes:
                    childrens_children.append(text_node_to_html_node(node))
                children.append(parentnode.ParentNode("li", childrens_children))
            # return the parent node with its children nodes
            return parentnode.ParentNode(parent_tag, children)

def markdown_to_html_node(markdown):
    # break down the markdown doc string into independent blocks
    block_lst = markdown_to_blocks(markdown)

    main_parent_node_tag = "div"
    # create a list for the children of main parent node
    chidren_nodes = []

    # loop through the blocks
    for markdown_block in block_lst:
        # get the block type 
        markdown_type = block_to_block_type(markdown_block)
        # get child nodes of main parent
        chidren_nodes.append(block_to_html_parent_node(markdown_block, markdown_type))
    return parentnode.ParentNode(main_parent_node_tag, chidren_nodes)

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

def helper_fill_folder_with_html(source_lst, src_path, des_path, template_path):
    for item in source_lst:
        # if the item is a file then copy it to des folder
        if os.path.isfile(f"{src_path}/{item}"):
            if not (".html" in item.lower()):
                modified_item = re.sub(r"\.[a-zA-Z]{1,16}$", ".html", item)
            generate_page(f"{src_path}/{item}", template_path, f"{des_path}/{modified_item}")
        # else if it is a folder
        elif os.path.isdir(f"{src_path}/{item}"):
            # get its list of items
            new_src_lst = os.listdir(f"{src_path}/{item}")
            # create folder in the des folder
            os.mkdir(f"{des_path}/{item}")
            # recursively go through the subfolder items
            helper_fill_folder_with_html(new_src_lst, f"{src_path}/{item}", f"{des_path}/{item}", template_path)
    return

def extract_title(markdown):
    """Return the first H1 header title with no leading or trailing spaces"""
    # capture all h1 header titles
    titles = re.findall(r"# (.*)\s{0,4}", markdown)
    # use the first one if it exist, stripped of leading spaces or ending spaces
    if len(titles) >= 1:
        return titles[0].strip()
    else:
        raise Exception("No H1 header was found in the markdown")

def helper_build_des_path(des_path):
    # if the path exists then jsut return true
    if os.path.exists(des_path):
        return True
        
    # break up the path
    des_path_lst = des_path.split("/")
    build_path = ""
    # check that each component of the path exists
    for i,item in enumerate(des_path_lst):
        # if the item is a potential file with it exists or not
        if re.search(r".*\.[a-zA-Z]{1,16}", item):
            build_path += item
            # make sure a file item is the last item in the list or the path is broken by a file
            if i == (len(des_path_lst) - 1):
                return True
            else:
                return False
    
        # if the component is a single dot or double then ignore
        if item == "." or item == "" or item == "..":
            build_path += item + "/"
            continue
        elif not os.path.exists(build_path + item):
            os.mkdir(build_path + item)
        build_path += item + "/"
    return True

def generate_page(from_path, template_path, dest_path):
    """Creates a page"""
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    full_Md_text = None
    # retrieve the full .md file text from the path given
    with open(from_path, "r", encoding="utf-8") as fd:
        full_Md_text = fd.read() 

    template_text = None
    # retrieve the full template file text from the path given
    with open(template_path, "r", encoding="utf-8") as fd:
        template_text = fd.read()
    
    # get the html node of full MD text
    html_node = markdown_to_html_node(full_Md_text)
    # get the string of the html
    html_str = html_node.to_html()
    
    # get md title text
    title = extract_title(full_Md_text)

    # Replace the {{ Title }} and {{ Content }} placeholders in the template with title Md and html Md string
    template_text = template_text.replace("{{ Title }}", title, 1)
    template_text = template_text.replace("{{ Content }}", html_str, 1)

    if helper_build_des_path(dest_path):
        with open(dest_path, "w", encoding="utf-8") as fd:
            fd.write(template_text)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    # get initial list of items in the source folder
    init_lst = os.listdir(dir_path_content)
    # use helper recursive function
    helper_fill_folder_with_html(init_lst, dir_path_content, dest_dir_path, template_path)


# lst = markdown_to_blocks("""# Tolkien Fan Club

# ![JRR Tolkien sitting](/images/tolkien.png)

# Here's the deal, **I like Tolkien**.

# > "I am in fact a Hobbit in all but size."
# >
# > -- J.R.R. Tolkien

# ## Blog posts

# - [Why Glorfindel is More Impressive than Legolas](/blog/glorfindel)
# - [Why Tom Bombadil Was a Mistake](/blog/tom)
# - [The Unparalleled Majesty of "The Lord of the Rings"](/blog/majesty)

# ## Reasons I like Tolkien

# - You can spend years studying the legendarium and still not understand its depths
# - It can be enjoyed by children and adults alike
# - Disney _didn't ruin it_ (okay, but Amazon might have)
# - It created an entirely new genre of fantasy

# ## My favorite characters (in order)

# 1. Gandalf
# 2. Bilbo
# 3. Sam
# 4. Glorfindel
# 5. Galadriel
# 6. Elrond
# 7. Thorin
# 8. Sauron
# 9. Aragorn

# Here's what `elflang` looks like (the perfect coding language):

# ```
# func main(){
#     fmt.Println("Aiya, Ambar!")
# }
# ```

# Want to get in touch? [Contact me here](/contact).

# This site was generated with a custom-built [static site generator](https://www.boot.dev/courses/build-static-site-generator-python) from the course on [Boot.dev](https://www.boot.dev).
# """)

# for txt in lst:
#     print(txt)
#     print(block_to_block_type(txt))