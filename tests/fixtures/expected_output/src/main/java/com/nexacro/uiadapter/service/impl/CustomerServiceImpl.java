package com.nexacro.uiadapter.service.impl;

import java.util.List;
import java.util.Map;

import org.mybatis.spring.SqlSessionTemplate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.nexacro.java.xapi.data.DataSet;
import com.nexacro.uiadapter.jakarta.core.data.DataSetRowTypeAccessor;
import com.nexacro.uiadapter.mapper.CustomerMapper;
import com.nexacro.uiadapter.service.CustomerService;

@Service("customerService")
public class CustomerServiceImpl implements CustomerService {

    private static final Logger log = LoggerFactory.getLogger(CustomerServiceImpl.class);

    @Autowired
    private SqlSessionTemplate sqlSession;

    @Override
    @Transactional(readOnly = true)
    public List<Map<String, Object>> select_customer_datalist_map(Map<String, String> searchMap) {
        CustomerMapper mapper = sqlSession.getMapper(CustomerMapper.class);
        return mapper.select_customer_datalist_map(searchMap);
    }

    @Override
    @Transactional
    public void save_customer_datalist_map(List<Map<String, Object>> dataList) {
        log.debug("save_customer_datalist_map entered: dataList={}", dataList);
        if (dataList == null || dataList.isEmpty()) {
            log.warn("save_customer_datalist_map: empty dataList, skipping");
            return;
        }
        CustomerMapper mapper = sqlSession.getMapper(CustomerMapper.class);
        for (Map<String, Object> row : dataList) {
            int rowType = resolveRowType(row);

            if (rowType == DataSet.ROW_TYPE_INSERTED) {
                mapper.insert_customer_map(row);
            }

            else if (rowType == DataSet.ROW_TYPE_UPDATED) {
                mapper.update_customer_map(row);
            }

            else if (rowType == DataSet.ROW_TYPE_DELETED) {
                mapper.delete_customer_map(row);
            }

            else {
                log.warn("save_customer_datalist_map: unrecognised rowType={} row={}", rowType, row);
            }
        }
    }

    /**
     * Resolve the nexacro DataSet row-state flag from a Map-mode payload.
     *
     * <p>Accepts every wire form observed across xapi versions:
     * <ul>
     *   <li>Integer value under {@link DataSetRowTypeAccessor#NAME} ("DataSetRowType")
     *       — set by the converter when the target implements
     *       {@link DataSetRowTypeAccessor}; absent for raw {@code Map}.</li>
     *   <li>String single-char {@code _RowType_} value ({@code I}/{@code U}/{@code D}/{@code N}/{@code O})
     *       — canonical XML/JSON/SSV wire encoding per nexacro data-formats spec.</li>
     *   <li>Numeric string under either key — defensive against converter variance.</li>
     * </ul>
     * Returns {@link DataSet#ROW_TYPE_NORMAL} when unresolved so the caller's dispatch
     * skips the row without throwing.
     */
    private static int resolveRowType(Map<String, Object> row) {
        Object v = row.get(DataSetRowTypeAccessor.NAME);
        if (v == null) {
            v = row.get("_RowType_");
        }
        if (v instanceof Integer) {
            return (Integer) v;
        }
        if (v == null) {
            return DataSet.ROW_TYPE_NORMAL;
        }
        String s = v.toString().trim();
        if (s.isEmpty()) {
            return DataSet.ROW_TYPE_NORMAL;
        }
        char c = Character.toUpperCase(s.charAt(0));
        switch (c) {
            case 'I': return DataSet.ROW_TYPE_INSERTED;
            case 'U': return DataSet.ROW_TYPE_UPDATED;
            case 'D': return DataSet.ROW_TYPE_DELETED;
            case 'N': return DataSet.ROW_TYPE_NORMAL;
            default:
                try { return Integer.parseInt(s); } catch (NumberFormatException ignore) { return DataSet.ROW_TYPE_NORMAL; }
        }
    }
}
