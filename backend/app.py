import os
import sqlite3
import tomllib
from datetime import datetime, timedelta
from sqlite3 import Error

# from notification import NotificationService
# https://flask-login.readthedocs.io/en/latest/
import flask_login
from flask import Blueprint, Flask, current_app, g, has_app_context, jsonify, request
from flask_cors import CORS
from .user import MaybeUser, User

from .services.chat import ChatService
from .notification import send_email_notification
    
chatService = ChatService()

login_manager = flask_login.LoginManager()

create_users_table = """CREATE TABLE IF NOT EXISTS users( 
    user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    first_name TEXT NOT NULL, 
    last_name TEXT NOT NULL, 
    contact_number TEXT NOT NULL UNIQUE, 
    email TEXT UNIQUE, 
    password TEXT NOT NULL,
    email_opt_in INT NOT NULL);"""

# TODO(kurt): normalize database - don't keep seller_id and seller_email as separate fields
# use a foreign key to reference the user table instead

# TODO: declare the column names as constants
create_product_table = """CREATE TABLE IF NOT EXISTS product(prod_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL, photo TEXT, 
    seller_id INTEGER NOT NULL,
    seller_email TEXT NOT NULL,
    initial_price REAL NOT NULL,
    date TIMESTAMP NOT NULL,
    increment REAL,
    deadline_date TIMESTAMP NOT NULL,
    description TEXT,
    FOREIGN KEY(seller_email) references users(email),
    FOREIGN KEY(seller_id) references users(user_id));"""

create_bids_table = """CREATE TABLE IF NOT EXISTS bids(prod_id INTEGER, email TEXT NOT NULL , bid_amount REAL NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY(email) references users(email), FOREIGN KEY(prod_id) references product(prod_id), PRIMARY KEY(prod_id, email));"""

create_table_claims = """CREATE TABLE IF NOT EXISTS claims(prod_id INTEGER, email TEXT NOT NULL, expiry_date TEXT NOT NULL, claim_status INTEGER, FOREIGN KEY(email) references users(email), FOREIGN KEY(prod_id) references product(prod_id));"""

create_message_table = """CREATE TABLE IF NOT EXISTS messages(
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    recipient_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    time_sent DATETIME DEFAULT CURRENT_TIMESTAMP,
    read BOOLEAN DEFAULT 0,
    FOREIGN KEY (message_id) REFERENCES users (user_id)
    FOREIGN KEY (sender_id) REFERENCES users (user_id)
    FOREIGN KEY (product_id) REFERENCES product (prod_id)
)"""


create_notification_table = """CREATE TABLE IF NOT EXISTS notifications(
    notif_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEST NOT NULL,
    detail_page TEST NOT NULL,
    time_sent DATETIME DEFAULT CURRENT_TIMESTAMP,
    read BOOLEAN DEFAULT 0
    
    )"""

create_watchlist_table = """CREATE TABLE IF NOT EXISTS watchlist(
    watchlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (product_id) REFERENCES products(prod_id),
    UNIQUE(user_id, product_id)
)"""


def create_table(conn:sqlite3.Connection, create_table_sql:str):
    try:
        c = conn.cursor()
        _ = c.execute(create_table_sql)
        conn.commit()
    except Error as e:
        print(e)

def init_db(conn):
    if conn is not None:
        create_table(conn, create_users_table)
        create_table(conn, create_product_table)
        create_table(conn, create_bids_table)
        create_table(conn, create_table_claims)

        create_table(conn, create_message_table)
        create_table(conn, create_notification_table)
        create_table(conn, create_watchlist_table)
        conn.commit()

        conn.close()
    else:
        print("Error! Cannot create the database connection")

def get_db(db_file=None) -> sqlite3.Connection:
    """
    Get a database connection
    param db_file: the database file to use - only needs to be set outside of the app context
    """
    if has_app_context() and db_file is not None:
        raise ValueError("db_file should not be set when inside the app context")
    # this may be called outside of the app context, so
    if has_app_context():
        db:sqlite3.Connection|None = getattr(g, '_database', None)
    else:
        db:sqlite3.Connection|None = None
    if db is None:
        if db_file is None:
            database_file = current_app.config['DATABASE']
        else:
            database_file = db_file
        db = sqlite3.connect(database_file)
        if has_app_context():
            g._database = db
    return db
    


