---
name: karpathy-rdb-mybatis
description: Generates MyBatis + nexacro uiadapter backend (controller/service/mapper/domain + schema.sql/data.sql) from Stage 1 blueprint and Stage 2 DDL.
---

# karpathy-rdb-mybatis

Stage 3 of the business-fullstack-creater pipeline.

## Inputs
- `wiki/_blueprint.yaml` — Stage 1 output (version 1, validation.passed must be true)
- `db/migrations/V001~V004__*.sql` — Stage 2 PostgreSQL DDL
- `db/seed/*.sql` (optional) — Stage 2 seed rows

## Outputs (under `--out`, default `backend/`)
- `src/main/java/com/nexacro/uiadapter/{controller,service,service/impl,mapper,domain}/*.java`
- `src/main/resources/schema.sql`, `data.sql`
- `src/main/resources/mybatis/mapper/*.xml`
- `mybatis-report.md`

## Conventions
- 4.2 canonical package layout under `com.nexacro.uiadapter`
- Plain POJO `extends NexacroBase`, no Lombok, no JPA
- Endpoints `/<entity>/select_datalist_map.do`, `/<entity>/save_datalist_map.do`
- Map-based search input, `List<Map<String,Object>>` output
- HSQLDB runtime via `schema.sql` (Spring Boot bootstrap)

See `references/` for the input contract, output layout, and uiadapter spec.
