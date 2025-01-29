

class HTMLNode:

    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props # dictionary of html attributes
    
    def to_html():
        raise NotImplementedError()
    
    def props_to_html(self):
        propStr = ""
        for key in self.props:
            propStr += f" {key}={self.props[key]}"
        return propStr
    
    def __repr__(self):
        return f"-------------------------\nself.tag = {self.tag}\nself.value = {self.value}\nself.children = {self.children}\nself.props = {self.props}\n-------------------------"
