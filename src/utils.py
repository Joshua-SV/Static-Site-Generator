import textnode
import leafnode
import re

def text_node_to_html_node(text_node):
        """
        creates a leafnode from a textnode by type
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
        
        # If there's an odd number of parts, there's an unmatched delimiter
        if len(text_parts) % 2 == 0:
            raise ValueError(f"Unmatched delimiter '{delimiter}' in text: {node.text}")

        for i, part in enumerate(text_parts):
            if part == "":
                continue  # Skip empty segments caused by consecutive delimiters
            if i % 2 == 0:
                new_nodes.append(textnode.TextNode(part, textnode.TextType.NORMAL))  # Normal text
            else:
                new_nodes.append(textnode.TextNode(part, text_type))  # Delimited text

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

        # 
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

