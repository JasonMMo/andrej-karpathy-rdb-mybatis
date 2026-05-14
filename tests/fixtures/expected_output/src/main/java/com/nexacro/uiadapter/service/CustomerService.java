package com.nexacro.uiadapter.service;

import java.util.List;
import java.util.Map;

public interface CustomerService {
    List<Map<String, Object>> select_customer_datalist_map(Map<String, String> searchMap);
    void save_customer_datalist_map(List<Map<String, Object>> dataList);
}
