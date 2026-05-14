package com.nexacro.uiadapter.domain;

import com.nexacro.uiadapter.jakarta.core.data.NexacroBase;

public class Address extends NexacroBase {


    private String addressId;

    private String customerId;

    private String line1;

    private String searchCondition;

    private String searchKeyword;

    private String searchUseYn;



    public String getAddressId() { return addressId; }
    public void setAddressId(String addressId) { this.addressId = addressId; }


    public String getCustomerId() { return customerId; }
    public void setCustomerId(String customerId) { this.customerId = customerId; }


    public String getLine1() { return line1; }
    public void setLine1(String line1) { this.line1 = line1; }


    public String getSearchCondition() { return searchCondition; }
    public void setSearchCondition(String searchCondition) { this.searchCondition = searchCondition; }


    public String getSearchKeyword() { return searchKeyword; }
    public void setSearchKeyword(String searchKeyword) { this.searchKeyword = searchKeyword; }


    public String getSearchUseYn() { return searchUseYn; }
    public void setSearchUseYn(String searchUseYn) { this.searchUseYn = searchUseYn; }


}
