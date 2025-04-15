# https://www.digitalocean.com/community/tutorials/unit-test-in-flask
# Import sys module for modifying Python's runtime environment
import sys
# Import os module for interacting with the operating system
import os

# Add the parent directory to sys.path
new_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
new_path = os.path.abspath(os.path.join(new_path, '..'))
print(f"Adding {new_path} to sys.path")
sys.path.append(new_path)

from flask.testing import FlaskClient
import pytest  # noqa: E402
from backend.app import app as main_app  # noqa: E402
from backend.app import init_db, get_db  # noqa: E402

class Helpers:
    """Helper class for test cases."""
    user0_signup_data = {
        'firstName': 'example0_first',
        'lastName': 'example0_last',
        'email': 'example0@example.com',
        'password': 'example0_password',
        'contact': '111-111-1111',
        'emailOptIn': True
    }

@pytest.fixture()
def app():
    """Create a new app instance for testing."""
    app = main_app
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'test.db'
    with app.app_context():
        init_db(get_db())
    yield app

    # remove the test database after the test
    if os.path.exists(app.config['DATABASE']):
        os.remove(app.config['DATABASE'])

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


def test_signup_success(client: FlaskClient):
    """Test the signup functionality."""
    response = client.post('/signup', json=Helpers.user0_signup_data)
    # Check if the response is successful
    assert response.status_code == 200
    assert b'success' in response.data.lower(), "Expected 'success' in response data"


def test_signup_db(client: FlaskClient):
    # ensure that user0 is not in the database
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (Helpers.user0_signup_data['email'],))
        user = cursor.fetchone()
        assert user is None, "User should not exist before signup - make sure tests are cleaned up properly"

    response = client.post('/signup', json=Helpers.user0_signup_data)

    assert response.status_code == 200
    # check the user is in the database
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT first_name FROM users WHERE email=?", (Helpers.user0_signup_data['email'],))
        user = cursor.fetchone()
        assert user is not None, "User should exist after signup"
    