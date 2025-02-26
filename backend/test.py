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

@patch('app.read_message')
def test_read_message_failure(mock_read_call):
    mock_read_call = MagicMock()
    connection = Mock()
    cursor = connection.cursor()
    mock_read_call.return_value = connection
    m = mock.MagicMock()
    m.values = {"global_id": 123, "product_id": 42}
    with mock.patch("app.request", m):
        result = app.read_message()
    assert result['message'].__eq__("User has not messaged regarding this product.")
    
@patch('app.read_message')
def test_read_message_success(mock_read_call):
    mock_read_call = MagicMock()
    connection = Mock()
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO messages (sender_id, recipient_id, product_id, message) 
            VALUES (?, ?, ?, ?)''', [123, 122, 42, "this is a message"])
    connection.commit()
    mock_read_call.return_value = connection
    m = mock.MagicMock()
    m.values = {"global_id": 123, "product_id": 42}
    with mock.patch("app.request", m):
        result = app.read_message()
    assert result['message'].__eq__("Message read successfully")
    
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
    connection = Mock()
    cursor = Mock()
    connection.cursor.return_value = cursor
    cursor.fetchall.return_value = [
        (1, "this is a message", "\\profile", "Now")
    ]
    mock_read_call.return_value = connection
    result = app.get_user_notifications(0)
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
    assert result == expected_result
    
@patch('app.create_connection')
def test_read_success(mock_read_call):
    connection = Mock()
    cursor = Mock()
    connection.cursor.return_value = cursor
    cursor.fetchall.return_value = [
        ("this is a message", "\\profile", "Now")
    ]
    mock_read_call.return_value = connection
    result = app.read_user_notifications(0)
    expected_result = "Read notification successfully"
    assert result['result'] == expected_result
    
@patch('app.create_connection')
def test_read_all_success(mock_read_call):
    connection = Mock()
    cursor = Mock()
    connection.cursor.return_value = cursor
    cursor.fetchall.return_value = [
        ("this is a message", "\\profile", "Now")
    ]
    mock_read_call.return_value = connection
    result = app.read_all_user_notifications(0)
    expected_result = "Read all notifications successfully"
    assert result['result'] == expected_result

@patch('app.delete_product')
def test_delete_product_success(mock_delete_call):
    mock_delete_call = MagicMock()
    connection = Mock()
    mock_delete_call.return_value = connection
    m = mock.MagicMock()
    m.values = {"product_id: 1"}
    with mock.patch("app.request", m):
        result = app.delete_product(1)
        print("result=", result)
    assert result['result'].__eq__('Added notification successfully')

