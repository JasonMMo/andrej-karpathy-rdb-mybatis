# nexacro uiadapter Spec Summary

References:
- `spring boot 3.0기반-nexacroN-개발자가이드(v0.3).pdf` p.62–74
- GitLab: `nexacron/spring-boot/jakarta/uiadapter-jakarta` `BoardController.java`, `BoardServiceImpl.java`

## Mandatory imports (per layer)
- Controller: `com.nexacro.uiadapter.spring.core.data.{NexacroResult, ParamDataSet}`, `com.nexacro.uiadapter.spring.core.NexacroException`
- ServiceImpl: `com.nexacro.java.xapi.data.DataSet`, `com.nexacro.uiadapter.spring.core.data.DataSetRowTypeAccessor`, `org.mybatis.spring.SqlSessionTemplate`
- Domain: `com.nexacro.uiadapter.spring.core.data.NexacroBase`

## Save dispatch (single endpoint)
```java
int rowType = Integer.parseInt(String.valueOf(row.get(DataSetRowTypeAccessor.NAME)));
if (rowType == DataSet.ROW_TYPE_INSERTED) { mapper.insert_<entity>_map(row); }
else if (rowType == DataSet.ROW_TYPE_UPDATED) { mapper.update_<entity>_map(row); }
else if (rowType == DataSet.ROW_TYPE_DELETED) { mapper.delete_<entity>_map(row); }
```

## Method naming
- Controller method = endpoint segment (snake_case): `select_datalist_map`, `save_datalist_map`
- Service / Mapper methods: `<verb>_<entity>_<suffix>_map` — `select_<entity>_datalist_map`, `insert_<entity>_map`, `update_<entity>_map`, `delete_<entity>_map`, `save_<entity>_datalist_map`

## Mapper XML
- `namespace` = full mapper interface FQCN
- column references = `#{UPPER_SNAKE}` matching DDL column names
- `parameterType="java.util.Map"`, `resultType="java.util.Map"` (search list)
