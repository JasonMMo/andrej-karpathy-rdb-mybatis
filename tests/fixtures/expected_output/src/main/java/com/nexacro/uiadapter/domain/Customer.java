package com.nexacro.uiadapter.domain;

public class Customer extends NexacroBase {


    private String customerId;

    private String name;

    private String email;

    private String status;

    private String searchCondition;

    private String searchKeyword;

    private String searchUseYn;



    public String getCustomerId() { return customerId; }
    public void setCustomerId(String customerId) { this.customerId = customerId; }


    public String getName() { return name; }
    public void setName(String name) { this.name = name; }


    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }


    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }


    public String getSearchCondition() { return searchCondition; }
    public void setSearchCondition(String searchCondition) { this.searchCondition = searchCondition; }


    public String getSearchKeyword() { return searchKeyword; }
    public void setSearchKeyword(String searchKeyword) { this.searchKeyword = searchKeyword; }


    public String getSearchUseYn() { return searchUseYn; }
    public void setSearchUseYn(String searchUseYn) { this.searchUseYn = searchUseYn; }


}
