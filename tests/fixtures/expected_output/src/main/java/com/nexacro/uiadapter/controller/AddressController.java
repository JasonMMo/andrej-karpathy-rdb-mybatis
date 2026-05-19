package com.nexacro.uiadapter.controller;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

import com.nexacro.uiadapter.jakarta.core.data.NexacroResult;
import com.nexacro.uiadapter.jakarta.core.annotation.ParamDataSet;
import com.nexacro.uiadapter.jakarta.core.NexacroException;
import com.nexacro.uiadapter.service.AddressService;

@Controller
public class AddressController {

    @Autowired
    private AddressService addressService;

    @RequestMapping(value = "/address/select_datalist_map.do")
    public NexacroResult select_datalist_map(
            @ParamDataSet(name = "dsSearch", required = false) Map<String, String> searchMap)
            throws NexacroException {
        List<Map<String, Object>> list = addressService.select_address_datalist_map(searchMap);
        NexacroResult result = new NexacroResult();
        result.addDataSet("output1", list);
        return result;
    }

    @RequestMapping(value = "/address/save_datalist_map.do")
    public NexacroResult save_datalist_map(
            @ParamDataSet(name = "dataList") List<Map<String, Object>> dataList)
            throws NexacroException {
        addressService.save_address_datalist_map(dataList);
        return new NexacroResult();
    }
}
