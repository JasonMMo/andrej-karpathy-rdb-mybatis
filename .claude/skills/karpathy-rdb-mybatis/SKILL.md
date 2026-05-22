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

## Lanes (v0.3+)

- `--lane nexacro` (default) — Nexacro UIAdapter 기반 산출 (`NexacroBase` extends, `NexacroResult` 반환, `.do` 엔드포인트). 자세한 컨트랙트는 `references/nexacro-uiadapter-spec.md`.
- `--lane vanilla` — 의존성 없는 순수 Spring + MyBatis 산출 (`@RestController`, REST 엔드포인트, POJO entity). `references/vanilla-spec.md`.

See `references/` for the input contract, output layout, and uiadapter spec.

## Ownership & Self-Check (Phase A — 2026-05-22)

이 skill 은 **business-fullstack-creater 5축 책임표의 `mybatis (Stage 3)` 축**을 담당. 활동 뷰는 `business-fullstack-creater/learn-log.md` §0.

- **깊이 누적 위치**: `templates/<lane>/` (nexacro/vanilla/jakarta/javax) + `precompute.py` (lane-aware enrichment)
- **단위 테스트**: `tests/` (pytest)
- **누적 트랩 (6)**: explicit-id MERGE 패턴 / `@Mapper` bean 어노테이션 진실원천 / typed seed sentinel / REST snake_case URL / MyBatis Map placeholder case = envelope key case / nexacro `_RowType_` 안전추출
- **미해결 환류**: **G-Jackson** (javax `boot-jdk8-javax` runner Jackson 2.16+ 부재 → `JsonToken.valueDescFor` `NoSuchMethodError`, Growth-33부터 deferred) / **vanilla lane 라이브 검증대 부재** (자체 minimal-servlet runner 미정)
- **Self-check (Growth 종료 시)**: 새 lane/template/precompute 분기가 발생했다면 `business-fullstack-creater/learn-log.md` §0 mybatis 행 + §3 (패턴) 또는 §4 (트랩) 한 줄 환류했는가?
