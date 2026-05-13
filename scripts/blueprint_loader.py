import pathlib
import yaml


class BlueprintError(Exception):
    pass


def load(path: pathlib.Path) -> dict:
    path = pathlib.Path(path)
    if not path.exists():
        raise BlueprintError(f"blueprint not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("version") != 1:
        raise BlueprintError(f"unsupported blueprint version: {data.get('version')} (expected 1)")
    validation = data.get("validation") or {}
    if validation.get("passed") is not True:
        raise BlueprintError("blueprint validation.passed is not true — re-run Stage 1 /karpathy-rdb compile")
    return data
