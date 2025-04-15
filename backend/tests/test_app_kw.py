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

from flask_login import current_user
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

    user1_signup_data = {
        'firstName': 'example1_first',
        'lastName': 'example1_last',
        'email': 'example1@example.com',
        'password': 'example1_password',
        'contact': '222-222-2222',
        'emailOptIn': True
    }

    product0_data = {
        'productName': 'Test Product',
        'initialPrice': 100,
        'increment': 10,
        'photo': 'image_binary_data0',
        'description': 'This is a test product.',
        'biddingTime': 14, # in days
    }

    product1_data = {
        'productName': 'Test Product 2',
        'initialPrice': 200,
        'increment': 20,
        'photo': 'image_binary_data1',
        'description': 'This is a test product 2.',
        'biddingTime': 14, # in days
    }

    @staticmethod
    def loginUser(client: FlaskClient, user_data: dict) -> int:
        """
        Helper function to login a user.
        :param client: Flask test client
        :param user_data: User data dictionary
        :return: Response status code
        """
        response = client.post('/login', json={
            'email': user_data['email'],
            'password': user_data['password']
        })
        return response.status_code
    
    @staticmethod
    def createAndLoginUser(client: FlaskClient, user_data: dict) -> int:
        """
        Helper function to create and login a user.
        :param client: Flask test client
        :param user_data: User data dictionary
        :return: Response status code
        """
        # First signup
        response = client.post('/signup', json=user_data)
        assert response.status_code == 200

        # Login with the same credentials
        return Helpers.loginUser(client, user_data)

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
        db_file=db_path,
        testing = True,
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

def test_signup_duplicate_email(client: FlaskClient):
    """
    Test the signup functionality with a duplicate email.
    """
    # First signup
    response = client.post('/signup', json=Helpers.user0_signup_data)
    assert response.status_code == 200

    # Second signup with the same email
    second_user = Helpers.user1_signup_data.copy()
    second_user['email'] = Helpers.user0_signup_data['email']
    response = client.post('/signup', json=second_user)
    assert response.status_code == 401

    # ensure still only one user in the database
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE email=?", (Helpers.user0_signup_data['email'],))
        count = cursor.fetchone()[0]
        assert count == 1


def test_signup_duplicate_contact(client: FlaskClient):
    """
    Test the signup functionality with a duplicate contact number.
    """
    # First signup
    response = client.post('/signup', json=Helpers.user0_signup_data)
    assert response.status_code == 200

    # Second signup with the same contact number
    second_user = Helpers.user1_signup_data.copy()
    second_user['contact'] = Helpers.user0_signup_data['contact']
    response = client.post('/signup', json=second_user)
    assert response.status_code == 401

    # ensure still only one user in the database
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE contact_number=?", (Helpers.user0_signup_data['contact'],))
        count = cursor.fetchone()[0]
        assert count == 1

def test_signup_multiple_users(client: FlaskClient):
    """
    Test the signup functionality with multiple users.
    """
    # First signup
    response = client.post('/signup', json=Helpers.user0_signup_data)
    assert response.status_code == 200

    # Second signup
    response = client.post('/signup', json=Helpers.user1_signup_data)
    assert response.status_code == 200

    # Check if both users exist in the database
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (Helpers.user0_signup_data['email'],))
        user0 = cursor.fetchone()
        cursor.execute("SELECT * FROM users WHERE email=?", (Helpers.user1_signup_data['email'],))
        user1 = cursor.fetchone()
        assert user0 is not None, "User0 should exist after signup"
        assert user1 is not None, "User1 should exist after signup"


def test_login_success(client: FlaskClient):
    """
    Test the login functionality.
    """
    # First signup
    response = client.post('/signup', json=Helpers.user0_signup_data)
    assert response.status_code == 200

    # Login with the same credentials
    response = client.post('/login', json={
        'email': Helpers.user0_signup_data['email'],
        'password': Helpers.user0_signup_data['password']
    })
    assert response.status_code == 200
    assert b'success' in response.data.lower()


def test_login_badpassword(client: FlaskClient):
    """
    Test the login functionality with a bad password.
    """
    # First signup
    response = client.post('/signup', json=Helpers.user0_signup_data)
    assert response.status_code == 200

    # Login with the same email but wrong password
    wrong_password = Helpers.user0_signup_data['password'] + 'wrong'
    response = client.post('/login', json={
        'email': Helpers.user0_signup_data['email'],
        'password': wrong_password
    })
    assert response.status_code == 401
    assert b'invalid' in response.data.lower()

def test_login_bademail(client: FlaskClient):
    """
    Test the login functionality with a bad email.
    """
    # First signup
    response = client.post('/signup', json=Helpers.user0_signup_data)
    assert response.status_code == 200

    # Login with a wrong email
    wrong_email = Helpers.user0_signup_data['email'] + 'wrong'
    response = client.post('/login', json={
        'email': wrong_email,
        'password': Helpers.user0_signup_data['password']
    })
    assert response.status_code == 401
    assert b'invalid' in response.data.lower()

