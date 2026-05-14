# andrej-karpathy-rdb-mybatis

Stage 3 of the **business-fullstack-creater** pipeline.

```
Stage 1 (rdb-skill) → Stage 2 (rdb-ddl) → **Stage 3 (this)** → Stage 4 (nexacro-claude-skills)
```

Generates a complete MyBatis + nexacro uiadapter `backend/` from a Stage 1 `_blueprint.yaml` and Stage 2 V001~V004 PostgreSQL DDL.

## Install

```bash
/plugin marketplace add D:\AI\workspace\andrej-karpathy-rdb-mybatis
/plugin install andrej-karpathy-rdb-mybatis
```

## Usage

```bash
/karpathy-rdb-mybatis compile \
  --blueprint wiki/_blueprint.yaml \
  --ddl-dir db/migrations \
  --out backend/
```

Optional:
- `--package com.nexacro.uiadapter` (default)
- `--skip-compile` — skip R006 javac check
- `--dry-run` — write report only, no code

## What it generates (per entity)

| Path | Purpose |
|---|---|
| `src/main/java/.../controller/<Entity>Controller.java` | `select_datalist_map.do`, `save_datalist_map.do` |
| `src/main/java/.../service/<Entity>Service.java` | interface |
| `src/main/java/.../service/impl/<Entity>ServiceImpl.java` | `@Transactional`, rowType dispatch |
| `src/main/java/.../mapper/<Entity>Mapper.java` | MyBatis interface |
| `src/main/resources/mybatis/mapper/<Entity>Mapper.xml` | CRUD + dynamic search |
| `src/main/java/.../domain/<Entity>.java` | Plain POJO extends NexacroBase |

Plus:
- `src/main/resources/schema.sql` — HSQLDB DDL (V001~V004 converted)
- `src/main/resources/data.sql` — seed (optional)
- `mybatis-report.md` — validation + file inventory

## Validation

| Rule | Check | On fail |
|---|---|---|
| R001 | blueprint version == 1 | exit 1 |
| R002 | validation.passed == true | exit 1 |
| R003 | V001~V004 present | exit 1 |
| R004 | every entity has PK | exit 1 |
| R005 | mapper xml namespace + id alignment | exit 2 (artifacts preserved) |
| R006 | javac compile clean (requires `NEXACRO_LIBS_DIR`) | exit 2 (artifacts preserved) |

## Development

```bash
python -m pip install -e .[dev]
pytest -v
```
