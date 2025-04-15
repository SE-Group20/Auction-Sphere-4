# Import os module for interacting with the operating system
import os
import shutil

from flask.testing import FlaskClient

# https://www.digitalocean.com/community/tutorials/unit-test-in-flask
# Import sys module for modifying Python's runtime environment
import sys
import tempfile

# Add the parent directory to sys.path
new_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
new_path = os.path.abspath(os.path.join(new_path, '..'))
print(f"Adding {new_path} to sys.path")
sys.path.append(new_path)

import pytest  # noqa: E402

from backend.app import create_app, get_db  # noqa: E402


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
    # create a temporary folder
    tmp_folder = tempfile.mkdtemp()
    app_key_path = os.path.join(tmp_folder, 'app_key')
    db_path = os.path.join(tmp_folder, 'test.db')
    # create a dummy notification file
    notification_cfg_contents = """
SMTP_USERNAME = ""
SMTP_PASSWORD = ""
SMTP_SERVER = ""
    """
    notification_cfg_path = os.path.join(tmp_folder, 'notifications.toml')
    with open(notification_cfg_path, 'w') as f:
        f.write(notification_cfg_contents)
    app = create_app(
        app_key_path=app_key_path,
        notify_config_file=notification_cfg_path,
        db_file=db_path
    )
    app.config['TESTING'] = True
    yield app

    # remove the temporary folder after the test
    shutil.rmtree(tmp_folder)


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
    
def test_secret_key_read(app):
    """
    ensure that ./app_key is loaded
    """
    # check that the app_key is loaded from the file
    with open('./app_key', 'r') as f:
        app_key = f.read().strip()
    assert app_key == app.secret_key

def test_secret_key_generated():
    """
    ensure that the secret key is generated if it does not exist
    """
    # restart the app
    new_app = create_app()
    app_key = new_app.secret_key
    # check that the file was created
    assert os.path.exists('./app_key')
    # check that the file contains the key
    with open('./app_key', 'r') as f:
        file_key = f.read().strip()
    assert file_key == app_key