def getuserobject() -> User|None:
    maybe_current_user: MaybeUser = flask_login.current_user
    if not maybe_current_user or maybe_current_user.is_authenticated is False:
        return None
    # must be a user - safe to cast
    current_user: User = maybe_current_user # pyright:ignore[reportAssignmentType]
    return current_user

app_functions = Blueprint("app_functions", __name__)
@app_functions.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


"""
API end point for user creation.
It extracts firstName, lastName, email, contact number and password from the json.
This further checks if the email provided is already there in the database or not.
If the account is already created, the API returns (An account with this contact already exists)
otherwise, a new user is created in the users table with all the details extracted from json.
"""


@app_functions.route("/signup", methods=["POST"])
def signup():
    firstName:str = request.get_json()['firstName']
    lastName:str = request.get_json()['lastName']
    email:str = request.get_json()['email']
    contact:str = request.get_json()['contact']
    password:str = request.get_json()['password']
    email_opt_in:bool = request.get_json().get('emailOptIn', False)

    user_obj = User(None, email, password, firstName, lastName, contact, email_opt_in)

    conn = get_db()

    success, message = user_obj.try_signup(conn)

    response = {}
    if success:
        response["message"] = "Account created successfully"
        return jsonify(response)
    else:
        response["message"] = message
        return jsonify(response), 401
        


"""
API end point for user login.
User email and password are extracted from the json.
These are validated from the data already available in users table.
If the email and password are correct, login is successful else user is asked to create an account.
"""


@app_functions.route("/login", methods=["POST"])
def login():
    email:str = request.get_json()['email']
    password:str = request.get_json()['password']

    conn = get_db()

    result:User|None = User.try_login(conn, email, password)
    response = {}
    # print("Result:", result)

    if result:
        # we found a user in the db
        login_result = flask_login.login_user(result) # pyright:ignore[reportUnknownMemberType]
        if login_result:
            response["message"] = "Logged in successfully"
            return jsonify(response)

    response["message"] = "Invalid credentials"
    return jsonify(response), 401


""" 
API end point for user profile.
User email is set in the login function which is used here to pull the user stats.
Page includes information entered by the user i.e first name, last name, contact number and email.
It also displays the specific product cards for the user. 
It shows the products the user has put for sale and the products for which the user has submitted a bid.
"""


