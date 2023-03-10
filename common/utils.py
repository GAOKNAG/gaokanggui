import json


def format_json(content):
    if isinstance(content, (str, bytes)):
        try:
            content = json.load(content)
        except Exception as e:
            return content
        result = json.dumps(content, sort_keys=True, indent=4, separators=(',', ": ")).encode("latin-1").decode("unicode_escape")
