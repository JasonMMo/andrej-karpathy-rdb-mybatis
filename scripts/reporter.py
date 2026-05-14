import datetime
import pathlib
from dataclasses import dataclass, field


@dataclass
class ReportInput:
    out_root: pathlib.Path
    blueprint_path: pathlib.Path
    ddl_dir: pathlib.Path
    project: str
    entity_count: int
    generated_files: list = field(default_factory=list)
    validation: dict = field(default_factory=dict)
    ddl_conversions: list = field(default_factory=list)
    endpoints: list = field(default_factory=list)
    exit_code: int = 0
    extra_messages: list = field(default_factory=list)


def write_report(inp: ReportInput) -> pathlib.Path:
    now = datetime.datetime.now().isoformat(timespec="seconds")
    lines = [
        "# Stage 3 — MyBatis/uiadapter Codegen Report",
        "",
        f"- Generated at: {now}",
        f"- Blueprint: {inp.blueprint_path} (project: {inp.project}, entities: {inp.entity_count})",
        f"- DDL source: {inp.ddl_dir}",
        f"- Output: {inp.out_root}",
        f"- Exit code: {inp.exit_code}",
        "",
        "## Validation",
    ]
    for k in ["R001", "R002", "R003", "R004", "R005", "R006"]:
        lines.append(f"- {k}: {inp.validation.get(k, 'N/A')}")
    lines += ["", "## Generated files"]
    for f in inp.generated_files:
        lines.append(f"- {f}")
    lines += ["", "## DDL conversion", "| Source | Target | Notes |", "|---|---|---|"]
    for src, tgt, note in inp.ddl_conversions:
        lines.append(f"| {src} | {tgt} | {note} |")
    lines += ["", "## Endpoints"]
    for ep in inp.endpoints:
        lines.append(f"- POST {ep}")
    if inp.extra_messages:
        lines += ["", "## Notes"]
        for m in inp.extra_messages:
            lines.append(f"- {m}")
    path = pathlib.Path(inp.out_root) / "mybatis-report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
