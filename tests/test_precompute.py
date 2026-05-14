from precompute import gather_mapper_columns


def test_gather_mapper_columns_basic():
    entity = {
        "name": "customer",
        "table": "TB_CUSTOMER",
        "columns": [
            {"name": "customer_id", "type": "varchar(36)", "pk": True},
            {"name": "name",        "type": "varchar(100)"},
            {"name": "email",       "type": "varchar(200)"},
        ],
    }
    out = gather_mapper_columns(entity)
    assert out["pk_upper"] == ["CUSTOMER_ID"]
    assert out["non_pk_upper"] == ["NAME", "EMAIL"]
    assert out["all_upper"] == ["CUSTOMER_ID", "NAME", "EMAIL"]
    assert out["all_lower"] == ["customer_id", "name", "email"]
