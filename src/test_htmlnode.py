import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        node = HTMLNode("a", "google.com", props={"href": "https://www.google.com","target": "_blank",})
        self.assertEqual(node.tag, "a")

    def test_neq(self):
        node = HTMLNode("a", "google.com", props={"href": "https://www.google.com","target": "_blank",})
        node2 = HTMLNode("a", "facebook.com", props={"href": "https://www.facebook.com","target": "_blank",})
        self.assertNotEqual(node, node2) 

    def test_propStr(self):
        node = HTMLNode("a", "google.com", props={"href": "https://www.google.com","target": "_blank",})
        self.assertEqual(node.props_to_html(), " href=\"https://www.google.com\" target=\"_blank\"")

    def test_nodeType(self):
        node = HTMLNode("a", "google.com", props={"href": "https://www.google.com","target": "_blank",})
        self.assertIsInstance(node, HTMLNode)

if __name__ == "__main__":
    unittest.main()
