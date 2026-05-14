import pathlib
import pytest
from ddl_loader import load, DDLBundleError

GOLDEN = pathlib.Path(__file__).parent / "fixtures" / "golden_ddl"


def test_golden_loads():
    bundle = load(GOLDEN)
    assert bundle.schema_sql.startswith("CREATE SCHEMA")
    assert "TB_CUSTOMER" in bundle.tables_sql
    assert "ix_tb_customer_email" in bundle.indexes_sql
    assert "FOREIGN KEY" in bundle.constraints_sql
    assert bundle.seed_files == []


def test_rejects_missing_file(tmp_path):
    (tmp_path / "V001__create_schema.sql").write_text("-- empty", encoding="utf-8")
    with pytest.raises(DDLBundleError, match="V002"):
        load(tmp_path)


def test_collects_seed_files(tmp_path):
    for n in ["V001__create_schema.sql","V002__create_tables.sql","V003__create_indexes.sql","V004__create_constraints.sql"]:
        (tmp_path / n).write_text("-- " + n, encoding="utf-8")
    seed = tmp_path.parent / "seed"
    seed.mkdir()
    (seed / "01_customer_sample.sql").write_text("INSERT INTO TB_CUSTOMER VALUES ('1','a','b','c');", encoding="utf-8")
    bundle = load(tmp_path, seed_dir=seed)
    assert len(bundle.seed_files) == 1
