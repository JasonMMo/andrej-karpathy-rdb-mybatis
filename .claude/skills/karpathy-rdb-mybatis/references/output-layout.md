# Output Layout (Stage 3)

Under `--out` (default `backend/`):

```
src/main/java/com/nexacro/uiadapter/
├── controller/<Entity>Controller.java
├── service/<Entity>Service.java
├── service/impl/<Entity>ServiceImpl.java
├── mapper/<Entity>Mapper.java
└── domain/<Entity>.java
src/main/resources/
├── schema.sql
├── data.sql                (if seed present)
└── mybatis/mapper/<Entity>Mapper.xml
mybatis-report.md
```

Stage 3 does NOT touch `pom.xml`, `application.yml`, `Application.java`, or `config/` — those come from `nexacro-fullstack-starter`.
