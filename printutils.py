
def apply_indent(txt: str) -> str:
    indent = "  "
    return "\n".join(map((lambda x: indent + x), txt.splitlines()))