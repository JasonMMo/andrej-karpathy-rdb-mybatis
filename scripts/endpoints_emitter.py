import json
import pathlib


def _nexacro_payload(entities, context_path):
    out_entities = []
    for e in entities:
        name = e["name"]
        base = f"/{name}"
        out_entities.append({
            "name": name,
            "endpoint_base": base,
            "endpoints": [
                {
                    "method": "select_datalist_map",
                    "http_path": f"{base}/select_datalist_map.do",
                    "input": {"dsSearch": "param-dataset"},
                    "output": {"output1": "list-dataset"},
                },
                {
                    "method": "save_datalist_map",
                    "http_path": f"{base}/save_datalist_map.do",
                    "input": {"dataList": "row-dispatch"},
                    "output": {},
                },
            ],
        })
    return {
        "version": 1,
        "context_path": context_path,
        "entities": out_entities,
    }


def _vanilla_payload(entities, context_path):
    out_entities = []
    for e in entities:
        name = e["name"]
        base = f"{context_path}/{name}"
        out_entities.append({
            "name": name,
            "endpoint_base": base,
            "endpoints": [
                {
                    "method": "GET",
                    "http_path": base,
                },
                {
                    "method": "POST",
                    "http_path": base,
                },
            ],
        })
    return {
        "version": 2,
        "lane": "vanilla",
        "context_path": context_path,
        "entities": out_entities,
    }


def build_endpoints_payload(entities, context_path="/uiadapter", lane="nexacro"):
    if lane == "vanilla":
        return _vanilla_payload(entities, context_path)
    return _nexacro_payload(entities, context_path)


def write_endpoints_json(out_root, payload):
    out = pathlib.Path(out_root) / "endpoints.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out
