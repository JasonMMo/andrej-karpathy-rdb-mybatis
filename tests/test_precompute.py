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


from precompute import build_save_branches, build_search_predicates


def test_build_save_branches():
    entity = {"name": "customer", "columns": [{"name": "customer_id", "pk": True}]}
    branches = build_save_branches(entity)
    assert branches == [
        {"row_type_const": "DataSet.ROW_TYPE_INSERTED", "mapper_method": "insert_customer_map"},
        {"row_type_const": "DataSet.ROW_TYPE_UPDATED",  "mapper_method": "update_customer_map"},
        {"row_type_const": "DataSet.ROW_TYPE_DELETED",  "mapper_method": "delete_customer_map"},
    ]


def test_build_search_predicates():
    entity = {"name": "customer", "columns": [
        {"name": "customer_id", "pk": True},
        {"name": "name"},
        {"name": "email"},
    ]}
    preds = build_search_predicates(entity)
    assert preds == [
        '<if test="CUSTOMER_ID != null and CUSTOMER_ID != \'\'"> AND CUSTOMER_ID = #{CUSTOMER_ID}</if>',
        '<if test="NAME != null and NAME != \'\'"> AND NAME = #{NAME}</if>',
        '<if test="EMAIL != null and EMAIL != \'\'"> AND EMAIL = #{EMAIL}</if>',
    ]
