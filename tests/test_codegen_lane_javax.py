"""v0.5 H3 — javax lane regression (JPA entity with javax.persistence, JDK8/11)."""
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


def test_javax_entity_uses_javax_persistence(tmp_path):
    _render(tmp_path)
    entity = (tmp_path / "src/main/java/com/x/app/domain/Customer.java").read_text(encoding="utf-8")
    assert "import javax.persistence.Entity;" in entity
    assert "import javax.persistence.Id;" in entity
    assert "import javax.persistence.Column;" in entity
    assert "import javax.persistence.Table;" in entity
    assert "import javax.persistence.Transient;" in entity
    assert "jakarta.persistence" not in entity


def test_javax_entity_has_pk_and_table(tmp_path):
    _render(tmp_path)
    entity = (tmp_path / "src/main/java/com/x/app/domain/Customer.java").read_text(encoding="utf-8")
    assert "@Entity" in entity
    assert '@Table(name = "TB_CUSTOMER")' in entity
    assert "@Id" in entity


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