@app_functions.route('/profile', methods=["GET"])
def profile():
    current_user = getuserobject()
    if current_user is None:
        return jsonify({"message": "User not logged in"}), 401
    # create db connection
    conn = get_db()
    c = conn.cursor()

    # number of bids made by this user
    result = c.execute('SELECT COUNT(*) FROM bids WHERE email=?;', (current_user.email,))
    result_bid_count = list(result.fetchall())

    # up to 10 products listed by this user
    result = c.execute('SELECT prod_id, name, seller_email, initial_price, date, increment, deadline_date, description FROM product WHERE seller_email=? ORDER BY date DESC LIMIT 10;', (current_user.email,))
    products:list[tuple[str,...]] = list(result.fetchall())
    highestBids:list[int] = []
    names:list[str] = []

    # get the highest bid for each product
    # TODO: potentially slow - could be combined into a single query
    for product in products:
        result = c.execute("SELECT email, MAX(bid_amount) FROM bids WHERE prod_id=?;", (product[0],))
        result_bids:list[tuple[str|None, str]] = list(result.fetchall())

        # TODO: can this ever be none?
        if (result_bids[0][0] is not None):
            result_bids_row = result_bids[0]
            highestBids.append(int(result_bids_row[1]))

            result = c.execute("SELECT first_name, last_name FROM users WHERE email=?;", (result_bids_row[0],))
            bidder_name:list[tuple[str, str]] = list(result.fetchall())
            name_combined = bidder_name[0][0] + " " + bidder_name[0][1]
            names.append(name_combined)

        else:
            highestBids.append(-1)
            names.append("N/A")

    # get the products that this user has bid on
    result = c.execute('SELECT P.prod_id, P.name, P.seller_email, P.initial_price, P.date, P.increment, P.deadline_date, P.description FROM product P join bids B on P.prod_id = B.prod_id WHERE B.email=?;', (current_user.email,))
    bid_products_1:list[tuple[str,...]] = list(result.fetchall())

    highest_Bids:list[int] = []
    names_bids:list[str] = []

    for product in bid_products_1:
        # get the highest bid for each product
        result = c.execute("SELECT email, MAX(bid_amount) FROM bids WHERE prod_id=?;", (product[0],))
        result_bid_products:list[tuple[str|None, str]] = list(result.fetchall())

        if (result_bid_products[0][0] is not None):
            result_bid_product = result_bid_products[0]
            highest_Bids.append(int(result_bid_product[1]))

            result = c.execute("SELECT first_name, last_name FROM users WHERE email=?;", (result_bid_product[0],))
            bidder_name:list[tuple[str, str]] = list(result.fetchall())
            name_combined = bidder_name[0][0] + " " + bidder_name[0][1]
            names_bids.append(name_combined)
        else:
            highest_Bids.append(-1)
            names_bids.append("N/A")

    response = {}
    response['first_name'] = current_user.first_name
    response['last_name'] = current_user.last_name
    response['contact_no'] = current_user.contact_number
    response['email'] = current_user.email
    response['no_products'] = len(products)
    response['no_bids'] = result_bid_count[0][0]
    response['products'] = products
    response['maximum_bids'] = highestBids
    response['names'] = names
    response['bid_products'] = bid_products_1
    response['bid_bids'] = highest_Bids
    response['bid_names'] = names_bids

    return jsonify(response)

"""
API end point to create a new bid.
This API allows users to bid ona product which is open for auctioning.
Details like productId, email, and new bid amount are extracted from the json.
Then on the basis of productId, initial price of the product is checked to validate if the new bid amount is greater than the initial amount.
If the bid amount is lesser than the value extracted in the previous row, then the bid isn't created/updated.
Otherwise it is created/updated.
"""


@app_functions.route("/bid/create", methods=["POST"])
def create_bid():
    current_user = getuserobject()
    if current_user is None or current_user.is_authenticated is False:
        return jsonify({"message": "User not logged in"}), 401
    # Get relevant data
    productId:str = request.get_json()['prodId']
    email:str = current_user.email
    amount:str = request.get_json()['bidAmount']

    # create db connection
    conn = get_db()
    c = conn.cursor()

    # get initial price wanted by seller
    result = c.execute(
        "SELECT initial_price FROM product WHERE prod_id=?;", (productId,))
    result = list(result.fetchall())
    response = {}

    #  if bid amount is less than price by seller then don't save in db
    if (result[0][0] > (float)(amount)):
        response["message"] = "Amount less than initial price"
    else:
        currentTime = int(datetime.utcnow().timestamp())
        result = c.execute(
            "INSERT OR REPLACE INTO bids(prod_id,email,bid_amount,created_at) VALUES (?,?,?,?);",
            (productId, email, amount, currentTime))
        conn.commit()
        # ⬇️ Trigger email notification to opted-in users
        send_email_notification(f"New bid of ${amount} placed on Product ID: {productId}")
        response["message"] = "Saved Bid"
    return jsonify(response)    

"""
API end point to get a previous bid.
This API allows users to retrieve a previous bid by taking in a productID
They can extract the bid information, using it to get information like current bid and previous 
"""

@app_functions.route("/bid/get", methods=["GET"])
def get_bid():
    # Get relevant data
    productID = request.args.get('productID')
    # create db connection
    conn = get_db()
    c = conn.cursor()
    # get initial price wanted by seller
    result = c.execute(
        "SELECT * FROM bids WHERE prod_id=?;", (productID,))
    result = list(result.fetchall())
    response = {}
    response["result"] = result
    return jsonify(response)


