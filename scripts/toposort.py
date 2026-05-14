def topo_sort(entities: list, relations: list) -> list:
    by_name = {e["name"]: e for e in entities}
    indeg = {n: 0 for n in by_name}
    edges = {n: [] for n in by_name}
    for r in relations or []:
        src, dst = r.get("from"), r.get("to")
        if src in by_name and dst in by_name and src != dst:
            edges[dst].append(src)
            indeg[src] += 1
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
    # any cycle remainder: append in declaration order
    remaining = [e for e in entities if e["name"] not in {x["name"] for x in out}]
    return out + remaining
