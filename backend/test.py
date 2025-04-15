from unittest import mock
from unittest.mock import patch, MagicMock, Mock

import pytest
import sqlite3
from flask import json
# from .app import app

import backend.app as main_app
from backend.app import create_app

app = create_app()

# def test_hello_world():
#     assert (app.hello_world() == "<p>Hello, World!</p>")

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def mock_user():
    mock = MagicMock()
    mock.id = 1
    return mock

# @patch('app.create_connection')
# def test_get_product_image(mock_create_call):
#     mock_create_call = MagicMock()
#     connection = Mock()
#     cursor = connection.cursor()
#     mock_create_call.return_value = connection
#     m = mock.MagicMock()
#     m.values = {"productID": "1"}
#     with mock.patch("app.request", m):
#         result = app.get_product_image()
#         # print("result=", result)
#     assert m.values.keys().__contains__("productID")

# @patch('app.create_connection')
# def test_get_product_details(mock_create_call):
#     mock_create_call = MagicMock()
#     connection = Mock()
#     cursor = connection.cursor()
#     mock_create_call.return_value = connection
#     m = mock.MagicMock()
#     m.values = {"productID": "1"}
#     with mock.patch("app.request", m):
#         result = app.get_product_details()
#         # print("result=", result)
#     assert m.values.keys().__contains__("productID")

# @patch('app.create_connection')
# def test_get_all_products(mock_create_call):
#     mock_create_call = MagicMock()
#     connection = Mock()
#     cursor = connection.cursor()
#     mock_create_call.return_value = connection
#     result = app.get_all_products()

# # @patch('app.create_connection')
# # def test_get_all_products(mock_create_call):
# #     mock_create_call = MagicMock()
# #     connection = Mock()
# #     cursor = connection.cursor()
# #     mock_create_call.return_value = connection
# #     result = app.get_all_products()

# @patch('app.create_connection')
# def test_create_product(mock_create_call):
#     mock_create_call = MagicMock()
#     connection = Mock()
#     cursor = connection.cursor()
#     mock_create_call.return_value = connection
#     m = mock.MagicMock()
#     m.values = {"productName": "Ba", "sellerEmail": "n@gmail.com", "initialPrice": 300, "increment": 20, "photo": "", "description": "nice"}
#     with mock.patch("app.request", m):
#         result = app.create_product()
#         #print("result=", result)
#     assert result['result'].__eq__("Added product successfully")

# @patch('app.create_connection')
# def test_update_product(mock_create_call):
#     mock_create_call = MagicMock()
#     connection = Mock()
#     cursor = connection.cursor()
#     mock_create_call.return_value = connection
#     m = mock.MagicMock()
#     m.values = {"productName": "Ba", "sellerEmail": "n@gmail.com", "initialPrice": 300, "increment": 20, "photo": "", "description": "nice"}
#     with mock.patch("app.request", m):
#         result = app.update_product_details()
#         #print("result=", result)
#     assert result['message'].__eq__("Updated product successfully")

# @patch('app.send_message')
# def test_send_message(mock_send_call):
#     mock_send_call = MagicMock()
#     connection = Mock()
#     cursor = connection.cursor()
#     mock_send_call.return_value = connection
#     m = mock.MagicMock()
#     m.values = {"message": "Hello!", "recipient_id": 1, "sender_id": 2, "product_id": 42}
#     with mock.patch("app.request", m):
#         result = app.send_message()
#     assert result['message'].__eq__("Message sent successfully")

# @patch('app.read_message')
# def test_read_message_failure(mock_read_call):
#     mock_read_call = MagicMock()
#     connection = Mock()
#     cursor = connection.cursor()
#     mock_read_call.return_value = connection
#     m = mock.MagicMock()
#     m.values = {"global_id": 123, "product_id": 42}
#     with mock.patch("app.request", m):
#         result = app.read_message()
#     assert result['message'].__eq__("User has not messaged regarding this product.")
    
# @patch('app.read_message')
# def test_read_message_success(mock_read_call):
#     mock_read_call = MagicMock()
#     connection = Mock()
#     cursor = connection.cursor()
#     cursor.execute('''INSERT INTO messages (sender_id, recipient_id, product_id, message) 
#             VALUES (?, ?, ?, ?)''', [123, 122, 42, "this is a message"])
#     connection.commit()
#     mock_read_call.return_value = connection
#     m = mock.MagicMock()
#     m.values = {"global_id": 123, "product_id": 42}
#     with mock.patch("app.request", m):
#         result = app.read_message()
#     assert result['message'].__eq__("Message read successfully")
    
