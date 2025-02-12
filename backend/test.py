from unittest import mock
from unittest.mock import patch, MagicMock, Mock

import app

def test_hello_world():
    assert (app.hello_world() == "<p>Hello, World!</p>")

@patch('app.create_connection')
def test_get_product_image(mock_create_call):
    mock_create_call = MagicMock()
    connection = Mock()
    cursor = connection.cursor()
    mock_create_call.return_value = connection
    m = mock.MagicMock()
    m.values = {"productID": "1"}
    with mock.patch("app.request", m):
        result = app.get_product_image()
        # print("result=", result)
    assert m.values.keys().__contains__("productID")

@patch('app.create_connection')
def test_get_product_details(mock_create_call):
    mock_create_call = MagicMock()
    connection = Mock()
    cursor = connection.cursor()
    mock_create_call.return_value = connection
    m = mock.MagicMock()
    m.values = {"productID": "1"}
    with mock.patch("app.request", m):
        result = app.get_product_details()
        # print("result=", result)
    assert m.values.keys().__contains__("productID")

@patch('app.create_connection')
def test_get_all_products(mock_create_call):
    mock_create_call = MagicMock()
    connection = Mock()
    cursor = connection.cursor()
    mock_create_call.return_value = connection
    result = app.get_all_products()

@patch('app.create_connection')
def test_get_all_products(mock_create_call):
    mock_create_call = MagicMock()
    connection = Mock()
    cursor = connection.cursor()
    mock_create_call.return_value = connection
    result = app.get_all_products()

@patch('app.create_connection')
def test_create_product(mock_create_call):
    mock_create_call = MagicMock()
    connection = Mock()
    cursor = connection.cursor()
    mock_create_call.return_value = connection
    m = mock.MagicMock()
    m.values = {"productName": "Ba", "sellerEmail": "n@gmail.com", "initialPrice": 300, "increment": 20, "photo": "", "description": "nice"}
    with mock.patch("app.request", m):
        result = app.create_product()
        #print("result=", result)
    assert result['result'].__eq__("Added product successfully") 

@patch('app.create_connection')
def test_update_product(mock_create_call):
    mock_create_call = MagicMock()
    connection = Mock()
    cursor = connection.cursor()
    mock_create_call.return_value = connection
    m = mock.MagicMock()
    m.values = {"productName": "Ba", "sellerEmail": "n@gmail.com", "initialPrice": 300, "increment": 20, "photo": "", "description": "nice"}
    with mock.patch("app.request", m):
        result = app.update_product_details()
        #print("result=", result)
    assert result['message'].__eq__("Updated product successfully")

@patch('app.send_message')
def test_send_message(mock_send_call):
    mock_send_call = MagicMock()
    connection = Mock()
    cursor = connection.cursor()
    mock_send_call.return_value = connection
    m = mock.MagicMock()
    m.values = {"message": "Hello!", "recipient_id": 1, "sender_id": 2, "product_id": 42}
    with mock.patch("app.request", m):
        result = app.send_message()
    assert result['message'].__eq__("Message sent successfully")