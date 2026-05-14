package com.nexacro.uiadapter.service.impl;

import java.util.List;
import java.util.Map;

import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.nexacro.java.xapi.data.DataSet;
import com.nexacro.uiadapter.jakarta.core.data.DataSetRowTypeAccessor;
import com.nexacro.uiadapter.mapper.CustomerMapper;
import com.nexacro.uiadapter.service.CustomerService;

@Service("customerService")
public class CustomerServiceImpl implements CustomerService {

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
        CustomerMapper mapper = sqlSession.getMapper(CustomerMapper.class);
        for (Map<String, Object> row : dataList) {
            int rowType = Integer.parseInt(String.valueOf(row.get(DataSetRowTypeAccessor.NAME)));

            if (rowType == DataSet.ROW_TYPE_INSERTED) {
                mapper.insert_customer_map(row);
            }

            else if (rowType == DataSet.ROW_TYPE_UPDATED) {
                mapper.update_customer_map(row);
            }

            else if (rowType == DataSet.ROW_TYPE_DELETED) {
                mapper.delete_customer_map(row);
            }

        }
    }
}