"""
API end point for new product creation.
This API is used to create new entries for the products open for auctioning.
Here, productName, sellerEmail, initialPrice, increment, photo(byte 64 encoded) and product description are extracted from the json.
These values are entered into the product table.
"""


@app_functions.route("/product/create", methods=["POST"])
def create_product():
    current_user = getuserobject()
    if current_user is None:
        return jsonify({"message": "User not logged in"}), 401
    productName:str = request.get_json()['productName']
    initialPrice:str = request.get_json()['initialPrice']
    increment:str = request.get_json()['increment']
    photo:str = request.get_json()['photo']
    description:str = request.get_json()['description']
    biddingtime:str = request.get_json()['biddingTime']

    conn = get_db()
    c = conn.cursor()
    response:dict[str,str] = {}
    currentdatetime = datetime.now()
    formatted_date = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    parsed_date = datetime.strptime(formatted_date, '%Y-%m-%d %H:%M:%S')
    #print(type(currentdatetime))
    #print(type(biddingtime))
    deadlineDate = parsed_date + timedelta(days=int(biddingtime))
    #print(deadlineDate)

    query = "INSERT INTO product(name, seller_email, seller_id, photo, initial_price, date, increment, deadline_date, description) VALUES (?,?,?,?,?,?,?,?,?)"
    _ = c.execute(
        query,
        (str(productName),
        str(current_user.email),
        str(current_user.id),
        str(photo),
        initialPrice,
        deadlineDate,
        increment,
        deadlineDate,
        str(description)))
    conn.commit()
    response["result"] = "Added product successfully"

    return response


"""
API end point to list all the products.
This API lists down all the product details present in product table sorted in the descending order of date created.
"""


@app_functions.route("/product/listAll", methods=["GET"])
def get_all_products():
    query = "SELECT prod_id, name, seller_email, initial_price, date, increment, deadline_date, description FROM product ORDER BY date DESC"
    conn = get_db()
    c = conn.cursor()
    result = c.execute(query)
    all_prods = list(result.fetchall())
    response = {"result": all_prods}
    return (response)



"""
API end point to get image from product ID.
This API is used to get image of the product on the basis of productId extracted from the json.
This returns photo from the product table.

"""


@app_functions.route("/product/getImage", methods=["POST"])
def get_product_image():
    productId:str = request.get_json()['productID']
    query = "SELECT photo FROM product WHERE prod_id=?;"
    conn = get_db()
    c = conn.cursor()
    result = c.execute(query, (productId,))
    result = list(result.fetchall())
    response = {"result": result}
    return response

"""
API end point to get image from product ID.
This API is used to get image of the product on the basis of productId extracted from the json.
This returns photo from the product table.

"""


@app_functions.route("/getOwner", methods=["POST"])
def get_product_owner():
    productId:str = request.get_json()['productID']
    query = "SELECT seller_email FROM product WHERE prod_id=?;"
    conn = get_db()
    c = conn.cursor()
    result = c.execute(query, (productId,))
    result = list(result.fetchall())
    response = {"result": result}
    return response


"""
API end point to details of a product from product ID.
This API is used to get details of the product on the basis of productId extracted from json.
This returns all the details from from the product table.
It also lists down top ten bids of a particular product.
"""


@app_functions.route("/product/getDetails", methods=["POST"])
def get_product_details():
    productID:str = request.get_json()['productID']

    conn = get_db()
    c = conn.cursor()

    # gets product details
    query = "SELECT prod_id, name, seller_email, initial_price, date, increment, deadline_date, seller_id, description FROM product WHERE prod_id=?;"
    result = c.execute(query, (productID,))
    prod_details = list(result.fetchall())

    prod_details_dict = {
        "prod_id": prod_details[0][0],
        "name": prod_details[0][1],
        "seller_email": prod_details[0][2],
        "initial_price": prod_details[0][3],
        "date": prod_details[0][4],
        "increment": prod_details[0][5],
        "deadline_date": prod_details[0][6],
        "seller_id": prod_details[0][7],
        "description": prod_details[0][8],
    }


    # get highest 10 bids
    query = "SELECT email, MAX(bid_amount) FROM bids WHERE prod_id=? GROUP BY email ORDER BY MAX(bid_amount) DESC LIMIT 10;"
    result = c.execute(query, (productID,))

    topbids = list(c.fetchall())

    response = {"product": prod_details_dict, "bids": topbids}
    return response