def test_profile(client: FlaskClient):
    """
    Test the profile functionality.
    """
    # First signup
    response = client.post('/signup', json=Helpers.user0_signup_data)
    assert response.status_code == 200

    # Login with the same credentials
    response = client.post('/login', json={
        'email': Helpers.user0_signup_data['email'],
        'password': Helpers.user0_signup_data['password']
    })
    assert response.status_code == 200
    assert b'success' in response.data.lower()

    # Get profile data
    response = client.get('/profile')
    assert response.status_code == 200
    assert Helpers.user0_signup_data['firstName'] in response.data.decode()
    assert Helpers.user0_signup_data['lastName'] in response.data.decode()
    

def test_profile_not_logged_in(client: FlaskClient):
    """
    Test the profile functionality when not logged in.
    """
    # Get profile data
    response = client.get('/profile')
    assert response.status_code == 401
    assert b'not logged in' in response.data.lower()


def test_create_product(client: FlaskClient, app):
    """
    Test the create product functionality.
    """
    # First signup
    response = client.post('/signup', json=Helpers.user0_signup_data)
    assert response.status_code == 200

    # Login with the same credentials
    response = client.post('/login', json={
        'email': Helpers.user0_signup_data['email'],
        'password': Helpers.user0_signup_data['password']
    })
    assert response.status_code == 200
    assert b'success' in response.data.lower()

    # Create a product
    product_data = {
        'productName': 'Test Product',
        'initialPrice': 100,
        'increment': 10,
        'photo': '',
        'description': 'This is a test product.',
        'biddingTime': 14, # in days
    }
    response = client.post('/product/create', json=product_data)
    assert response.status_code == 200

    # Check if the product is created in the database
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT name, seller_id FROM product WHERE name=?", (product_data['productName'],))
        product = cursor.fetchone()
        assert product is not None, "Product should exist after creation"
        assert product[0] == product_data['productName'], "Product name should match"
        user = current_user
        assert product[1] == user.id, "Product seller_id should match the logged in user"


def test_product_appears_in_profile(client: FlaskClient):
    """
    Test that the product appears in the profile after creation.
    """
    # First signup
    response = client.post('/signup', json=Helpers.user0_signup_data)
    assert response.status_code == 200

    # Login with the same credentials
    response = client.post('/login', json={
        'email': Helpers.user0_signup_data['email'],
        'password': Helpers.user0_signup_data['password']
    })
    assert response.status_code == 200
    assert b'success' in response.data.lower()

    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # Get profile data
    response = client.get('/profile')
    assert response.status_code == 200
    assert Helpers.product0_data['productName'] in response.data.decode()


def test_user_bid(client: FlaskClient, app):
    # First signup
    response = client.post('/signup', json=Helpers.user0_signup_data)
    assert response.status_code == 200

    # Login with the same credentials
    response = client.post('/login', json={
        'email': Helpers.user0_signup_data['email'],
        'password': Helpers.user0_signup_data['password']
    })
    assert response.status_code == 200

    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # Get the product ID
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    # reset the client
    client = app.test_client()

    # User 1 signup
    response = client.post('/signup', json=Helpers.user1_signup_data)
    assert response.status_code == 200

    # User 1 login
    response = client.post('/login', json={
        'email': Helpers.user1_signup_data['email'],
        'password': Helpers.user1_signup_data['password']
    })
    assert response.status_code == 200

    # User 1 bids on the product
    bid_data = {
        'prodId': product_id,
        'bidAmount': Helpers.product0_data['initialPrice'] + Helpers.product0_data['increment']
    }
    response = client.post('/bid/create', json=bid_data)
    assert response.status_code == 200


def test_profile_bid_shown(client: FlaskClient, app):
    # First signup
    response = client.post('/signup', json=Helpers.user0_signup_data)
    assert response.status_code == 200

    # Login with the same credentials
    response = client.post('/login', json={
        'email': Helpers.user0_signup_data['email'],
        'password': Helpers.user0_signup_data['password']
    })
    assert response.status_code == 200

    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # Get the product ID
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    # reset the client
    user1client = app.test_client()
    with user1client.application.app_context():
        # User 1 signup
        response = user1client.post('/signup', json=Helpers.user1_signup_data)
        assert response.status_code == 200

        # User 1 login
        response = user1client.post('/login', json={
            'email': Helpers.user1_signup_data['email'],
            'password': Helpers.user1_signup_data['password']
        })
        assert response.status_code == 200

        # User 1 bids on the product
        bid_data = {
            'prodId': product_id,
            'bidAmount': Helpers.product0_data['initialPrice'] + Helpers.product0_data['increment']
        }
        response = user1client.post('/bid/create', json=bid_data)
        assert response.status_code == 200

        # User 1 gets their profile
        response = user1client.get('/profile')
        assert response.status_code == 200
        # print("user 1 profile data:", response.data.decode())
        response_json = response.get_json()
        assert response_json['no_bids'] == 1
        assert response_json['first_name'] == Helpers.user1_signup_data['firstName']

    # user 0 gets their profile
    response = client.get('/profile')
    assert response.status_code == 200
    # print("user 0 profile data:", response.data.decode())
    response_json = response.get_json()
    assert response_json['maximum_bids'][0] == Helpers.product0_data["initialPrice"] + Helpers.product0_data["increment"]
    assert response_json['first_name'] == Helpers.user0_signup_data['firstName']

