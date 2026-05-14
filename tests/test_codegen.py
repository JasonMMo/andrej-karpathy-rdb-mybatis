import pathlib
from codegen import render_entity_files

ENTITY = {
    "name": "customer",
    "table": "TB_CUSTOMER",
    "columns": [
        {"name": "customer_id", "type": "varchar(36)", "pk": True},
        {"name": "name",        "type": "varchar(100)"},
        {"name": "email",       "type": "varchar(200)"},
        {"name": "status",      "type": "varchar(20)"},
    ],
}


def test_render_entity_files_writes_six_files(tmp_path):
    out = tmp_path / "backend"
    paths = render_entity_files(out, ENTITY, base_package="com.nexacro.uiadapter")
    assert (out / "src/main/java/com/nexacro/uiadapter/domain/Customer.java").exists()
    assert (out / "src/main/java/com/nexacro/uiadapter/mapper/CustomerMapper.java").exists()
    assert (out / "src/main/resources/mybatis/mapper/CustomerMapper.xml").exists()
    assert (out / "src/main/java/com/nexacro/uiadapter/service/CustomerService.java").exists()
    assert (out / "src/main/java/com/nexacro/uiadapter/service/impl/CustomerServiceImpl.java").exists()
    assert (out / "src/main/java/com/nexacro/uiadapter/controller/CustomerController.java").exists()
    assert len(paths) == 6


def test_controller_has_expected_endpoints(tmp_path):
    out = tmp_path / "backend"
    render_entity_files(out, ENTITY, base_package="com.nexacro.uiadapter")
    ctrl = (out / "src/main/java/com/nexacro/uiadapter/controller/CustomerController.java").read_text(encoding="utf-8")
    assert "/customer/select_datalist_map.do" in ctrl
    assert "/customer/save_datalist_map.do" in ctrl


def test_mapper_xml_namespace_matches_interface(tmp_path):
    out = tmp_path / "backend"
    render_entity_files(out, ENTITY, base_package="com.nexacro.uiadapter")
    xml = (out / "src/main/resources/mybatis/mapper/CustomerMapper.xml").read_text(encoding="utf-8")
    assert 'namespace="com.nexacro.uiadapter.mapper.CustomerMapper"' in xml


def test_service_impl_has_three_branches(tmp_path):
    out = tmp_path / "backend"
    render_entity_files(out, ENTITY, base_package="com.nexacro.uiadapter")
    impl = (out / "src/main/java/com/nexacro/uiadapter/service/impl/CustomerServiceImpl.java").read_text(encoding="utf-8")
    assert "ROW_TYPE_INSERTED" in impl
    assert "ROW_TYPE_UPDATED" in impl
    assert "ROW_TYPE_DELETED" in impl
    assert "insert_customer_map" in impl
    assert "update_customer_map" in impl
    assert "delete_customer_map" in impl


from toposort import topo_sort


def test_topo_sort_fk_aware():
    entities = [
        {"name": "address", "table": "TB_ADDRESS", "columns": [{"name": "address_id", "pk": True}]},
        {"name": "customer", "table": "TB_CUSTOMER", "columns": [{"name": "customer_id", "pk": True}]},
    ]
    relations = [{"from": "address", "to": "customer", "fk": "customer_id"}]
    ordered = topo_sort(entities, relations)
    names = [e["name"] for e in ordered]
    # parent (customer) must come before child (address)
    assert names.index("customer") < names.index("address")
