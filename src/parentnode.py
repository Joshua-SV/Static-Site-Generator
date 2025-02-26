from htmlnode import HTMLNode
from leafnode import LeafNode

class ParentNode(HTMLNode):

    def __init__(self, tag, children, props=None):
        super().__init__(tag, value=None, children=children, props=props)
    
    def to_html(self):
        if not isinstance(self.tag, str):
            raise ValueError(f"All parent nodes must have a tag. Current tag: {self.tag}")
        if not isinstance(self.children, list):
            raise ValueError(f"All parent nodes must have children. Current Children: {self.children}")
        
        children_html = "".join(child.to_html() for child in self.children) # recursively call to_html for each child
        if isinstance(self.props, dict):
            return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"
        return f"<{self.tag}>{children_html}</{self.tag}>"
