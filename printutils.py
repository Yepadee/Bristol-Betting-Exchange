
class Printable(object):
    def to_string(self, level: int) -> str:
        pass

    def apply_indent(self, txt: str, level: int) -> str:
        indent = "  " * level
        return "\n".join(map((lambda x: indent + x), txt.splitlines()))

    def __str__(self) -> str:
        return self.to_string(0)