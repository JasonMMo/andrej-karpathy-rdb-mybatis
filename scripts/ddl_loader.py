import pathlib
from dataclasses import dataclass, field


class DDLBundleError(Exception):
    pass


@dataclass
class DDLBundle:
    schema_sql: str = ""
    tables_sql: str = ""
    indexes_sql: str = ""
    constraints_sql: str = ""
    seed_files: list = field(default_factory=list)


REQUIRED = {
    "schema":      "V001__create_schema.sql",
    "tables":      "V002__create_tables.sql",
    "indexes":     "V003__create_indexes.sql",
    "constraints": "V004__create_constraints.sql",
}


def load(ddl_dir: pathlib.Path, seed_dir: pathlib.Path | None = None) -> DDLBundle:
    ddl_dir = pathlib.Path(ddl_dir)
    if not ddl_dir.exists():
        raise DDLBundleError(f"ddl dir not found: {ddl_dir}")
    bundle = DDLBundle()
    for slot, fname in REQUIRED.items():
        p = ddl_dir / fname
        if not p.exists():
            raise DDLBundleError(f"missing required DDL file: {fname}")
        setattr(bundle, f"{slot}_sql", p.read_text(encoding="utf-8"))
    if seed_dir and pathlib.Path(seed_dir).exists():
        bundle.seed_files = sorted(pathlib.Path(seed_dir).glob("*.sql"))
    return bundle
