import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_neq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.NORMAL)
        self.assertNotEqual(node, node2) 

    def test_url(self):
        node = TextNode("This is a text node", TextType.BOLD, "boot.dev")
        self.assertEqual(node.url, "boot.dev")
    
    def test_enum(self):
        node = TextNode("This is a text node", TextType.CODE, "boot.dev")
        self.assertIsInstance(node.text_type, TextType)

if __name__ == "__main__":
    unittest.main()

