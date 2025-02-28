import textnode
import leafnode
import parentnode
import re
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
            matches = re.findall(r'^\`{3}(.*?)\`{3}$', text) # get the text
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