import sys


def topo_sort(entities: list, relations: list) -> list:
    """Return entities in FK-dependency order (parents before children).

    Relation semantics: `from`/`to` direction is inconsistent in blueprints — N:1
    expresses child→parent, 1:N expresses parent→child. We normalize using
    cardinality so the FK-bearing side is always the dependent.
    """
    by_name = {e["name"]: e for e in entities}
    indeg = {n: 0 for n in by_name}
    edges = {n: [] for n in by_name}
    for r in relations or []:
        src, dst = r.get("from"), r.get("to")
        if src not in by_name or dst not in by_name or src == dst:
            continue
        card = (r.get("cardinality") or "").upper().replace(" ", "")
        # Normalize so `child` holds the FK and depends on `parent`.
        if card in ("1:N", "1:M"):
            child, parent = dst, src
        else:  # N:1, M:1, 1:1, or unspecified — assume `from` is the FK side
            child, parent = src, dst
        edges[parent].append(child)
        indeg[child] += 1
    order = [n for n, d in indeg.items() if d == 0]
    out = []
    i = 0
    while i < len(order):
        n = order[i]; i += 1
        out.append(by_name[n])
        for m in edges[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                order.append(m)
    # any cycle remainder: warn and append in declaration order
    settled = {x["name"] for x in out}
    remaining = [e for e in entities if e["name"] not in settled]
    if remaining:
        print(
            f"[toposort] WARNING: FK cycle detected; appending in declaration "
            f"order: {[e['name'] for e in remaining]}",
            file=sys.stderr,
        )
    return out + remaining
