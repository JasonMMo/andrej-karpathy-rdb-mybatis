"""Growth-32 followup B — jakarta lane domain is a plain POJO.

See test_codegen_lane_javax for the full rationale. jakarta lane shares the
same Map-only pipeline as javax, so the entity class is a plain POJO without
JPA annotations regardless of which `persistence` namespace is on classpath.
"""
import pathlib
from codegen import render_entity_files


ENTITY = {
    "name": "customer",
    "table": "TB_CUSTOMER",
    "columns": [
        {"name": "customer_id", "type": "varchar(36)", "pk": True},
        {"name": "name",        "type": "varchar(100)"},
        {"name": "email",       "type": "varchar(200)"},
    ],
}


def _render(tmp_path):
    return render_entity_files(tmp_path, ENTITY, base_package="com.x.app", lane="jakarta")


def test_jakarta_entity_is_plain_pojo_no_jpa(tmp_path):
    _render(tmp_path)
    entity = (tmp_path / "src/main/java/com/x/app/domain/Customer.java").read_text(encoding="utf-8")
    assert "jakarta.persistence" not in entity
    assert "javax.persistence" not in entity
    assert "@Entity" not in entity
    assert "@Table" not in entity
    assert "@Id" not in entity
    assert "@Column" not in entity
    assert "@Transient" not in entity


def test_jakarta_entity_has_fields_and_accessors(tmp_path):
    _render(tmp_path)
    entity = (tmp_path / "src/main/java/com/x/app/domain/Customer.java").read_text(encoding="utf-8")
    assert "private String customerId;" in entity
    assert "private String email;" in entity
    assert "public String getEmail()" in entity


def test_jakarta_controller_is_rest_style(tmp_path):
    _render(tmp_path)
    ctrl = (tmp_path / "src/main/java/com/x/app/controller/CustomerController.java").read_text(encoding="utf-8")
    assert "@RestController" in ctrl
    assert '@RequestMapping("/api/customer")' in ctrl
    assert "NexacroResult" not in ctrl
    assert "NexacroException" not in ctrl


def test_jakarta_service_impl_has_iud_branches(tmp_path):
    _render(tmp_path)
    impl = (tmp_path / "src/main/java/com/x/app/service/impl/CustomerServiceImpl.java").read_text(encoding="utf-8")
    assert '"I".equals(rowType)' in impl
    assert '"U".equals(rowType)' in impl
    assert '"D".equals(rowType)' in impl
    assert "insert_customer_map" in impl
    assert "update_customer_map" in impl
    assert "delete_customer_map" in impl
    assert "NexacroBase" not in impl


def test_jakarta_service_interface_is_rest_contract(tmp_path):
    """Growth-32 followup C — interface must match service-impl signatures."""
    _render(tmp_path)
    iface = (tmp_path / "src/main/java/com/x/app/service/CustomerService.java").read_text(encoding="utf-8")
    assert "List<Map<String, Object>> select_customer_datalist_map(Map<String, Object> params);" in iface
    assert "int save_customer_datalist_map(List<Map<String, Object>> rows);" in iface
    assert "Map<String, String>" not in iface
    assert "void save_" not in iface


def test_jakarta_mapper_interface_int_crud(tmp_path):
    """Growth-32 followup D — CRUD methods must return int, not void."""
    _render(tmp_path)
    mapper = (tmp_path / "src/main/java/com/x/app/mapper/CustomerMapper.java").read_text(encoding="utf-8")
    assert "int insert_customer_map(Map<String, Object> customer);" in mapper
    assert "int update_customer_map(Map<String, Object> customer);" in mapper
    assert "int delete_customer_map(Map<String, Object> customer);" in mapper
    assert "void insert_" not in mapper


def test_nexacro_lane_interfaces_unchanged(tmp_path):
    """Sanity: nexacro lane must keep its DataSet contract (Map<String,String>+void)."""
    render_entity_files(tmp_path, ENTITY, base_package="com.x.app", lane="nexacro")
    iface = (tmp_path / "src/main/java/com/x/app/service/CustomerService.java").read_text(encoding="utf-8")
    assert "Map<String, String> searchMap" in iface
    assert "void save_customer_datalist_map(List<Map<String, Object>> dataList);" in iface
