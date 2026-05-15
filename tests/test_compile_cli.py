import os
import pathlib
import subprocess
import sys
import shutil


PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE_BP = PLUGIN_ROOT / "tests" / "fixtures" / "golden_blueprint"
FIXTURE_DDL = PLUGIN_ROOT / "tests" / "fixtures" / "golden_ddl"


def _project_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    shutil.copy(FIXTURE_BP / "_blueprint.yaml", wiki / "_blueprint.yaml")
    db = tmp_path / "db" / "migrations"
    db.mkdir(parents=True)
    for f in FIXTURE_DDL.glob("V0*.sql"):
        shutil.copy(f, db / f.name)
    return tmp_path


def _run_compile(cwd: pathlib.Path, *args, env_extra=None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PLUGIN_ROOT / "scripts")
    if env_extra:
        env.update(env_extra)
    cmd = [sys.executable, str(PLUGIN_ROOT / "scripts" / "compile.py"), *args]
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)


def test_compile_success_skip_javac(tmp_path):
    proj = _project_dir(tmp_path)
    cp = _run_compile(proj, "compile", "--skip-compile")
    assert cp.returncode == 0, cp.stderr
    out = proj / "backend"
    assert (out / "src/main/java/com/nexacro/uiadapter/controller/CustomerController.java").exists()
    assert (out / "src/main/resources/schema.sql").exists()
    assert (out / "mybatis-report.md").exists()


def test_compile_exits_1_on_bad_blueprint(tmp_path):
    proj = _project_dir(tmp_path)
    (proj / "wiki" / "_blueprint.yaml").write_text(
        "version: 1\nproject: x\nentities: []\nrelations: []\nbusiness_rules: []\nvalidation: {passed: false}\n",
        encoding="utf-8",
    )
    cp = _run_compile(proj, "compile", "--skip-compile")
    assert cp.returncode == 1
    assert "validation.passed" in (cp.stdout + cp.stderr)


def test_compile_exits_1_and_reports_r001_fail_when_blueprint_missing(tmp_path):
    proj = _project_dir(tmp_path)
    (proj / "wiki" / "_blueprint.yaml").unlink()
    cp = _run_compile(proj, "compile", "--skip-compile")
    assert cp.returncode == 1
    report = (proj / "backend" / "mybatis-report.md").read_text(encoding="utf-8")
    assert "R001: FAIL" in report
    assert "R002: N/A" in report


def test_compile_strict_prefix_fails_on_violation(tmp_path):
    proj = _project_dir(tmp_path)
    # default prefix is TB_; force a violation by changing --table-prefix
    cp = _run_compile(proj, "compile", "--skip-compile", "--strict-prefix",
                      "--table-prefix", "ZZ_")
    assert cp.returncode == 1
    assert "table-prefix" in (cp.stdout + cp.stderr)


def test_compile_warns_on_prefix_violation_without_strict(tmp_path):
    proj = _project_dir(tmp_path)
    cp = _run_compile(proj, "compile", "--skip-compile",
                      "--table-prefix", "ZZ_")
    assert cp.returncode == 0, cp.stderr
    report = (proj / "backend" / "mybatis-report.md").read_text(encoding="utf-8")
    assert "warning" in report and "table-prefix" in report


def test_compile_dry_run_writes_no_code(tmp_path):
    proj = _project_dir(tmp_path)
    cp = _run_compile(proj, "compile", "--dry-run")
    assert cp.returncode == 0
    out = proj / "backend"
    assert (out / "mybatis-report.md").exists()
    assert not (out / "src/main/java/com/nexacro/uiadapter/controller/CustomerController.java").exists()


import json


def test_compile_dry_run_vanilla_lane(tmp_path):
    proj = _project_dir(tmp_path)
    cp = _run_compile(proj, "compile", "--dry-run", "--lane", "vanilla", "--package", "com.example.app")
    assert cp.returncode == 0, cp.stderr
    payload = json.loads((proj / "backend" / "endpoints.json").read_text(encoding="utf-8"))
    assert payload["version"] == 2
    assert payload["lane"] == "vanilla"
    assert payload["entities"][0]["endpoint_base"].startswith("/api/")


def test_compile_dry_run_default_lane_is_nexacro(tmp_path):
    proj = _project_dir(tmp_path)
    cp = _run_compile(proj, "compile", "--dry-run")
    assert cp.returncode == 0, cp.stderr
    payload = json.loads((proj / "backend" / "endpoints.json").read_text(encoding="utf-8"))
    assert payload["version"] == 1
    assert "lane" not in payload
