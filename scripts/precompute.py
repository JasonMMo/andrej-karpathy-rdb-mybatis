from name_mapper import to_upper_snake, to_camel, to_pascal
from column_classifier import classify

NEXACRO_LIB_PREFIX = "com.nexacro.uiadapter"


def gather_mapper_columns(entity: dict) -> dict:
    c = classify(entity)
    return {
        "pk_upper":     [to_upper_snake(x["name"]) for x in c["pk"]],
        "non_pk_upper": [to_upper_snake(x["name"]) for x in c["non_pk"]],
        "all_upper":    [to_upper_snake(x["name"]) for x in c["all"]],
        "all_lower":    [x["name"] for x in c["all"]],
    }


def build_save_branches(entity: dict) -> list:
    name = entity["name"]
    return [
        {"row_type_const": "DataSet.ROW_TYPE_INSERTED", "mapper_method": f"insert_{name}_map"},
        {"row_type_const": "DataSet.ROW_TYPE_UPDATED",  "mapper_method": f"update_{name}_map"},
        {"row_type_const": "DataSet.ROW_TYPE_DELETED",  "mapper_method": f"delete_{name}_map"},
    ]


def build_search_predicates(entity: dict) -> list:
    cols = gather_mapper_columns(entity)["all_upper"]
    return [
        f'<if test="{c} != null and {c} != \'\'"> AND {c} = #{{{c}}}</if>'
        for c in cols
    ]


_TYPE_MAP = {
    "varchar": "String", "char": "String", "text": "String", "longvarchar": "String",
    "int": "Integer", "integer": "Integer", "smallint": "Integer",
    "bigint": "Long", "long": "Long",
    "numeric": "java.math.BigDecimal", "decimal": "java.math.BigDecimal",
    "boolean": "Boolean", "bool": "Boolean",
    "timestamp": "java.sql.Timestamp", "date": "java.sql.Date", "time": "java.sql.Time",
}

_SEARCH_FIELDS = [
    {"field": "searchCondition", "java_type": "String"},
    {"field": "searchKeyword",   "java_type": "String"},
    {"field": "searchUseYn",     "java_type": "String"},
]


def _java_type_for(sql_type: str) -> str:
    base = (sql_type or "").split("(")[0].strip().lower()
    return _TYPE_MAP.get(base, "String")


def build_domain_fields(entity: dict) -> list:
    out = []
    for c in entity.get("columns") or []:
        field = to_camel(c["name"])
        jt = _java_type_for(c.get("type"))
        cap = field[0].upper() + field[1:]
        out.append({"field": field, "java_type": jt, "getter": f"get{cap}", "setter": f"set{cap}"})
    for sf in _SEARCH_FIELDS:
        cap = sf["field"][0].upper() + sf["field"][1:]
        out.append({"field": sf["field"], "java_type": sf["java_type"],
                    "getter": f"get{cap}", "setter": f"set{cap}"})
    return out


def build_entity_context(entity: dict, base_package: str) -> dict:
    name = entity["name"]
    pascal = to_pascal(name)
    return {
        "entity_name": name,
        "pascal": pascal,
        "camel": to_camel(name),
        "table": entity["table"],
        "base_package": base_package,
        "lib_prefix": NEXACRO_LIB_PREFIX,
        "mapper_fqcn": f"{base_package}.mapper.{pascal}Mapper",
        "endpoint_base": f"/{name}",
        "mapper_columns": gather_mapper_columns(entity),
        "save_branches": build_save_branches(entity),
        "search_predicates": build_search_predicates(entity),
        "fields": build_domain_fields(entity),
    }
