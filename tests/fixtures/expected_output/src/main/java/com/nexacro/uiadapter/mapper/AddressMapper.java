package com.nexacro.uiadapter.mapper;

import java.util.List;
import java.util.Map;

public interface AddressMapper {
    List<Map<String, Object>> select_address_datalist_map(Map<String, String> searchMap);
    void insert_address_map(Map<String, Object> address);
    void update_address_map(Map<String, Object> address);
    void delete_address_map(Map<String, Object> address);
}
