import json
import pathlib


def build_endpoints_payload(entities, context_path="/uiadapter"):
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


def write_endpoints_json(out_root, payload):
    out = pathlib.Path(out_root) / "endpoints.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out
