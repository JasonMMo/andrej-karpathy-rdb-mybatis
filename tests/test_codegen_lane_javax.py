"""Growth-32 followup B — javax lane domain is a plain POJO.

Original v0.5 H3 templates emitted `@Entity` + `javax.persistence.*` even though
the rest of the javax lane (controller/service/mapper) is Map-only. JPA was
never on the runtime classpath, so the generated `import javax.persistence.*`
broke the Maven build during live WAS validation (Growth-32, boot-jdk8-javax).

Contract now: javax/jakarta entity classes are plain POJOs — same shape as
vanilla — so the Map-only pipeline compiles without a JPA dependency.
"""
import pathlib
from codegen import render_entity_files


ENTITY = {
    "name": "customer",
    "table": "TB_CUSTOMER",
    "columns": [
        {"name": "customer_id", "type": "varchar(36)", "pk": True},
        {"name": "name",        "type": "varchar(100)"},
    ],
}


def _render(tmp_path):
    return render_entity_files(tmp_path, ENTITY, base_package="com.x.app", lane="javax")


def test_javax_entity_is_plain_pojo_no_jpa(tmp_path):
    _render(tmp_path)
    entity = (tmp_path / "src/main/java/com/x/app/domain/Customer.java").read_text(encoding="utf-8")
    # No JPA imports of any flavor
    assert "javax.persistence" not in entity
    assert "jakarta.persistence" not in entity
    # No JPA annotations
    assert "@Entity" not in entity
    assert "@Table" not in entity
    assert "@Id" not in entity
    assert "@Column" not in entity
    assert "@Transient" not in entity


def test_javax_entity_has_fields_and_accessors(tmp_path):
    _render(tmp_path)
    entity = (tmp_path / "src/main/java/com/x/app/domain/Customer.java").read_text(encoding="utf-8")
    assert "private String customerId;" in entity
    assert "private String name;" in entity
    assert "public String getCustomerId()" in entity
    assert "public void setName(String v)" in entity


def test_javax_controller_is_rest_style(tmp_path):
    _render(tmp_path)
    ctrl = (tmp_path / "src/main/java/com/x/app/controller/CustomerController.java").read_text(encoding="utf-8")
    assert "@RestController" in ctrl
    assert '@RequestMapping("/api/customer")' in ctrl
    assert "NexacroResult" not in ctrl


def test_javax_service_impl_has_iud_branches(tmp_path):
    _render(tmp_path)
    impl = (tmp_path / "src/main/java/com/x/app/service/impl/CustomerServiceImpl.java").read_text(encoding="utf-8")
    assert '"I".equals(rowType)' in impl
    assert '"U".equals(rowType)' in impl
    assert '"D".equals(rowType)' in impl
    assert "NexacroBase" not in impl


def test_javax_service_interface_is_rest_contract(tmp_path):
    """Growth-32 followup C — interface must match service-impl signatures."""
    _render(tmp_path)
    iface = (tmp_path / "src/main/java/com/x/app/service/CustomerService.java").read_text(encoding="utf-8")
    assert "List<Map<String, Object>> select_customer_datalist_map(Map<String, Object> params);" in iface
    assert "int save_customer_datalist_map(List<Map<String, Object>> rows);" in iface
    # Must NOT use nexacro contract
    assert "Map<String, String>" not in iface
    assert "void save_" not in iface


def test_javax_mapper_interface_int_crud(tmp_path):
    """Growth-32 followup D — CRUD methods must return int, not void."""
    _render(tmp_path)
    mapper = (tmp_path / "src/main/java/com/x/app/mapper/CustomerMapper.java").read_text(encoding="utf-8")
    assert "int insert_customer_map(Map<String, Object> customer);" in mapper
    assert "int update_customer_map(Map<String, Object> customer);" in mapper
    assert "int delete_customer_map(Map<String, Object> customer);" in mapper
    assert "void insert_" not in mapper
    assert "void update_" not in mapper
    assert "void delete_" not in mapper


def test_javax_mapper_interface_has_mapper_annotation(tmp_path):
    """Growth-33 followup F — runner registers mapper beans via @Mapper
    annotation auto-discovery (no @MapperScan). Without @Mapper the Spring
    context fails: NoSuchBeanDefinitionException at autowire time."""
    _render(tmp_path)
    mapper = (tmp_path / "src/main/java/com/x/app/mapper/CustomerMapper.java").read_text(encoding="utf-8")
    assert "import org.apache.ibatis.annotations.Mapper;" in mapper
    assert "@Mapper" in mapper
