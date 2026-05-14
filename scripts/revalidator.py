import pathlib
import re
import shutil
import subprocess
import os
from dataclasses import dataclass


JAVAC_TIMEOUT_SECONDS = 120


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


@dataclass
class JavacResult:
    ok: bool = True
    skipped: bool = False
    message: str = ""
    stderr: str = ""


def javac_check(out_root: pathlib.Path) -> JavacResult:
    libs_env = os.environ.get("NEXACRO_LIBS_DIR")
    if not libs_env:
        return JavacResult(ok=True, skipped=True,
                           message="NEXACRO_LIBS_DIR not set; R006 javac check skipped")
    libs_dir = pathlib.Path(libs_env)
    if not libs_dir.exists():
        return JavacResult(ok=True, skipped=True,
                           message=f"NEXACRO_LIBS_DIR does not exist: {libs_dir}")
    java_files = list(_java_root(out_root).rglob("*.java"))
    if not java_files:
        return JavacResult(ok=True, skipped=True, message="no .java files to compile")
    jars = list(libs_dir.glob("*.jar"))
    cp_sep = ";" if os.name == "nt" else ":"
    cp = cp_sep.join(str(j) for j in jars) if jars else ""
    build_dir = pathlib.Path(out_root) / ".build_check"
    build_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["javac", "-d", str(build_dir)]
    if cp:
        cmd += ["-cp", cp]
    cmd += [str(f) for f in java_files]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=JAVAC_TIMEOUT_SECONDS)
        result = JavacResult(
            ok=(proc.returncode == 0), skipped=False,
            message=("javac ok" if proc.returncode == 0 else "javac failed"),
            stderr=proc.stderr,
        )
    except subprocess.TimeoutExpired as e:
        result = JavacResult(ok=False, skipped=False,
                             message="javac timeout",
                             stderr=f"javac exceeded {JAVAC_TIMEOUT_SECONDS}s: {e}")
    finally:
        shutil.rmtree(build_dir, ignore_errors=True)
    return result
