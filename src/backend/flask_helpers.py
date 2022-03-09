from flask import Flask, url_for, flash
from werkzeug.routing import Rule
from typing import List

class FlaskHelper():
    def __init__(self, app: Flask, port: int):
        """Create this object after creating all flask routes"""
        self.app = app
        self.port = port

    @classmethod
    def flash_print(cls, msg: str, style: str=None):
        print(msg)
        flash(msg, style if style != None else "")

    def has_no_empty_params(self, rule: Rule):
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)

    def is_get_req(self, method: str):
        return method == "GET"
    def is_post_req(self, method: str):
        return method == "POST"
    def is_get_post_req(self, method: str):
        return self.is_get_req(method) or self.is_post_req(method)

    def is_rule_basic_dup(self, rule: Rule, rules: List[Rule]) -> bool:
        """Checks if multiple versions of route & this is basic one (ie has no args/params)"""
        sim_rules = list(filter(lambda x: x.rule.startswith(rule.rule), rules))
        sim_rules.sort(key=lambda x: len(x.arguments)) # get rule with most # args at end
        if len(sim_rules) > 1: # must always be at least 1 match (itself)
            # if best rule doesnt match passed one, means this is a dup
            return sim_rules[0] != rule
        else:
            # otherwise, assume not a dup so it'll be stored even if redundant
            return False


    def get_links(self, include_domain:bool=True, include_methods:bool=True, rm_dups:bool=True) -> list:
        """Returns list of all endpoints"""
        links = []
        pre_rule=f"http://localhost:{self.port}" if include_domain else ""
        for rule in self.app.url_map.iter_rules():
            if rm_dups and self.is_rule_basic_dup(rule, self.app.url_map.iter_rules()):
                continue

            methods = list(filter(self.is_get_post_req, rule.methods)) if include_methods else ""
            url = f"{pre_rule}{rule}"
            url_method = f"{url} {methods}"
            links.append(url_method)

        # sort (so common routes stay tg) and finish
        links.sort()
        return links

    def gen_site_map(self):
        @self.app.route("/site-map")
        def site_map() -> list:
            return self.get_links()

    def print_routes(self):
        """Print all Flask app routes"""
        print("Existing URLs:")
        print("\n".join(self.get_links()))


# exports
flash_print = FlaskHelper.flash_print
