package com.nexacro.uiadapter.service.impl;

import java.util.List;
import java.util.Map;

import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.nexacro.java.xapi.data.DataSet;
import com.nexacro.uiadapter.jakarta.core.data.DataSetRowTypeAccessor;
import com.nexacro.uiadapter.mapper.AddressMapper;
import com.nexacro.uiadapter.service.AddressService;

@Service("addressService")
public class AddressServiceImpl implements AddressService {

    @Autowired
    private SqlSessionTemplate sqlSession;

    @Override
    @Transactional(readOnly = true)
    public List<Map<String, Object>> select_address_datalist_map(Map<String, String> searchMap) {
        AddressMapper mapper = sqlSession.getMapper(AddressMapper.class);
        return mapper.select_address_datalist_map(searchMap);
    }

    @Override
    @Transactional
    public void save_address_datalist_map(List<Map<String, Object>> dataList) {
        AddressMapper mapper = sqlSession.getMapper(AddressMapper.class);
        for (Map<String, Object> row : dataList) {
            int rowType = Integer.parseInt(String.valueOf(row.get(DataSetRowTypeAccessor.NAME)));

            if (rowType == DataSet.ROW_TYPE_INSERTED) {
                mapper.insert_address_map(row);
            }

            else if (rowType == DataSet.ROW_TYPE_UPDATED) {
                mapper.update_address_map(row);
            }

            else if (rowType == DataSet.ROW_TYPE_DELETED) {
                mapper.delete_address_map(row);
            }

        }
    }
}
