from name_mapper import to_upper_snake
from column_classifier import classify


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
