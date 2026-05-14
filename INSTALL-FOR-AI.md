# Install instructions for AI agents

Goal: install this plugin into Claude Code from a local path.

## Steps

1. Add the marketplace pointing to the repo root:
   ```
   /plugin marketplace add D:\AI\workspace\andrej-karpathy-rdb-mybatis
   ```

2. Install the plugin:
   ```
   /plugin install andrej-karpathy-rdb-mybatis
   ```

3. Verify the slash command appears:
   ```
   /karpathy-rdb-mybatis compile --help
   ```

4. Run on a project that already has Stage 1 + Stage 2 outputs:
   - `wiki/_blueprint.yaml` (Stage 1)
   - `db/migrations/V001__create_schema.sql`, `V002__create_tables.sql`, `V003__create_indexes.sql`, `V004__create_constraints.sql` (Stage 2)
   - optional `db/seed/*.sql`

   Then:
   ```
   /karpathy-rdb-mybatis compile --skip-compile
   ```

5. Check `backend/mybatis-report.md` for validation results.

## Optional javac check

Set `NEXACRO_LIBS_DIR` to a directory containing:
- `nexacro-uiadapter-*.jar`
- `mybatis-spring-*.jar`
- `mybatis-*.jar`
- `spring-context-*.jar`, `spring-tx-*.jar`, `spring-web-*.jar`

Then run without `--skip-compile`.
