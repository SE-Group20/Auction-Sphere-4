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

import pytest  # noqa: E402
from backend.app import app as main_app  # noqa: E402
from backend.app import init_db, get_db  # noqa: E402

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




