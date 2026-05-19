"""v0.5 H3 — jakarta lane regression (JPA entity with jakarta.persistence)."""
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


def test_jakarta_entity_uses_jakarta_persistence(tmp_path):
    _render(tmp_path)
    entity = (tmp_path / "src/main/java/com/x/app/domain/Customer.java").read_text(encoding="utf-8")
    assert "import jakarta.persistence.Entity;" in entity
    assert "import jakarta.persistence.Id;" in entity
    assert "import jakarta.persistence.Column;" in entity
    assert "import jakarta.persistence.Table;" in entity
    assert "import jakarta.persistence.Transient;" in entity
    assert "javax.persistence" not in entity


def test_jakarta_entity_has_pk_annotation(tmp_path):
    _render(tmp_path)
    entity = (tmp_path / "src/main/java/com/x/app/domain/Customer.java").read_text(encoding="utf-8")
    assert "@Entity" in entity
    assert '@Table(name = "TB_CUSTOMER")' in entity
    assert "@Id" in entity
    assert '@Column(name = "customer_id")' in entity


def test_jakarta_entity_marks_search_fields_transient(tmp_path):
    _render(tmp_path)
    entity = (tmp_path / "src/main/java/com/x/app/domain/Customer.java").read_text(encoding="utf-8")
    # search fields should be @Transient (not @Column)
    assert "@Transient" in entity
    assert "searchCondition" in entity
    assert "searchKeyword" in entity
    assert "searchUseYn" in entity


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
