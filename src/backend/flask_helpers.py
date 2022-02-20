from flask import Flask, url_for

class FlaskHelper():
    def __init__(self, app: Flask, port: int):
        """Create this object after creating all flask routes"""
        self.app = app
        self.port = port

    def has_no_empty_params(self, rule):
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)

    def get_links(self) -> list:
        """Returns list of GET endpoints"""
        links = []
        for rule in self.app.url_map.iter_rules():
            url = f"http://localhost:{self.port}{rule}"
            links.append(url)
        return links

    def gen_site_map(self):
        @self.app.route("/site-map")
        def site_map() -> list:
            return self.get_links()

    def print_routes(self):
        """Print all Flask app routes"""
        print("Existing URLs:")
        print("\n".join(self.get_links()))