import pathlib
import pytest
from revalidator import lint_mapper_xmls, RevalidationError


def _seed_pair(base: pathlib.Path, namespace: str, ids: list, methods: list):
    java = base / "src/main/java/com/nexacro/uiadapter/mapper"
    java.mkdir(parents=True, exist_ok=True)
    iface = "package com.nexacro.uiadapter.mapper;\n\npublic interface CustomerMapper {\n"
    for m in methods:
        iface += f"    void {m}();\n"
    iface += "}\n"
    (java / "CustomerMapper.java").write_text(iface, encoding="utf-8")

    xml_root = base / "src/main/resources/mybatis/mapper"
    xml_root.mkdir(parents=True, exist_ok=True)
    xml = f'<?xml version="1.0"?>\n<mapper namespace="{namespace}">\n'
    for i in ids:
        xml += f'  <select id="{i}"></select>\n'
    xml += "</mapper>\n"
    (xml_root / "CustomerMapper.xml").write_text(xml, encoding="utf-8")


def test_lint_passes_when_aligned(tmp_path):
    _seed_pair(tmp_path,
               namespace="com.nexacro.uiadapter.mapper.CustomerMapper",
               ids=["select_customer_datalist_map", "insert_customer_map"],
               methods=["select_customer_datalist_map", "insert_customer_map"])
    lint_mapper_xmls(tmp_path)  # no raise


def test_lint_fails_on_namespace_mismatch(tmp_path):
    _seed_pair(tmp_path,
               namespace="wrong.ns.CustomerMapper",
               ids=["x"], methods=["x"])
    with pytest.raises(RevalidationError, match="namespace"):
        lint_mapper_xmls(tmp_path)


def test_lint_fails_on_id_method_mismatch(tmp_path):
    _seed_pair(tmp_path,
               namespace="com.nexacro.uiadapter.mapper.CustomerMapper",
               ids=["select_customer_datalist_map"], methods=["insert_customer_map"])
    with pytest.raises(RevalidationError, match="id"):
        lint_mapper_xmls(tmp_path)


def test_javac_skip_when_libs_dir_missing(tmp_path, monkeypatch):
    from revalidator import javac_check, JavacResult
    monkeypatch.delenv("NEXACRO_LIBS_DIR", raising=False)
    result = javac_check(tmp_path)
    assert isinstance(result, JavacResult)
    assert result.skipped is True
    assert "NEXACRO_LIBS_DIR" in result.message


def test_javac_skip_when_no_java_files(tmp_path, monkeypatch):
    from revalidator import javac_check
    monkeypatch.setenv("NEXACRO_LIBS_DIR", str(tmp_path))
    result = javac_check(tmp_path)
    assert result.skipped is True
