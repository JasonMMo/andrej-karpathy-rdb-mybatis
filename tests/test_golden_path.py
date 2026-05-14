import pathlib
import shutil
import subprocess
import sys
import os

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE_BP = PLUGIN_ROOT / "tests" / "fixtures" / "golden_blueprint"
FIXTURE_DDL = PLUGIN_ROOT / "tests" / "fixtures" / "golden_ddl"
EXPECTED = PLUGIN_ROOT / "tests" / "fixtures" / "expected_output"


def _run(tmp_path):
    proj = tmp_path / "proj"
    (proj / "wiki").mkdir(parents=True)
    shutil.copy(FIXTURE_BP / "_blueprint.yaml", proj / "wiki" / "_blueprint.yaml")
    (proj / "db" / "migrations").mkdir(parents=True)
    for f in FIXTURE_DDL.glob("V0*.sql"):
        shutil.copy(f, proj / "db" / "migrations" / f.name)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PLUGIN_ROOT / "scripts")
    cp = subprocess.run(
        [sys.executable, str(PLUGIN_ROOT / "scripts" / "compile.py"),
         "compile", "--skip-compile"],
        cwd=proj, capture_output=True, text=True, env=env,
    )
    assert cp.returncode == 0, cp.stderr
    return proj / "backend"


def _normalize(s: str) -> str:
    return "\n".join(line.rstrip() for line in s.splitlines() if line.strip()) + "\n"


def test_golden_files_match_snapshot(tmp_path):
    out = _run(tmp_path)
    if not EXPECTED.exists():
        # bootstrap: copy and fail with a hint, run once to lock
        EXPECTED.mkdir(parents=True)
        for f in out.rglob("*"):
            if f.is_file() and f.name != "mybatis-report.md":
                rel = f.relative_to(out)
                dest = EXPECTED / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(f, dest)
        raise AssertionError("expected_output bootstrapped - review and commit, then re-run")

    diffs = []
    for f in EXPECTED.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(EXPECTED)
        actual = out / rel
        if not actual.exists():
            diffs.append(f"missing: {rel}")
            continue
        if _normalize(actual.read_text(encoding="utf-8")) != _normalize(f.read_text(encoding="utf-8")):
            diffs.append(f"mismatch: {rel}")
    assert not diffs, "snapshot drift:\n" + "\n".join(diffs)