# @patch('app.create_connection')
# def test_create_notif(mock_create_call):
#     mock_create_call = MagicMock()
#     connection = Mock()
#     mock_create_call.return_value = connection
#     m = mock.MagicMock()
#     m.values = {"user_id": "1", "message": "Good Job!", "detail_page": '/profile'}
#     with mock.patch("app.request", m):
#         result = app.create_notification()
#         print("result=", result)
#     assert result['result'].__eq__('Added notification successfully')

# @patch('app.create_connection')
# def test_notification_failure(mock_read_call):
#     mock_read_call = MagicMock()
#     connection = Mock()
#     cursor = connection.cursor()
#     mock_read_call.return_value = connection
#     m = mock.MagicMock()
#     m.values = {"global_id": 123}
#     with mock.patch("app.request", m):
#         result = app.get_user_notifications()
#     assert result['notifications'].__eq__("User has no unread notifications.")
    
# @patch('app.create_connection')
# def test_notification_success(mock_read_call):
#     connection = Mock()
#     cursor = Mock()
#     connection.cursor.return_value = cursor
#     cursor.fetchall.return_value = [
#         (1, "this is a message", "\\profile", "Now")
#     ]
#     mock_read_call.return_value = connection
#     result = app.get_user_notifications()
    
#     m = mock.MagicMock()
#     m.values = {"global_id": 1}
    
#     expected_result = {
#         "notifications": [
#             {
#                 "notif_id": 1,
#                 "image": "../src/assets/logo96.png",
#                 "message": "this is a message",
#                 "detailPage": "\\profile",
#                 "receivedTime": "Now"
#             }
#         ]
#     }
#     print(result)
#     assert result == expected_result
    
# @patch('backend.app.create_connection')
# def test_read_success(mock_read_call):
#     connection = Mock()
#     cursor = Mock()
#     connection.cursor.return_value = cursor
#     cursor.fetchall.return_value = [
#         ("this is a message", "\\profile", "Now")
#     ]
#     mock_read_call.return_value = connection
#     result = app.read_user_notifications(0)
#     expected_result = "Read notification successfully"
#     assert result['result'] == expected_result
    
# @patch('app.create_connection')
# def test_read_all_success(mock_read_call):
#     connection = Mock()
#     cursor = Mock()
#     connection.cursor.return_value = cursor
#     cursor.fetchall.return_value = [
#         ("this is a message", "\\profile", "Now")
#     ]
#     mock_read_call.return_value = connection
#     result = app.read_all_user_notifications()
#     expected_result = "Read all notifications successfully"
#     assert result['result'] == expected_result

    
# @patch('app.create_connection')
# def test_get_bid_success(mock_create_connection):
#     mock_connection = Mock()
#     mock_cursor = Mock()
#     mock_connection.cursor.return_value = mock_cursor
#     mock_cursor.fetchall.return_value = [
#         (1, "user1@example.com", 100, "2025-02-26 09:28:31")
#     ]
#     mock_create_connection.return_value = mock_connection
    
#     with app.app.test_request_context('/bid/get', query_string={'productID': '1'}):
#         response = app.get_bid()
    
#     expected_response = {"result": [[1, "user1@example.com", 100, "2025-02-26 09:28:31"]]}
    
#     assert response.get_json() == expected_response


# @patch('backend.app.delete_product')
# def test_delete_product_success(mock_delete_call):
#     mock_delete_call = MagicMock()
#     connection = Mock()
#     mock_delete_call.return_value = connection
#     m = mock.MagicMock()
#     m.values = {"product_id: 1"}
#     with mock.patch("app.request", m):
#         result = app.delete_product(1)
#         print("result=", result)
#     assert result['result'].__eq__('Added notification successfully')


# For Watchlist endpoints:
# 1. User not logged in
@patch('backend.app.getuserobject', return_value=None)
def test_check_watchlist_not_logged_in(mock_userobj, client):
    response = client.post('/watchlist/check', json={"productID": 1})
    assert response.status_code == 401


