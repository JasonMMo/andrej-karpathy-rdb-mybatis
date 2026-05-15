# Vanilla Lane Spec Summary (v0.3+)

`--lane vanilla` 로 호출 시 산출되는 Spring + MyBatis 코드의 contract.

## Imports per layer (JDK17 + Spring Boot 3)
- Controller: `org.springframework.web.bind.annotation.{RestController, RequestMapping, GetMapping, PostMapping, RequestBody, RequestParam}`
- ServiceImpl: `org.springframework.stereotype.Service`, `org.springframework.beans.factory.annotation.Autowired`, `java.util.{List, Map}`
- Domain: 없음 (POJO no extends)

## Endpoint contract
- `GET  /api/<entity>` → `select_<entity>_datalist_map(Map params)` → `List<Map<String,Object>>`
- `POST /api/<entity>` → `save_<entity>_datalist_map(List<Map<String,Object>> rows)` → `int affected`

## Save dispatch (single endpoint, no DataSet)
요청 body 의 각 row Map 안에 `_rowType` 필드 (`"I" | "U" | "D"`) 로 라우팅.
```java
String rowType = String.valueOf(row.getOrDefault("_rowType", ""));
if ("I".equals(rowType)) { mapper.insert_<entity>_map(row); }
else if ("U".equals(rowType)) { mapper.update_<entity>_map(row); }
else if ("D".equals(rowType)) { mapper.delete_<entity>_map(row); }
```

## endpoints.json (v2)
```json
{
  "version": 2,
  "lane": "vanilla",
  "context_path": "/",
  "entities": [
    {"name": "product", "endpoint_base": "/api/product",
     "endpoints": [
       {"method": "select", "http": "GET",  "http_path": "/api/product",
        "input": {"params": "query-map"}, "output": {"body": "list-of-map"}},
       {"method": "save",   "http": "POST", "http_path": "/api/product",
        "input": {"body": "list-of-map"}, "output": {"body": "int-affected"}}
     ]}
  ]
}
```

## Mapper / DDL
nexacro lane 과 동일 — mapper interface, mapper.xml, schema.sql 에 lane 영향 없음.
