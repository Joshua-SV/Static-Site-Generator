import textnode
import leafnode
import re

import utils

def main():
    obj = textnode.TextNode("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg) ![](fsaffasf.com)", textnode.TextType.NORMAL)

    

    #print(split_nodes_delimiter([obj],"`",textnode.TextType.CODE))
    print(utils.splite_node_images([obj]))


if __name__ == "__main__":
    main()