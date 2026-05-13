---
name: karpathy-rdb-mybatis
description: Stage 3 — Generate MyBatis + nexacro uiadapter backend from Stage 1/2 artifacts
argument-hint: compile [--blueprint <path>] [--ddl-dir <path>] [--out <path>] [--package <name>] [--skip-compile] [--dry-run]
allowed-tools: Bash, Read, Write, Edit
---

Run the Stage 3 codegen pipeline.

Arguments after `compile`:
- `--blueprint <path>` (default `wiki/_blueprint.yaml`)
- `--ddl-dir <path>` (default `db/migrations`)
- `--out <path>` (default `backend/`)
- `--package <name>` (default `com.nexacro.uiadapter`)
- `--table-prefix <prefix>` (default `TB_`, sanity check only)
- `--skip-compile` to bypass R006 javac
- `--dry-run` to write report only

Execute via:
`python scripts/compile.py $ARGUMENTS`