@app_functions.route("/getName", methods=["GET"])
def get_product_name():
    productID = request.args.get('productID')
    # query = "SELECT p.name FROM product p WHERE p.prod_id=" + str(productID) + ";"
    query = "SELECT name FROM product WHERE prod_id=?;"
    conn = get_db()
    c = conn.cursor()
    result = c.execute(query, (productID,))
    name = list(result.fetchall())
    response = {"result": name[0][0]}
    return response

"""
API endpoitn to delete a product where product_id is the id of the product
"""
@app_functions.route("/product/<product_id>", methods=["DELETE"])
def delete_product(product_id:str):
    query = "DELETE FROM product WHERE prod_id=?;"
    conn = get_db()
    c = conn.cursor()
    result = c.execute(query, (product_id,))
    conn.commit()

    print("Deleted product with id:", product_id)
    print("result:", result)

    return "Product deleted"

"""
API end point to update a product.
This API is used while updating the details of a product.
User provides productId, productName, initialPrice, deadlineDate, description and increment value which is extracted from the json.
These new values are updated in the product table on the basis of productId.
"""


@app_functions.route("/product/update", methods=["POST"])
def update_product_details():
    productId:str = request.get_json()['productID']
    productName:str = request.get_json()['productName']
    initialPrice:str = request.get_json()['initialPrice']
    deadlineDate:str = request.get_json()['deadlineDate']
    description:str = request.get_json()['description']
    increment:str = request.get_json()['increment']

    query = "UPDATE product SET name=?, initial_price=?, deadline_date=?, increment=?, description=? WHERE prod_id=?;"
    conn = get_db()
    c = conn.cursor()
    result = c.execute(query, (productName, initialPrice, deadlineDate, increment, description, productId))
    conn.commit()
    print("Updated product with id:", productId)
    print("result:", result)

    response = {"message": "Updated product successfully"}

    return response


"""
API end point to get top ten latest products.
This API extracts details of the top products sorted by descending order of date created.
It also fetches the highest bids on the those products from the bids table and the user details from the user table.
If there is no such bid on the product, -1 is appended to the list.
"""


@app_functions.route("/getLatestProducts", methods=["GET"])
def get_landing_page():
    response = {}
    query = "SELECT prod_id, name, seller_email, initial_price, date, increment, deadline_date, description FROM product ORDER BY date DESC LIMIT 10;"
    conn = get_db()
    c = conn.cursor()
    latest_prod_result = c.execute(query)
    products:list[tuple[str,...]] = list(latest_prod_result.fetchall())
    #print("Products got:", products)
    highestBids:list[int] = []
    names:list[str] = []
    for product in products:
        prod_result = c.execute("SELECT email, MAX(bid_amount) FROM bids WHERE prod_id=?;", (product[0],))
        prod_result_list:list[tuple[str|None, int]] = list(prod_result.fetchall())
        if (prod_result_list[0][0] is not None):
            this_prod = prod_result_list[0]
            highestBids.append(this_prod[1])
            bidders_result = c.execute("SELECT first_name, last_name FROM users WHERE email=?;", (this_prod[0],))
            bidders_result_list:list[tuple[str, str]] = list(bidders_result.fetchall())
            names.append(bidders_result_list[0][0] + " " + bidders_result_list[0][1])
        else:
            highestBids.append(-1)
            names.append("N/A")
    response = {
        "products": products,
        "maximumBids": highestBids,
        "names": names}
    #print(response)
    return jsonify(response)


@app_functions.route("/getTopTenProducts", methods=["GET"])
def get_top_products():
    response = {}
    query = "SELECT name, photo, description FROM product ORDER BY date DESC LIMIT 10;"
    conn = get_db()
    c = conn.cursor()
    result = c.execute(query)
    products = list(result.fetchall())
    if len(products) == 0:
        print("No data found")
    response = {
        "products": products}
    return jsonify(response)


