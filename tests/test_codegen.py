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


def test_nexacro_lib_prefix_independent_of_base_package(tmp_path):
    """When --package is a custom value, NexacroN *library* imports must still
    point at com.nexacro.uiadapter.jakarta.core (the fixed library prefix).
    NexacroBase is project-local (not in the library JAR), so it lives at
    {project_root_pkg}.domain.NexacroBase. When project_root_pkg defaults to
    base_package, generated POJOs sit in the same package as NexacroBase and
    need NO import."""
    out = tmp_path / "backend"
    render_entity_files(out, ENTITY, base_package="com.mycompany.app")
    java_root = out / "src/main/java/com/mycompany/app"
    ctrl = (java_root / "controller/CustomerController.java").read_text(encoding="utf-8")
    impl = (java_root / "service/impl/CustomerServiceImpl.java").read_text(encoding="utf-8")
    domain = (java_root / "domain/Customer.java").read_text(encoding="utf-8")
    # library types stay at fixed nexacro prefix
    assert "import com.nexacro.uiadapter.jakarta.core.data.NexacroResult;" in ctrl
    assert "import com.nexacro.uiadapter.jakarta.core.NexacroException;" in ctrl
    assert "import com.nexacro.uiadapter.jakarta.core.data.DataSetRowTypeAccessor;" in impl
    # NexacroBase is project-local and lives in same package as Customer → no import
    assert "import" not in domain.split("public class")[0].split("package")[1]
    assert "extends NexacroBase" in domain
    # project types use the custom base package
    assert "package com.mycompany.app.controller;" in ctrl
    assert "import com.mycompany.app.service.CustomerService;" in ctrl
    assert "import com.mycompany.app.mapper.CustomerMapper;" in impl


def test_nexacro_base_import_when_in_subpackage(tmp_path):
    """When generated POJOs live in a sub-package (e.g. base_package=
    com.nexacro.uiadapter.customer with project_root_pkg=com.nexacro.uiadapter),
    NexacroBase must be explicitly imported from {project_root_pkg}.domain."""
    out = tmp_path / "backend"
    render_entity_files(
        out, ENTITY,
        base_package="com.nexacro.uiadapter.customer",
        project_root_pkg="com.nexacro.uiadapter",
    )
    domain = (out / "src/main/java/com/nexacro/uiadapter/customer/domain/Customer.java").read_text(encoding="utf-8")
    assert "package com.nexacro.uiadapter.customer.domain;" in domain
    assert "import com.nexacro.uiadapter.domain.NexacroBase;" in domain
    assert "extends NexacroBase" in domain


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


def test_render_entity_files_vanilla_lane(tmp_path):
    entity = {
        "name": "user", "table": "TB_USER",
        "columns": [{"name": "id", "pk": True, "type": "bigint"}, {"name": "name", "type": "varchar(50)"}],
    }
    written = render_entity_files(tmp_path, entity, base_package="com.x.app", lane="vanilla")
    entity_java = pathlib.Path([p for p in written if p.name == "User.java"][0]).read_text(encoding="utf-8")
    assert "extends NexacroBase" not in entity_java
    assert "package com.x.app.domain" in entity_java

    controller_java = pathlib.Path([p for p in written if p.name == "UserController.java"][0]).read_text(encoding="utf-8")
    assert "@RestController" in controller_java
    assert "NexacroResult" not in controller_java
    assert '@RequestMapping("/api/user")' in controller_java


from codegen import render_schema_sql
from ddl_loader import DDLBundle
from postgres_to_hsqldb import convert_bundle


def test_render_schema_sql_writes_to_resources(tmp_path):
    bundle = DDLBundle(
        schema_sql="CREATE SCHEMA IF NOT EXISTS public;",
        tables_sql="CREATE TABLE public.TB_X (ID INT PRIMARY KEY);",
        indexes_sql="",
        constraints_sql="",
    )
    converted = convert_bundle(bundle)
    path = render_schema_sql(tmp_path / "backend", converted)
    text = path.read_text(encoding="utf-8")
    assert "Generated from db/migrations" in text
    assert "CREATE TABLE TB_X" in text
    assert "CREATE SCHEMA" not in text
