class ColumnClassifierError(Exception):
    pass


def classify(entity: dict) -> dict:
    cols = entity.get("columns") or []
    pk = [c for c in cols if c.get("pk")]
    non_pk = [c for c in cols if not c.get("pk")]
    return {"pk": pk, "non_pk": non_pk, "all": cols}


def validate_pk_coverage(entities: list) -> None:
    bad = [e["name"] for e in entities if not any(c.get("pk") for c in (e.get("columns") or []))]
    if bad:
        raise ColumnClassifierError(f"entities without PK: {bad}")
