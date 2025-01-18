import textnode

def main():
    obj = textnode.TextNode("This is a text node", textnode.TextType.BOLD, "https://www.boot.dev")

    print(obj)


if __name__ == "__main__":
    main()