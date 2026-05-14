import pathlib
from reporter import write_report, ReportInput


def test_report_has_required_sections(tmp_path):
    inp = ReportInput(
        out_root=tmp_path,
        blueprint_path=pathlib.Path("wiki/_blueprint.yaml"),
        ddl_dir=pathlib.Path("db/migrations"),
        project="고객관리",
        entity_count=2,
        generated_files=[tmp_path / "x.java"],
        validation={"R001": "PASS", "R002": "PASS", "R003": "PASS", "R004": "PASS", "R005": "PASS", "R006": "SKIP"},
        ddl_conversions=[("V002__create_tables.sql", "schema.sql §1", "type map: NUMERIC→DECIMAL")],
        endpoints=["/customer/select_datalist_map.do", "/customer/save_datalist_map.do"],
        exit_code=0,
    )
    path = write_report(inp)
    text = path.read_text(encoding="utf-8")
    for section in ["# Stage 3", "Validation", "Generated files", "DDL conversion", "Endpoints", "Exit code: 0"]:
        assert section in text
