from enum import Enum

class TextType(Enum):
	NORMAL = "normal"
	BOLD = "bold"
	ITALIC = "italic"
	CODE = "code"
	LINKS = "links"
	IMAGES = "images"


class TextNode:

	def __init__(self, text, text_type, url=None):
		self.text = text
		self.text_type = text_type
		self.url = url
	
	def __eq__(self, other):
		if self.text == other.text and self.text_type.value == other.text_type.value and self.url == other.url:
			return True
		return False
	
	# toString method of the object
	def __repr__(self):
		return f"TextNode({self.text}, {self.text_type.value}, {self.url})"
	

	
		