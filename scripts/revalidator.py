import pathlib
import re
import subprocess
import os


class RevalidationError(Exception):
    pass


_NAMESPACE = re.compile(r'<mapper\s+namespace\s*=\s*"([^"]+)"')
_ID = re.compile(r'<(?:select|insert|update|delete)\s+id\s*=\s*"([^"]+)"')
_IFACE_METHOD = re.compile(r'(?:public\s+)?(?:\w[\w<>,\s\[\]\.]*?)\s+(\w+)\s*\(')


def _java_root(out_root: pathlib.Path) -> pathlib.Path:
    return pathlib.Path(out_root) / "src" / "main" / "java"


def _xml_root(out_root: pathlib.Path) -> pathlib.Path:
    return pathlib.Path(out_root) / "src" / "main" / "resources" / "mybatis" / "mapper"


def _read_methods_from_iface(iface_path: pathlib.Path) -> list:
    txt = iface_path.read_text(encoding="utf-8")
    body = txt[txt.index("{") + 1 : txt.rindex("}")]
    return [m.group(1) for m in _IFACE_METHOD.finditer(body)]


def lint_mapper_xmls(out_root: pathlib.Path) -> None:
    java_root = _java_root(out_root)
    xml_root = _xml_root(out_root)
    if not xml_root.exists():
        raise RevalidationError(f"mapper xml dir missing: {xml_root}")
    for xml in xml_root.glob("*Mapper.xml"):
        text = xml.read_text(encoding="utf-8")
        m = _NAMESPACE.search(text)
        if not m:
            raise RevalidationError(f"{xml.name}: namespace not found")
        ns = m.group(1)
        expected_iface = java_root / pathlib.Path(*ns.split("."))
        expected_iface = expected_iface.with_suffix(".java")
        if not expected_iface.exists():
            raise RevalidationError(f"{xml.name}: namespace {ns} has no matching interface at {expected_iface}")
        ids = set(_ID.findall(text))
        methods = set(_read_methods_from_iface(expected_iface))
        missing_in_iface = ids - methods
        if missing_in_iface:
            raise RevalidationError(f"{xml.name}: id(s) not in interface: {sorted(missing_in_iface)}")
        missing_in_xml = methods - ids
        if missing_in_xml:
            raise RevalidationError(f"{xml.name}: method(s) not in xml: {sorted(missing_in_xml)}")
