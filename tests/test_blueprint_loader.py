import pathlib
import pytest
from blueprint_loader import load, BlueprintError

GOLDEN = pathlib.Path(__file__).parent / "fixtures" / "golden_blueprint" / "_blueprint.yaml"


def test_golden_loads():
    bp = load(GOLDEN)
    assert bp["project"] == "고객관리"
    assert len(bp["entities"]) == 2


def test_rejects_wrong_version(tmp_path):
    p = tmp_path / "bp.yaml"
    p.write_text("version: 2\nproject: x\nentities: []\nrelations: []\nbusiness_rules: []\nvalidation: {passed: true}\n", encoding="utf-8")
    with pytest.raises(BlueprintError, match="version"):
        load(p)


def test_rejects_validation_failed(tmp_path):
    p = tmp_path / "bp.yaml"
    p.write_text("version: 1\nproject: x\nentities: []\nrelations: []\nbusiness_rules: []\nvalidation: {passed: false}\n", encoding="utf-8")
    with pytest.raises(BlueprintError, match="validation.passed"):
        load(p)


def test_rejects_missing_file(tmp_path):
    with pytest.raises(BlueprintError, match="not found"):
        load(tmp_path / "missing.yaml")