# 2. No request data
@patch('backend.app.getuserobject', return_value=mock_user())
def test_check_watchlist_no_data(mock_userobj, client):
    response = client.post('/watchlist/check', json=None)
    assert response.status_code == 500


# 3. Missing product ID
@patch('backend.app.getuserobject', return_value=mock_user())
def test_check_watchlist_missing_product_id(mock_userobj, client):
    response = client.post('/watchlist/check', json={})
    assert response.status_code == 400


# 4. Check Watchlist — Product not in watchlist
@patch('backend.app.getuserobject', return_value=mock_user())
@patch('backend.app.get_db')
def test_check_watchlist_not_found(mock_db, mock_userobj, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.post('/watchlist/check', json={"productID": 123})
    assert response.status_code == 200
    assert response.json["isInWatchlist"] is False


# 5. Check Watchlist — Product in watchlist
@patch('backend.app.getuserobject', return_value=mock_user())
@patch('backend.app.get_db')
def test_check_watchlist_found(mock_db, mock_userobj, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)  # Simulate product found
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.post('/watchlist/check', json={"productID": 1})
    assert response.status_code == 200
    assert response.json["isInWatchlist"] is True

# 6. Add to watchlist — not logged in
@patch('backend.app.getuserobject', return_value=None)
def test_add_to_watchlist_not_logged_in(mock_userobj, client):
    response = client.post('/watchlist/add', json={"productID": 1})
    assert response.status_code == 401


# 7. Add to watchlist — no data
@patch('backend.app.getuserobject', return_value=mock_user())
def test_add_to_watchlist_no_data(mock_userobj, client):
    response = client.post('/watchlist/add', json=None)
    assert response.status_code == 500


# 8. Add to watchlist — missing product ID
@patch('backend.app.getuserobject', return_value=mock_user())
def test_add_to_watchlist_missing_id(mock_userobj, client):
    response = client.post('/watchlist/add', json={"someKey": "value"})
    assert response.status_code == 400


# 9. Add to watchlist — valid
@patch('backend.app.getuserobject', return_value=mock_user())
@patch('backend.app.get_db')
def test_add_to_watchlist_success(mock_db, mock_userobj, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.post('/watchlist/add', json={"productID": 2})
    assert response.status_code == 200
    assert response.json["isInWatchlist"] is True


# 10. Remove from watchlist — valid
@patch('backend.app.getuserobject', return_value=mock_user())
@patch('backend.app.get_db')
def test_remove_from_watchlist_success(mock_db, mock_userobj, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.post('/watchlist/remove', json={"productID": 2})
    assert response.status_code == 200
    assert response.json["isInWatchlist"] is False


# 11. Remove from watchlist — missing product ID
@patch('backend.app.getuserobject', return_value=mock_user())
def test_remove_from_watchlist_missing_id(mock_userobj, client):
    response = client.post('/watchlist/remove', json={"notProductID": 1})
    assert response.status_code == 400


# 12. Get watchlist items — not logged in
@patch('backend.app.getuserobject', return_value=None)
def test_get_watchlist_items_not_logged_in(mock_userobj, client):
    response = client.get('/watchlist/items')
    assert response.status_code == 401


# 13. Get watchlist items — empty
@patch('backend.app.getuserobject', return_value=mock_user())
@patch('backend.app.get_db')
def test_get_watchlist_items_empty(mock_db, mock_userobj, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Empty watchlist fetch
    mock_cursor.execute.return_value.fetchall.return_value = []
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.get('/watchlist/items')
    assert response.status_code == 200
    assert response.json["products"] == []


# 14. Get watchlist users — missing query param
def test_get_watchlist_users_missing_param(client):
    response = client.get('/watchlist/users')
    assert response.status_code == 400
    assert "productId parameter is required" in response.json["error"]


# 15. Get watchlist users — valid
@patch('backend.app.get_db')
def test_get_watchlist_users_success(mock_db, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Fake users returned by DB
    mock_cursor.execute.return_value.fetchall.return_value = [
        (1, 'user1@example.com'),
        (2, 'user2@example.com'),
    ]
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value = mock_conn

    response = client.get('/watchlist/users?productId=1')
    assert response.status_code == 200
    assert len(response.json["users"]) == 2