"""
send_messaage sends a message with the logged in user as the sender, and recipient specified by recipient_id
product is specified by product_id, and message is stored in message.
"""
@app_functions.route("/message", methods=["POST"])
def send_message():
    product_id:str = request.get_json()['product_id']
    # sender_id = global_id
    current_user = getuserobject()
    if current_user is None:
        return jsonify({"message": "User not logged in"}), 401
    sender_id = current_user.id
    recipient_id:str = request.get_json()['recipient_id']
    message:str = request.get_json()['message']

    return chatService.send_message(get_db(), message, recipient_id, sender_id, product_id)


"""
get_messages returns the last message of each conversation chain the user is participating in.
"""
@app_functions.route("/messages", methods=["GET"])
def get_messages():
    current_user = getuserobject()
    if current_user is None:
        return jsonify({"message": "User not logged in"}), 401
    return chatService.get_messages(get_db(), current_user.id)

"""
read message returns all messages for a conversation given its product_id and bidder_id
"""
@app_functions.route("/message/product/<product_id>/bidder/<bidder_id>", methods=["GET"])
def read_message(product_id, bidder_id):
    current_user = getuserobject()
    if current_user is None:
        return jsonify({"message": "User not logged in"}), 401
    return chatService.read_message(get_db(), current_user.id,int(bidder_id), int(product_id))


"""
API end point for new notification creation.
This API is used to create new notifications for users.
Here, messages, recpients,  are extracted from the json.
These values are entered into the notification table.
"""

@app_functions.route("/notifications", methods=["POST"])
def create_notification():
    user_id:str = request.get_json()['user_id']
    message:str = request.get_json()['message']
    detail_page:str = request.get_json()['detail_page']
    currentdatetime = datetime.now()
    formatted_date = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db()
    c = conn.cursor()
    response:dict[str, str] = {}

    query = "INSERT INTO notifications(user_id, message, detail_page, time_sent, read) VALUES (?,?,?,?,?)"
    _ = c.execute(
        query,
        (str(user_id),
        str(message),
        str(detail_page),
        str(formatted_date),
        False))
    conn.commit()
    response["result"] = "Added notification successfully"

    return response

"""
API end point for retrieving user notifications.
This API is used to retrieve notifications for users.
Here, notifications, message details, links, and time_sent
are extracted from the database.
"""
@app_functions.route("/notifications/get", methods=["GET"])
def get_user_notifications():
    current_user = getuserobject()
    if current_user is None:
        return jsonify({"message": "User not logged in"}), 401
    user_id = current_user.id
    query = '''SELECT notif_id,message,detail_page,time_sent 
                FROM notifications 
                WHERE user_id = ? AND read = FALSE'''
    conn = get_db()
    c = conn.cursor()
    notif_results = c.execute(query, [user_id])
    results = list(notif_results.fetchall())
    if len(results) == 0:
        return {"notifications": []}
    else:
        notifications = []
        for row in results:
            notifications.append({
                "notif_id": row[0],
                "image": '../src/assets/logo96.png', #Can be set on a case by case basis, this is an intentionally failing placeholder
                "message": row[1],
                "detailPage": row[2],
                "receivedTime": row[3]
            })
        return {"notifications": notifications}
        
"""
API end point for set user notifications as read.
This API is used to update a single user notification.
Here, a notification is set to read if not already read.
"""
@app_functions.route("/notifications/<int:notif_id>/read", methods=["PUT"])
def read_user_notifications(notif_id):
    try:
        query = '''UPDATE notifications SET read = TRUE 
                WHERE notif_id = ? AND read = FALSE'''
        conn = get_db()
        c = conn.cursor()
        _ = c.execute(query, (notif_id,))
        conn.commit()
        response = {}
        response["result"] = "Read notification successfully"
        return response
    except Exception as e:
        return {"error": "Failed to update notification"}, 500

