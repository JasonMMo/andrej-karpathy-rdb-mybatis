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


from precompute import build_domain_fields, build_entity_context


def test_build_domain_fields():
    entity = {"name": "customer", "columns": [
        {"name": "customer_id", "type": "varchar(36)", "pk": True},
        {"name": "status", "type": "varchar(20)"},
    ]}
    fields = build_domain_fields(entity)
    field_names = [f["field"] for f in fields]
    assert "customerId" in field_names
    assert "status" in field_names
    # auto search fields
    assert "searchCondition" in field_names
    assert "searchKeyword" in field_names
    assert "searchUseYn" in field_names
    customer_id = next(f for f in fields if f["field"] == "customerId")
    assert customer_id["java_type"] == "String"
    assert customer_id["getter"] == "getCustomerId"
    assert customer_id["setter"] == "setCustomerId"


def test_build_entity_context_shape():
    entity = {"name": "customer", "table": "TB_CUSTOMER", "columns": [
        {"name": "customer_id", "type": "varchar(36)", "pk": True},
        {"name": "name", "type": "varchar(100)"},
    ]}
    ctx = build_entity_context(entity, base_package="com.nexacro.uiadapter")
    assert ctx["entity_name"] == "customer"
    assert ctx["pascal"] == "Customer"
    assert ctx["camel"] == "customer"
    assert ctx["table"] == "TB_CUSTOMER"
    assert ctx["base_package"] == "com.nexacro.uiadapter"
    assert ctx["mapper_fqcn"] == "com.nexacro.uiadapter.mapper.CustomerMapper"
    assert ctx["endpoint_base"] == "/customer"
    assert ctx["mapper_columns"]["pk_upper"] == ["CUSTOMER_ID"]
    assert ctx["save_branches"][0]["mapper_method"] == "insert_customer_map"
    assert ctx["search_predicates"][0].startswith('<if test="CUSTOMER_ID')
    assert ctx["fields"][0]["field"] == "customerId"
