"""v0.5 H3 — lane suffix v2 generalization regression.

suffix v2 mapping:
  nexacro → ""        (legacy: no suffix on template filenames)
  vanilla → ".vanilla"
  jakarta → ".jakarta"
  javax   → ".javax"
"""
import pathlib
from codegen import render_entity_files


ENTITY = {
    "name": "user",
    "table": "TB_USER",
    "columns": [
        {"name": "user_id", "type": "varchar(36)", "pk": True},
        {"name": "name",    "type": "varchar(100)"},
    ],
}


def _render(tmp_path, lane):
    return render_entity_files(tmp_path / lane, ENTITY, base_package="com.x.app", lane=lane)


def test_suffix_nexacro_emits_six_files(tmp_path):
    paths = _render(tmp_path, "nexacro")
    assert len(paths) == 6


def test_suffix_vanilla_emits_six_files(tmp_path):
    paths = _render(tmp_path, "vanilla")
    assert len(paths) == 6


def test_suffix_jakarta_emits_six_files(tmp_path):
    paths = _render(tmp_path, "jakarta")
    assert len(paths) == 6


def test_suffix_javax_emits_six_files(tmp_path):
    paths = _render(tmp_path, "javax")
    assert len(paths) == 6
