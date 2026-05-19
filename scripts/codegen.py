import pathlib
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from precompute import build_entity_context


TEMPLATE_ROOT = pathlib.Path(__file__).resolve().parent.parent / ".claude" / "skills" / "karpathy-rdb-mybatis" / "templates"


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_ROOT)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )


def _write(path: pathlib.Path, content: str) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def render_entity_files(out_root: pathlib.Path, entity: dict, base_package: str, lane: str = "nexacro") -> list:
    out_root = pathlib.Path(out_root)
    ctx = build_entity_context(entity, base_package=base_package, lane=lane)
    env = _env()

    pkg_path = base_package.replace(".", "/")
    java_root = out_root / "src" / "main" / "java" / pkg_path
    xml_root  = out_root / "src" / "main" / "resources" / "mybatis" / "mapper"

    suffix = "" if lane == "nexacro" else f".{lane}"

    written = []
    written.append(_write(java_root / "domain" / f"{ctx['pascal']}.java",
                          env.get_template(f"domain/entity{suffix}.java.j2").render(**ctx)))
    written.append(_write(java_root / "mapper" / f"{ctx['pascal']}Mapper.java",
                          env.get_template("mapper/mapper-interface.java.j2").render(**ctx)))
    written.append(_write(xml_root / f"{ctx['pascal']}Mapper.xml",
                          env.get_template("mapper/mapper.xml.j2").render(**ctx)))
    written.append(_write(java_root / "service" / f"{ctx['pascal']}Service.java",
                          env.get_template("service/service-interface.java.j2").render(**ctx)))
    written.append(_write(java_root / "service" / "impl" / f"{ctx['pascal']}ServiceImpl.java",
                          env.get_template(f"service/service-impl{suffix}.java.j2").render(**ctx)))
    written.append(_write(java_root / "controller" / f"{ctx['pascal']}Controller.java",
                          env.get_template(f"controller/controller{suffix}.java.j2").render(**ctx)))
    return written


def render_schema_sql(out_root: pathlib.Path, converted_sql: str) -> pathlib.Path:
    env = _env()
    text = env.get_template("ddl/schema.sql.j2").render(converted_sql=converted_sql)
    return _write(pathlib.Path(out_root) / "src" / "main" / "resources" / "schema.sql", text)


def render_data_sql(out_root: pathlib.Path, converted_seed: str) -> pathlib.Path:
    env = _env()
    text = env.get_template("ddl/data.sql.j2").render(converted_seed=converted_seed)
    return _write(pathlib.Path(out_root) / "src" / "main" / "resources" / "data.sql", text)
