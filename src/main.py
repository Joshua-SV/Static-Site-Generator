import textnode
import leafnode

def main():
    obj = textnode.TextNode("This is a text node", textnode.TextType.IMAGES, "https://www.boot.dev")

    def text_node_to_html_node(text_node):
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

    print(text_node_to_html_node(obj).to_html())


if __name__ == "__main__":
    main()