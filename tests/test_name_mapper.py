from name_mapper import to_pascal, to_camel, to_upper_snake, to_snake


def test_to_pascal():
    assert to_pascal("customer") == "Customer"
    assert to_pascal("customer_address") == "CustomerAddress"
    assert to_pascal("TB_CUSTOMER") == "TbCustomer"


def test_to_camel():
    assert to_camel("customer_id") == "customerId"
    assert to_camel("status") == "status"


def test_to_upper_snake():
    assert to_upper_snake("customer_id") == "CUSTOMER_ID"
    assert to_upper_snake("customerId") == "CUSTOMER_ID"


def test_to_snake():
    assert to_snake("CustomerId") == "customer_id"
    assert to_snake("CUSTOMER_ID") == "customer_id"
    assert to_snake("customerId") == "customer_id"
