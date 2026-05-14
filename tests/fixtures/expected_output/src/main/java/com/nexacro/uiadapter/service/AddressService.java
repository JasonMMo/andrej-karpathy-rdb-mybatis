package com.nexacro.uiadapter.service;

import java.util.List;
import java.util.Map;

public interface AddressService {
    List<Map<String, Object>> select_address_datalist_map(Map<String, String> searchMap);
    void save_address_datalist_map(List<Map<String, Object>> dataList);
}
