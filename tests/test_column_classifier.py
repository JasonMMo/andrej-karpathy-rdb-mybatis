import pytest
from column_classifier import classify, validate_pk_coverage, ColumnClassifierError


def _entity(name, cols):
    return {"name": name, "table": "TB_" + name.upper(), "columns": cols}


def test_classify_pk_and_non_pk():
    e = _entity("customer", [
        {"name": "customer_id", "type": "varchar(36)", "pk": True},
        {"name": "name",        "type": "varchar(100)"},
        {"name": "email",       "type": "varchar(200)"},
    ])
    c = classify(e)
    assert [x["name"] for x in c["pk"]] == ["customer_id"]
    assert [x["name"] for x in c["non_pk"]] == ["name", "email"]
    assert [x["name"] for x in c["all"]] == ["customer_id", "name", "email"]


def test_validate_pk_coverage_passes():
    entities = [_entity("customer", [{"name": "id", "pk": True, "type": "int"}])]
    validate_pk_coverage(entities)


def test_validate_pk_coverage_fails_when_no_pk():
    entities = [_entity("orphan", [{"name": "x", "type": "int"}])]
    with pytest.raises(ColumnClassifierError, match="PK"):
        validate_pk_coverage(entities)