def test_profile_product_nobids(client: FlaskClient, app):
    # First signup
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200

    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # Get the product ID
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    # Get profile data
    response = client.get('/profile')
    assert response.status_code == 200
    # print("user 0 profile data:", response.data.decode())
    response_json = response.get_json()
    assert response_json['no_bids'] == 0
    assert response_json['names'][0] == 'N/A'


def test_bid_not_logged_in(client: FlaskClient, app):
    """
    Test the bid functionality when not logged in.
    """
    # create a user and sign in
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200
    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # get the product ID
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    client2 = app.test_client(use_cookies=False)
    with client2.application.app_context():
        # try to bid
        bid_data = {
            'prodId': product_id,
            'bidAmount': Helpers.product0_data['initialPrice'] + Helpers.product0_data['increment']
        }
        response = client2.post('/bid/create', json=bid_data)
        assert response.status_code == 401


def test_bid_less_than_initial(client: FlaskClient, app):
    """
    Test the bid functionality with a bid less than the initial price.
    """
    # First signup
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200

    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # get the product ID
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"


    client2 = app.test_client()
    with client2.application.app_context():
        # User 1 signup
        assert Helpers.createAndLoginUser(client2, Helpers.user1_signup_data) == 200

        # User 1 bids on the product with a bid less than the initial price
        bid_data = {
            'prodId': product_id,
            'bidAmount': Helpers.product0_data['initialPrice'] - 10
        }
        response = client2.post('/bid/create', json=bid_data)
        assert response.status_code == 200
        assert b'less than initial price' in response.data.lower()


def test_get_bids(client: FlaskClient, app):
    """
    Test the get bids functionality.
    """
    # First signup
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200

    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # get the product ID
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    # User 1 signup
    client2 = app.test_client()
    assert Helpers.createAndLoginUser(client2, Helpers.user1_signup_data) == 200

    # User 1 bids on the product
    bid_data = {
        'prodId': product_id,
        'bidAmount': Helpers.product0_data['initialPrice'] + Helpers.product0_data['increment']
    }
    with client2.application.app_context():
        # User 1 bids on the product
        response = client2.post('/bid/create', json=bid_data)
        assert response.status_code == 200

    # Get bids for the product
    response = client.get('bid/get', query_string={'prodId': product_id})
    assert response.status_code == 200
    # TODO: verify response data


def test_get_all_products(client: FlaskClient, app):
    """
    Test the get all products functionality.
    """
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200
    # Create both products
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200
    response = client.post('/product/create', json=Helpers.product1_data)
    assert response.status_code == 200

    # Get all products
    response = client.get('/product/listAll')
    assert response.status_code == 200
    response_json = response.get_json()
    assert len(response_json["result"]) == 2


def test_get_product_image(client: FlaskClient, app):
    """
    Test the get product image functionality.
    """
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200
    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # get the product ID
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    # Get the product image
    response = client.post('/product/getImage', json={
        'productID': product_id
    })
    assert response.status_code == 200
    response_json = response.get_json()
    assert len(response_json['result']) == 1
    assert response_json['result'][0][0] == Helpers.product0_data['photo']


def test_product_getowner(client: FlaskClient, app):
    """
    Test the get product owner functionality.
    """
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200
    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # get the product ID
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    # Get the product owner
    response = client.post('/getOwner', json={
        'productID': product_id
    })
    assert response.status_code == 200
    response_json = response.get_json()
    assert len(response_json['result']) == 1
    assert response_json['result'][0][0] == Helpers.user0_signup_data['email']


def test_product_getdetails(client: FlaskClient, app):
    """
    Test the get product details functionality.
    """
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200
    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # get the product ID
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    # Get the product details
    response = client.post('/product/getDetails', json={
        'productID': product_id
    })
    assert response.status_code == 200
    response_json = response.get_json()
    response_prod = response_json['product']
    assert response_prod['prod_id'] == product_id
    assert response_prod['name'] == Helpers.product0_data['productName']
    assert response_prod['seller_email'] == Helpers.user0_signup_data['email']
    assert response_prod['initial_price'] == Helpers.product0_data['initialPrice']
    assert response_prod['increment'] == Helpers.product0_data['increment']
    assert response_prod['description'] == Helpers.product0_data['description']

