import re
import unicodedata


def normalize_column_name(name: str) -> str:
    """Normalize a Google Sheet column header to a variable name."""
    name = name.lower().strip()
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"[/\s]+", "_", name)
    name = re.sub(r"[^a-z0-9_]", "", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def render_template(template: str, data: dict) -> str:
    """Replace {{variable}} placeholders with values from data.
    Unmatched variables are left as-is.
    """
    def replace_match(match):
        key = match.group(1).strip()
        if key in data:
            return str(data[key])
        return match.group(0)

    return re.sub(r"\{\{(\s*\w+\s*)\}\}", replace_match, template)
