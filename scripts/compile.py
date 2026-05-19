import argparse
import pathlib
import sys

from blueprint_loader import load as load_blueprint, BlueprintError
from ddl_loader import load as load_ddl, DDLBundleError
from column_classifier import validate_pk_coverage, ColumnClassifierError
from toposort import topo_sort
from postgres_to_hsqldb import convert_bundle, convert_seed_files
from codegen import render_entity_files, render_schema_sql, render_data_sql
from revalidator import lint_mapper_xmls, javac_check, RevalidationError
from reporter import write_report, ReportInput
from endpoints_emitter import build_endpoints_payload, write_endpoints_json


def _parse_args(argv):
    p = argparse.ArgumentParser(prog="karpathy-rdb-mybatis")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compile")
    c.add_argument("--blueprint", default="wiki/_blueprint.yaml")
    c.add_argument("--ddl-dir",   default="db/migrations")
    c.add_argument("--seed-dir",  default="db/seed")
    c.add_argument("--out",       default="backend")
    c.add_argument("--lane",      choices=["nexacro", "vanilla", "jakarta", "javax"], default="nexacro")
    c.add_argument("--package",   default=None)
    c.add_argument("--table-prefix", default="TB_")
    c.add_argument("--strict-prefix", action="store_true",
                   help="fail (exit 1) when any entity's table does not start with --table-prefix")
    c.add_argument("--skip-compile", action="store_true")
    c.add_argument("--dry-run",   action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "compile" and args.package is None:
        args.package = (
            "com.nexacro.uiadapter" if args.lane == "nexacro" else "com.example.app"
        )
    return args


def _check_table_prefix(entities, prefix):
    bad = [e["name"] for e in entities if not e.get("table", "").startswith(prefix)]
    return bad


def main(argv=None):
    args = _parse_args(argv or sys.argv[1:])
    if args.cmd != "compile":
        print(f"unknown command: {args.cmd}", file=sys.stderr)
        return 1

    validation = {}
    extra = []
    try:
        bp = load_blueprint(args.blueprint)
        validation["R001"] = "PASS"
        validation["R002"] = "PASS"
    except BlueprintError as e:
        msg = str(e)
        if "validation.passed" in msg:
            validation["R001"] = "PASS"
            validation["R002"] = "FAIL"
        else:
            validation["R001"] = "FAIL"
            validation["R002"] = "N/A"
        print(f"[R001/R002] {msg}", file=sys.stderr)
        _emit_partial_report(args, validation, exit_code=1, extra=[msg])
        return 1

    try:
        seed_dir = pathlib.Path(args.seed_dir)
        ddl = load_ddl(args.ddl_dir, seed_dir=seed_dir if seed_dir.exists() else None)
        validation["R003"] = "PASS"
    except DDLBundleError as e:
        validation["R003"] = "FAIL"
        print(f"[R003] {e}", file=sys.stderr)
        _emit_partial_report(args, validation, exit_code=1, extra=[str(e)])
        return 1

    try:
        validate_pk_coverage(bp["entities"])
        validation["R004"] = "PASS"
    except ColumnClassifierError as e:
        validation["R004"] = "FAIL"
        print(f"[R004] {e}", file=sys.stderr)
        _emit_partial_report(args, validation, exit_code=1, extra=[str(e)])
        return 1

    prefix_violations = _check_table_prefix(bp["entities"], args.table_prefix)
    if prefix_violations:
        msg = f"table-prefix: {prefix_violations} do not start with {args.table_prefix}"
        if args.strict_prefix:
            print(f"[table-prefix] {msg}", file=sys.stderr)
            _emit_partial_report(args, validation, exit_code=1, extra=[msg])
            return 1
        extra.append(f"warning: {msg}")

    sorted_entities = topo_sort(bp["entities"], bp.get("relations") or [])

    out_root = pathlib.Path(args.out)
    generated = []
    endpoints = []

    if args.dry_run:
        validation.setdefault("R005", "SKIP")
        validation.setdefault("R006", "SKIP")
        context_path = "/uiadapter" if args.lane == "nexacro" else "/api"
        if args.lane == "nexacro":
            for e in sorted_entities:
                endpoints.append(f"/{e['name']}/select_datalist_map.do")
                endpoints.append(f"/{e['name']}/save_datalist_map.do")
        else:
            for e in sorted_entities:
                endpoints.append(f"/api/{e['name']}")
        endpoints_payload = build_endpoints_payload(sorted_entities, context_path=context_path, lane=args.lane)
        write_endpoints_json(out_root, endpoints_payload)
        generated.append(str(out_root / "endpoints.json"))
        _emit_full_report(args, validation, generated, endpoints, exit_code=0, extra=extra + ["dry-run mode"])
        return 0

    converted_sql = convert_bundle(ddl)
    generated.append(render_schema_sql(out_root, converted_sql))
    if ddl.seed_files:
        converted_seed = convert_seed_files(ddl.seed_files)
        generated.append(render_data_sql(out_root, converted_seed))

    for e in sorted_entities:
        generated.extend(render_entity_files(out_root, e, base_package=args.package, lane=args.lane))
        if args.lane == "nexacro":
            endpoints.append(f"/{e['name']}/select_datalist_map.do")
            endpoints.append(f"/{e['name']}/save_datalist_map.do")
        else:
            endpoints.append(f"/api/{e['name']}")

    exit_code = 0
    try:
        lint_mapper_xmls(out_root)
        validation["R005"] = "PASS"
    except RevalidationError as e:
        validation["R005"] = "FAIL"
        extra.append(f"R005: {e}")
        exit_code = 2

    if args.skip_compile:
        validation["R006"] = "SKIP"
    else:
        jr = javac_check(out_root)
        if jr.skipped:
            validation["R006"] = "SKIP"
            extra.append(jr.message)
        elif jr.ok:
            validation["R006"] = "PASS"
        else:
            validation["R006"] = "FAIL"
            extra.append("javac stderr:\n" + jr.stderr)
            exit_code = max(exit_code, 2)

    context_path = "/uiadapter" if args.lane == "nexacro" else "/api"
    endpoints_payload = build_endpoints_payload(sorted_entities, context_path=context_path, lane=args.lane)
    write_endpoints_json(out_root, endpoints_payload)
    generated.append(str(out_root / "endpoints.json"))
    _emit_full_report(args, validation, generated, endpoints, exit_code=exit_code, extra=extra,
                      project=bp.get("project", ""), entity_count=len(sorted_entities))
    return exit_code


def _emit_partial_report(args, validation, exit_code, extra):
    write_report(ReportInput(
        out_root=pathlib.Path(args.out),
        blueprint_path=pathlib.Path(args.blueprint),
        ddl_dir=pathlib.Path(args.ddl_dir),
        project="(unknown)",
        entity_count=0,
        validation=validation,
        exit_code=exit_code,
        extra_messages=extra,
    ))


def _emit_full_report(args, validation, generated, endpoints, exit_code, extra,
                      project="", entity_count=0):
    ddl_conversions = [
        ("V001__create_schema.sql", "(omitted)",     "HSQLDB has no schema concept"),
        ("V002__create_tables.sql", "schema.sql §1", "type map applied"),
        ("V003__create_indexes.sql", "schema.sql §2", "as-is after schema strip"),
        ("V004__create_constraints.sql", "schema.sql §3", "FK + CHECK preserved"),
    ]
    write_report(ReportInput(
        out_root=pathlib.Path(args.out),
        blueprint_path=pathlib.Path(args.blueprint),
        ddl_dir=pathlib.Path(args.ddl_dir),
        project=project,
        entity_count=entity_count,
        generated_files=generated,
        validation=validation,
        ddl_conversions=ddl_conversions,
        endpoints=endpoints,
        exit_code=exit_code,
        extra_messages=extra,
    ))


if __name__ == "__main__":
    sys.exit(main())
