import re

_camel_split = re.compile(r"(?<!^)(?=[A-Z])")


def to_snake(s: str) -> str:
    if "_" in s:
        return s.lower()
    return _camel_split.sub("_", s).lower()


def to_upper_snake(s: str) -> str:
    return to_snake(s).upper()


def to_pascal(s: str) -> str:
    parts = to_snake(s).split("_")
    return "".join(p.capitalize() for p in parts if p)


def to_camel(s: str) -> str:
    p = to_pascal(s)
    return p[0].lower() + p[1:] if p else p
