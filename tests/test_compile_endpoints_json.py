import json
import os
import pathlib
import subprocess
import sys
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE_BP = ROOT / "tests" / "fixtures" / "golden_blueprint"
FIXTURE_DDL = ROOT / "tests" / "fixtures" / "golden_ddl"


def _run_compile(tmp_path, *extra_args):
    """Copy fixtures into a project dir and run compile.py via subprocess."""
    proj = tmp_path / "proj"
    wiki = proj / "wiki"
    wiki.mkdir(parents=True)
    shutil.copy(FIXTURE_BP / "_blueprint.yaml", wiki / "_blueprint.yaml")
    db = proj / "db" / "migrations"
    db.mkdir(parents=True)
    for f in FIXTURE_DDL.glob("V0*.sql"):
        shutil.copy(f, db / f.name)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "scripts")

    cmd = [
        sys.executable, str(ROOT / "scripts" / "compile.py"), "compile",
        "--skip-compile",
        *extra_args,
    ]
    return subprocess.run(cmd, cwd=proj, capture_output=True, text=True, env=env), proj


def test_compile_emits_endpoints_json(tmp_path):
    r, proj = _run_compile(tmp_path)
    assert r.returncode == 0, r.stderr
    ep = proj / "backend" / "endpoints.json"
    assert ep.exists(), f"endpoints.json not found at {ep}"
    data = json.loads(ep.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert len(data["entities"]) >= 1
    methods = [m["method"] for m in data["entities"][0]["endpoints"]]
    assert "select_datalist_map" in methods and "save_datalist_map" in methods


def test_compile_dry_run_emits_endpoints_json(tmp_path):
    r, proj = _run_compile(tmp_path, "--dry-run")
    assert r.returncode == 0, r.stderr
    ep = proj / "backend" / "endpoints.json"
    assert ep.exists(), f"endpoints.json not found at {ep} (dry-run)"
    data = json.loads(ep.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert len(data["entities"]) >= 1
    methods = [m["method"] for m in data["entities"][0]["endpoints"]]
    assert "select_datalist_map" in methods and "save_datalist_map" in methods
