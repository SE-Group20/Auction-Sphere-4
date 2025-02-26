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
    
@patch('app.create_connection')
def test_create_notif(mock_create_call):
    mock_create_call = MagicMock()
    connection = Mock()
    mock_create_call.return_value = connection
    m = mock.MagicMock()
    m.values = {"user_id": "1", "message": "Good Job!", "detail_page": '/profile'}
    with mock.patch("app.request", m):
        result = app.create_notification()
        print("result=", result)
    assert result['result'].__eq__('Added notification successfully')

@patch('app.create_connection')
def test_notification_failure(mock_read_call):
    mock_read_call = MagicMock()
    connection = Mock()
    cursor = connection.cursor()
    mock_read_call.return_value = connection
    m = mock.MagicMock()
    m.values = {"user_id": 1}
    with mock.patch("app.request", m):
        result = app.get_user_notifications(1)
    assert result['notifications'].__eq__("User has no unread notifications.")
    
@patch('app.create_connection')
def test_notification_success(mock_read_call):
    # Create mock connection and cursor
    connection = Mock()
    cursor = Mock()
    connection.cursor.return_value = cursor
    # Simulate query results
    cursor.fetchall.return_value = [
        (1, "this is a message", "\\profile", "Now")
    ]
    # Mock create_connection to return the mock connection
    mock_read_call.return_value = connection
    # Call the function
    result = app.get_user_notifications(0)
    # Expected result
    expected_result = {
        "notifications": [
            {
                "notif_id": 1,
                "image": "logo96.png",
                "message": "this is a message",
                "detailPage": "\\profile",
                "receivedTime": "Now"
            }
        ]
    }
    # Assertions
    assert result == expected_result
    
@patch('app.create_connection')
def test_read_success(mock_read_call):
    # Create mock connection and cursor
    connection = Mock()
    cursor = Mock()
    connection.cursor.return_value = cursor
    # Simulate query results
    cursor.fetchall.return_value = [
        ("this is a message", "\\profile", "Now")
    ]
    # Mock create_connection to return the mock connection
    mock_read_call.return_value = connection
    # Call the function
    result = app.read_user_notifications(0)
    # Expected result
    expected_result = "Read notification successfully"
    # Assertions
    assert result['result'] == expected_result
    
@patch('app.create_connection')
def test_read_all_success(mock_read_call):
    # Create mock connection and cursor
    connection = Mock()
    cursor = Mock()
    connection.cursor.return_value = cursor
    # Simulate query results
    cursor.fetchall.return_value = [
        ("this is a message", "\\profile", "Now")
    ]
    # Mock create_connection to return the mock connection
    mock_read_call.return_value = connection
    # Call the function
    result = app.read_all_user_notifications(0)
    # Expected result
    expected_result = "Read all notifications successfully"
    # Assertions
    assert result['result'] == expected_result
    