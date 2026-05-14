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
