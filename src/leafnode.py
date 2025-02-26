from htmlnode import HTMLNode

class LeafNode(HTMLNode):

    def __init__(self, tag, value, props=None):

        super().__init__(tag, value, props=props)
    
    def to_html(self):
        if self.value is None:
            raise ValueError("All leaf nodes must have a value.")
        if self.tag is None:
            return f"{self.value}"
        elif self.tag == "img":
            return f"<{self.tag}{self.props_to_html()}>" 
        elif self.tag != None and isinstance(self.props, dict):
            return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
        
        return f"<{self.tag}>{self.value}</{self.tag}>"