"""
API end point for set user notifications as read.
This API is used to update all of a user's notifications.
Here, a notification is set to read if not already read.
"""
@app_functions.route("/notifications/read", methods=["PUT"])
def read_all_user_notifications():
    current_user = getuserobject()
    if current_user is None:
        return jsonify({"message": "User not logged in"}), 401
    user_id = current_user.id
    try:
        query = '''UPDATE notifications SET read = TRUE 
                WHERE read = ALSE and user_id = ?'''
        conn = get_db()
        c = conn.cursor()
        _ = c.execute(query, [user_id])
        conn.commit()
        response = {}
        response["result"] = "Read all notifications successfully"
        return response
    except Exception as e:
        return {"error": "Failed to update notifications"}, 500
    

@app_functions.route("/logout", methods=["POST"])
def logout():
    """
    Logout the current user
    """
    current_user = getuserobject()
    if current_user is None:
        return jsonify({"message": "User not logged in"}), 401
    flask_login.logout_user()
    return jsonify({"message": "Logged out successfully"})

@app_functions.route("/currentuser", methods=["GET"])
def get_current_user():
    """
    Get properties of the currently logged in user
    Useful to check if the user is logged in, or to retrieve details
    As of April 11, 2025, this is not used in the frontend, but could be useful
    in the future.
    """
    current_user = getuserobject()
    if current_user is None:
        return jsonify({"message": "User not logged in"}), 401
    response = {
        "user_id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "contact_number": current_user.contact_number
    }
    return jsonify(response)

# Watchlist routes

@app_functions.route('/watchlist/check', methods=['POST'])
# @login_required
def check_watchlist():
    current_user = getuserobject()
    if current_user is None:
        return jsonify({"message": "User not logged in"}), 401
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Get product ID from request
        product_id = data.get('productID')
        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400

        # Get current user from Flask-Login
        user_id = current_user.id

        # Check if product exists in user's watchlist
        query = '''SELECT 1 FROM watchlist WHERE user_id = ? AND product_id = ?'''
        conn = get_db()
        c = conn.cursor()
        
        _ = c.execute(query, [user_id, product_id])
        
        is_in_watchlist = c.fetchone() is not None

        return jsonify({
            "success": True,
            "isInWatchlist": is_in_watchlist
        })

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database operation failed"}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app_functions.route('/watchlist/add', methods=['POST'])
def add_to_watchlist():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({"success": True})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response
        
    current_user = getuserobject()
    if current_user is None:
        return jsonify({"message": "User not logged in"}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Get product_id from request data (use get() with default to avoid KeyError)
        product_id = data.get('productID') or data.get('product_id')  # Handle both cases
        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400
        user_id = current_user.id

        query = '''INSERT INTO watchlist (user_id, product_id) VALUES (?, ?)'''
        conn = get_db()
        c = conn.cursor()
        
        _ = c.execute(query, [user_id, product_id])
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Added to watchlist",
            "isInWatchlist": True  # Helps frontend update state
        })

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except sqlite3.IntegrityError:
        return jsonify({"error": "Database integrity error"}), 400
    except Exception as e:
        print(f"Watchlist error: {str(e)}")  # Log for debugging
        return jsonify({"error": "Internal server error"}), 500


@app_functions.route('/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    current_user = getuserobject()
    if current_user is None:
        return jsonify({"message": "User not logged in"}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Get product_id from request data (use get() with default to avoid KeyError)
        product_id = data.get('productID') or data.get('product_id')  # Handle both cases
        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400
        user_id = current_user.id

        query = '''DELETE FROM watchlist WHERE user_id = ? AND product_id = ?'''
        conn = get_db()
        c = conn.cursor()
        
        _ = c.execute(query, [user_id, product_id])
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Removed from watchlist",
            "isInWatchlist": False  # Helps frontend update state
        })

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except sqlite3.IntegrityError as e:
        return jsonify({"error": "Database integrity error"}), 400
    except Exception as e:
        print(f"Watchlist error: {str(e)}")  # Log for debugging
        return jsonify({"error": "Internal server error"}), 500
    
