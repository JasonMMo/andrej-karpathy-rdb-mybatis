# Blueprint Input Contract (Stage 1 → Stage 3)

Source: `wiki/_blueprint.yaml` produced by `/karpathy-rdb compile`.

## Required top-level keys
- `version`: must equal `1`
- `project`: string (Korean domain name)
- `entities`: list of `{name, table, schema, columns, indexes?, constraints?}`
- `relations`: list of `{from, to, cardinality, fk, on_delete?}`
- `business_rules`: list of `{name, applies_to, enforced_by}`
- `validation.passed`: must equal `true`

## Entity column shape
```yaml
columns:
  - { name: customer_id, type: varchar(36), pk: true, nullable: false }
  - { name: name,        type: varchar(100), nullable: true }
```

## Hard rejects
- `version != 1` → exit 1
- `validation.passed != true` → exit 1
- any entity with zero `pk: true` columns → exit 1
