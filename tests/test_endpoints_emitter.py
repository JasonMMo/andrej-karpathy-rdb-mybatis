import json
import pathlib

from endpoints_emitter import build_endpoints_payload, write_endpoints_json


def test_build_endpoints_payload_two_methods_per_entity():
    entities = [
        {"name": "customer", "table": "TB_CUSTOMER"},
        {"name": "customer_address", "table": "TB_CUSTOMER_ADDRESS"},
    ]
    payload = build_endpoints_payload(entities, context_path="/uiadapter")
    assert payload["version"] == 1
    assert payload["context_path"] == "/uiadapter"
    names = [e["name"] for e in payload["entities"]]
    assert names == ["customer", "customer_address"]
    cust = payload["entities"][0]
    assert cust["endpoint_base"] == "/customer"
    methods = [ep["method"] for ep in cust["endpoints"]]
    assert methods == ["select_datalist_map", "save_datalist_map"]
    assert cust["endpoints"][0]["http_path"] == "/customer/select_datalist_map.do"
    assert cust["endpoints"][0]["input"] == {"dsSearch": "param-dataset"}
    assert cust["endpoints"][0]["output"] == {"output1": "list-dataset"}
    assert cust["endpoints"][1]["input"] == {"dataList": "row-dispatch"}
    assert cust["endpoints"][1]["output"] == {}


def test_write_endpoints_json_round_trip(tmp_path):
    payload = {"version": 1, "context_path": "/x", "entities": []}
    p = write_endpoints_json(tmp_path, payload)
    assert p == tmp_path / "endpoints.json"
    assert json.loads(p.read_text(encoding="utf-8")) == payload


def test_build_endpoints_payload_empty_entities():
    payload = build_endpoints_payload([], context_path="/uiadapter")
    assert payload == {"version": 1, "context_path": "/uiadapter", "entities": []}


def test_build_endpoints_payload_default_context_path():
    payload = build_endpoints_payload([{"name": "x"}])
    assert payload["context_path"] == "/uiadapter"


def test_vanilla_payload_shape():
    entities = [{"name": "order", "table": "TB_ORDER"}]
    payload = build_endpoints_payload(entities, context_path="/api", lane="vanilla")
    assert payload["version"] == 2
    assert payload["lane"] == "vanilla"
    assert payload["context_path"] == "/api"
    ent = payload["entities"][0]
    assert ent["name"] == "order"
    methods = [ep["method"] for ep in ent["endpoints"]]
    assert "GET" in methods
    assert "POST" in methods
    paths = [ep["http_path"] for ep in ent["endpoints"]]
    assert "/api/order" in paths


def test_nexacro_payload_unchanged():
    entities = [{"name": "customer", "table": "TB_CUSTOMER"}]
    payload = build_endpoints_payload(entities, context_path="/uiadapter", lane="nexacro")
    assert payload["version"] == 1
    assert "lane" not in payload
    cust = payload["entities"][0]
    methods = [ep["method"] for ep in cust["endpoints"]]
    assert methods == ["select_datalist_map", "save_datalist_map"]