@app_functions.route('/watchlist/items', methods=['GET'])
def get_watchlist_items():
    current_user = getuserobject()
    if current_user is None:
        return jsonify({"message": "User not logged in"}), 401
    try:
        user_id = current_user.id
        
        query = '''SELECT p.prod_id, p.name, p.seller_email, p.initial_price, p.date, p.increment, p.deadline_date, p.description
            FROM product p, watchlist w
            WHERE p.prod_id = w.product_id AND w.user_id = ?
            ORDER BY w.created_at DESC'''
        conn = get_db()
        c = conn.cursor()

        watchlist_prod_result = c.execute(query, [user_id])
        products:list[tuple[str,...]] = list(watchlist_prod_result.fetchall())
        #print("Products got:", products)
        highestBids:list[int] = []
        names:list[str] = []
        for product in products:
            prod_result = c.execute("SELECT email, MAX(bid_amount) FROM bids WHERE prod_id=?;", (product[0],))
            prod_result_list:list[tuple[str|None, int]] = list(prod_result.fetchall())
            if (prod_result_list[0][0] is not None):
                this_prod = prod_result_list[0]
                highestBids.append(this_prod[1])
                bidders_result = c.execute("SELECT first_name, last_name FROM users WHERE email=?;", (this_prod[0],))
                bidders_result_list:list[tuple[str, str]] = list(bidders_result.fetchall())
                names.append(bidders_result_list[0][0] + " " + bidders_result_list[0][1])
            else:
                highestBids.append(-1)
                names.append("N/A")
        response = {
            "products": products,
            "maximumBids": highestBids,
            "names": names}
        #print(response)
        return jsonify(response)
        
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database operation failed"}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app_functions.route("/watchlist/users", methods=["GET"])
def get_watchlist_users():
    product_id = request.args.get('productId')
    if not product_id:
        return jsonify({"error": "productId parameter is required"}), 400
    
    query = '''SELECT DISTINCT u.user_id, u.email 
            FROM users u, watchlist w 
            WHERE u.user_id = w.user_id AND w.product_id = ?'''
    
    conn = get_db()
    c = conn.cursor()
    watchers_results = c.execute(query, [product_id])
    results = list(watchers_results.fetchall())
    
    users = []
    for row in results:
        users.append({
            "user_id": row[0],
            "email": row[1]
        })
    
    return jsonify({"users": users})

# flask app factory pattern. makes testing a _lot_ easier
# (yes, it's not quite the same as the recommended setup, but hey)
def create_app(app_key_path = "./app_key", notify_config_file="./notifications.toml", db_file="./auction.db", testing=False) -> Flask:
    """
    Create a Flask application.
    """
    # Create the Flask app
    app = Flask(__name__)
    app.testing = testing
    # Load the configuration from a file
    # ensure the file exists
    if not os.path.exists(notify_config_file):
        print("Configuration file notifications.toml not found. Email's will not be sent.")
        # use template config instead
        notify_config_file = "notifications.toml.example"
    conf_loaded = app.config.from_file(notify_config_file, load=tomllib.load, text=False)
    this_file_dir = os.path.dirname(os.path.abspath(__file__))
    # if app_key_path is not an absolute path, make it absolute
    if not os.path.isabs(app_key_path):
        app_key_path = os.path.join(this_file_dir, app_key_path)
    if os.path.exists(app_key_path):
        with open(app_key_path, "r") as f:
            app.secret_key = f.read()
    else:
        if not testing:
            print("app_key file not found - creating a random key")
        import secrets
        app.secret_key = secrets.token_hex(16)
        with open("app_key", "w") as f:
            f.write(str(app.secret_key))
        if not testing: 
            print("app_key file created - please keep this file safe")
    # Initialize CORS
    _ = CORS(app)
    # Initialize the login manager
    login_manager.init_app(app)  # pyright:ignore[reportUnknownMemberType]

    app.config['DATABASE'] = db_file


    @login_manager.user_loader
    def load_user(user_id:str|int) -> User|None:
        user =  User.user_by_id(get_db(), user_id)
        return user


    def convertToBinaryData(filename:str):
        # Convert digital data to binary format

        with open(filename, 'rb') as file:
            blobData = file.read()
        return blobData
    init_db(get_db(db_file))

    # add the routes to the app
    app.register_blueprint(app_functions)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