def test_product_getname(client: FlaskClient, app):
    """
    Test the get product name functionality.
    """
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200
    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # get the product ID
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    # Get the product name
    # this one uses query_string instead, for some reason
    response = client.get('/getName', query_string={
        'productID': product_id
    })
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['result'] == Helpers.product0_data['productName']

def test_product_delete(client: FlaskClient, app):
    """
    Test the delete product functionality.
    """
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200
    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # get the product ID
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    # Delete the product
    response = client.delete('/product/' + str(product_id))
    assert response.status_code == 200

    # Check if the product is deleted from the database
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM product WHERE prod_id=?", (product_id,))
        product = cursor.fetchone()
        assert product is None

# known to fail
@pytest.mark.skip(reason="Not implemented yet")
def test_product_delete_not_logged_in(client: FlaskClient, app):
    """
    Test the delete product functionality when not logged in.
    """
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200
    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # get the product ID
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    # reset the client
    client2 = app.test_client()
    with client2.application.app_context():
        # Delete the product
        response = client2.delete('/product/' + str(product_id))
        assert response.status_code == 401


@pytest.mark.skip(reason="Not implemented yet")
def test_product_delete_not_owner(client: FlaskClient, app):
    """
    Test the delete product functionality when not the owner.
    """
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200
    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # get the product ID
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    # reset the client
    client2 = app.test_client()
    with client2.application.app_context():
        # User 1 signup
        assert Helpers.createAndLoginUser(client2, Helpers.user1_signup_data) == 200

        # Delete the product
        response = client2.delete('/product/' + str(product_id))
        assert response.status_code == 401
        assert b'not the owner' in response.data.lower()

def test_product_update(client: FlaskClient, app):
    """
    Test the update product functionality.
    """
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200
    # Create a product
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200

    # get the product ID
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    # Update the product
    updated_product_data = {
        'productName': 'Updated Product',
        'productID': product_id,
        'initialPrice': 150,
        'increment': 15,
        'description': 'This is an updated test product.',
        'deadlineDate': '2023-12-31',
    }
    response = client.post('/product/update', json=updated_product_data)
    assert response.status_code == 200

    # Check if the product is updated in the database
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM product WHERE prod_id=?", (product_id,))
        product = cursor.fetchone()
        assert product is not None
        assert product[1] == updated_product_data['productName']


def test_get_latest_products(client: FlaskClient, app):
    """
    Test the get latest products functionality.
    """
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200
    # Create both products
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200
    response = client.post('/product/create', json=Helpers.product1_data)
    assert response.status_code == 200

    # get id of the first product
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    client2 = app.test_client()
    # bid on the first product
    with client2.application.app_context():
        # User 1 signup
        assert Helpers.createAndLoginUser(client2, Helpers.user1_signup_data) == 200

        # User 1 bids on the product
        bid_data = {
            'prodId': product_id,
            'bidAmount': Helpers.product0_data['initialPrice'] + Helpers.product0_data['increment']
        }
        response = client2.post('/bid/create', json=bid_data)
        assert response.status_code == 200


    # Get latest products
    response = client.get('/getLatestProducts')
    assert response.status_code == 200
    response_json = response.get_json()
    assert len(response_json) == 3
    assert "products" in response_json.keys()
    assert "maximumBids" in response_json.keys()
    assert "names" in response_json.keys()


def test_top_products(client: FlaskClient, app):
    """
    Test the get top products functionality.
    """
    assert Helpers.createAndLoginUser(client, Helpers.user0_signup_data) == 200
    # Create both products
    response = client.post('/product/create', json=Helpers.product0_data)
    assert response.status_code == 200
    response = client.post('/product/create', json=Helpers.product1_data)
    assert response.status_code == 200

    # get id of the first product
    with client.application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT prod_id FROM product WHERE name=?", (Helpers.product0_data['productName'],))
        product_id = cursor.fetchone()[0]
        assert product_id is not None, "Product ID should not be None"

    client2 = app.test_client()
    # bid on the first product
    with client2.application.app_context():
        # User 1 signup
        assert Helpers.createAndLoginUser(client2, Helpers.user1_signup_data) == 200

        # User 1 bids on the product
        bid_data = {
            'prodId': product_id,
            'bidAmount': Helpers.product0_data['initialPrice'] + Helpers.product0_data['increment']
        }
        response = client2.post('/bid/create', json=bid_data)
        assert response.status_code == 200

    # Get top products
    response = client.get('/getTopTenProducts')
    assert response.status_code == 200
    response_json = response.get_json()
    assert "products" in response_json.keys()
    assert len(response_json["products"]) == 2


