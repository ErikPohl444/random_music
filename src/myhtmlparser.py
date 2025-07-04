from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_anchor = False
        self.link_text = ""
        self.last_link_text = ""
        self.last_url = ""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.in_anchor = True
            self.link_text = ""
            for name, value in attrs:
                if name == "href":
                    self.current_link = value

    def handle_data(self, data):
        if self.in_anchor:
            self.link_text += data

    def handle_endtag(self, tag):
        if tag == "a" and self.in_anchor:
            self.last_url = self.current_link
            self.last_link_text = self.link_text.strip()
            self.in_anchor = False
            self.current_link = None
            self.link_text = ""
