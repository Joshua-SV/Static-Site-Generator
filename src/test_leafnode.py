import unittest

from leafnode import LeafNode

class TestLeafNode(unittest.TestCase):
    def test_eq(self):
        node = LeafNode("a", "google.com", props={"href": "https://www.google.com","target": "_blank",})
        self.assertEqual(node.tag, "a")

    def test_neq(self):
        node = LeafNode("a", "google.com", props={"href": "https://www.google.com","target": "_blank",})
        node2 = LeafNode("a", "facebook.com", props={"href": "https://www.facebook.com","target": "_blank",})
        self.assertNotEqual(node, node2) 

    def test_propStr(self):
        node = LeafNode("a", "google.com", props={"href": "https://www.google.com","target": "_blank",})
        self.assertEqual(node.props_to_html(), " href=\"https://www.google.com\" target=\"_blank\"")

    def test_nodeType(self):
        node = LeafNode("a", "google.com", props={"href": "https://www.google.com","target": "_blank",})
        self.assertIsInstance(node, LeafNode)
    
    def test_to_html(self):
        node = LeafNode("a", "google.com", props={"href": "https://www.google.com","target": "_blank",})
        self.assertEqual(node.to_html(), "<a href=\"https://www.google.com\" target=\"_blank\">google.com</a>")

if __name__ == "__main__":
    unittest.main()
