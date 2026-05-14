package com.nexacro.uiadapter.mapper;

import java.util.List;
import java.util.Map;

public interface CustomerMapper {
    List<Map<String, Object>> select_customer_datalist_map(Map<String, String> searchMap);
    void insert_customer_map(Map<String, Object> customer);
    void update_customer_map(Map<String, Object> customer);
    void delete_customer_map(Map<String, Object> customer);
}
