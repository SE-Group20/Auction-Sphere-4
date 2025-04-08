import os
from flask import Flask, request, jsonify, url_for, g
from flask_cors import CORS
import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta

from flask_login.utils import LocalProxy

from backend.services.chat import ChatService
from backend.user import User, MaybeUser
# from notification import NotificationService
# https://flask-login.readthedocs.io/en/latest/
import flask_login
login_manager = flask_login.LoginManager()

app = Flask(__name__)
login_manager.init_app(app) # pyright:ignore[reportUnknownMemberType]
# try to load secret key from app_key file
this_file_dir = os.path.dirname(os.path.abspath(__file__))
key_file = os.path.join(this_file_dir, "app_key")
if os.path.exists(key_file):
    with open("app_key", "r") as f:
        app.secret_key = f.read()
else:
    print("app_key file not found!")
    quit()

_ = CORS(app)

chatService = ChatService()

@login_manager.user_loader
def load_user(user_id:str|int) -> User|None:
    return User.user_by_id(get_db(), user_id)

def create_table(conn:sqlite3.Connection, create_table_sql:str):
    try:
        c = conn.cursor()
        _ = c.execute(create_table_sql)
        conn.commit()
    except Error as e:
        print(e)


def convertToBinaryData(filename:str):
    # Convert digital data to binary format

    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


database_file = r"auction.db"

def get_db() -> sqlite3.Connection:
    db:sqlite3.Connection|None = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database_file)
    return db


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


"""
API end point for user creation.
It extracts firstName, lastName, email, contact number and password from the json.
This further checks if the email provided is already there in the database or not.
If the account is already created, the API returns (An account with this contact already exists)
otherwise, a new user is created in the users table with all the details extracted from json.
"""


@app.route("/signup", methods=["POST"])
def signup():
    firstName:str = request.get_json()['firstName']
    lastName:str = request.get_json()['lastName']
    email:str = request.get_json()['email']
    contact:str = request.get_json()['contact']
    password:str = request.get_json()['password']

    user_obj = User(None, email, password, firstName, lastName, contact)

    conn = get_db()

    success, message = user_obj.try_signup(conn)

    response = {}
    if success:
        response["message"] = "Account created successfully"
    else:
        response["message"] = message

    if success:
        return jsonify(response)
    else:
        return jsonify(response), 409


"""
API end point for user login.
User email and password are extracted from the json.
These are validated from the data already available in users table.
If the email and password are correct, login is successful else user is asked to create an account.
"""


@app.route("/login", methods=["POST"])
def login():
    email:str = request.get_json()['email']
    password:str = request.get_json()['password']

    conn = get_db()

    result:User|None = User.try_login(conn, email, password)
    response = {}

    if result:
        # we found a user in the db
        login_result = flask_login.login_user(result) # pyright:ignore[reportUnknownMemberType]
        if login_result:
            response["message"] = "Logged in successfully"
            return jsonify(response)

    response["message"] = "Invalid credentials"
    return jsonify(response)


""" 
API end point for user profile.
User email is set in the login function which is used here to pull the user stats.
Page includes information entered by the user i.e first name, last name, contact number and email.
It also displays the specific product cards for the user. 
It shows the products the user has put for sale and the products for which the user has submitted a bid.
"""


@app.route('/profile', methods=["POST"])
def profile():
    maybe_current_user: MaybeUser = flask_login.current_user
    if not maybe_current_user or maybe_current_user.is_authenticated == False:
        return jsonify({"message": "User not logged in"}), 401

    # must be a user - safe to cast
    current_user: User = maybe_current_user # pyright:ignore[reportAssignmentType]
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


@app.route("/bid/create", methods=["POST"])
def create_bid():
    # Get relevant data
    productId:str = request.get_json()['prodId']
    email:str = request.get_json()['email']
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

        response["message"] = "Saved Bid"
    return jsonify(response)

"""
API end point to get a previous bid.
This API allows users to retrieve a previous bid by taking in a productID
They can extract the bid information, using it to get information like current bid and previous 
"""

@app.route("/bid/get", methods=["GET"])
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


@app.route("/product/create", methods=["POST"])
def create_product():
    productName:str = request.get_json()['productName']
    sellerEmail:str = request.get_json()['sellerEmail']
    # TODO(kurt): don't trust the client's input!
    sellerId:str = request.get_json()['sellerId']
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
         str(sellerEmail),
         str(sellerId),
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


@app.route("/product/listAll", methods=["GET"])
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


@app.route("/product/getImage", methods=["POST"])
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


@app.route("/getOwner", methods=["POST"])
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


@app.route("/product/getDetails", methods=["POST"])
def get_product_details():
    productID:str = request.get_json()['productID']

    conn = get_db()
    c = conn.cursor()

    # gets product details
    query = "SELECT prod_id, name, seller_email, initial_price, date, increment, deadline_date, description FROM product WHERE prod_id=?;"
    result = c.execute(query, (productID,))
    prod_details = list(result.fetchall())


    # get highest 10 bids
    query = "SELECT email, MAX(bid_amount) FROM bids WHERE prod_id=? GROUP BY email ORDER BY MAX(bid_amount) DESC LIMIT 10;"
    result = c.execute(query, (productID,))

    topbids = list(c.fetchall())

    response = {"product": prod_details, "bids": topbids}
    return response

@app.route("/getName", methods=["GET"])
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
@app.route("/product/<product_id>", methods=["DELETE"])
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


@app.route("/product/update", methods=["POST"])
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


@app.route("/getLatestProducts", methods=["GET"])
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


@app.route("/getTopTenProducts", methods=["GET"])
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
@app.route("/message", methods=["POST"])
def send_message():
    product_id:str = request.get_json()['product_id']
    # sender_id = global_id
    maybe_current_user: MaybeUser = flask_login.current_user
    if not maybe_current_user or maybe_current_user.is_authenticated == False:
        return jsonify({"message": "User not logged in"}), 401
    # must be a user - safe to cast
    current_user: User = maybe_current_user # pyright:ignore[reportAssignmentType]
    sender_id = current_user.id
    recipient_id:str = request.get_json()['recipient_id']
    message:str = request.get_json()['message']

    return chatService.send_message(message, recipient_id, sender_id, product_id)


"""
get_messages returns the last message of each conversation chain the user is participating in.
"""
@app.route("/messages", methods=["GET"])
def get_messages():
    maybe_current_user: MaybeUser = flask_login.current_user
    if not maybe_current_user or maybe_current_user.is_authenticated == False:
        return jsonify({"message": "User not logged in"}), 401
    # must be a user - safe to cast
    current_user: User = maybe_current_user # pyright:ignore[reportAssignmentType]
    return chatService.get_messages(current_user.id)

"""
read message returns all messages for a conversation given its product_id and bidder_id
"""
@app.route("/message/product/<product_id>/bidder/<bidder_id>", methods=["GET"])
def read_message(product_id, bidder_id):
    maybe_current_user: MaybeUser = flask_login.current_user
    if not maybe_current_user or maybe_current_user.is_authenticated == False:
        return jsonify({"message": "User not logged in"}), 401
    # must be a user - safe to cast
    current_user: User = maybe_current_user # pyright:ignore[reportAssignmentType]
    return chatService.read_message(current_user.id,bidder_id, product_id)

  
"""
API end point for new notification creation.
This API is used to create new notifications for users.
Here, messages, recpients,  are extracted from the json.
These values are entered into the notification table.
"""

@app.route("/notifications", methods=["POST"])
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
@app.route("/notifications/get", methods=["GET"])
def get_user_notifications():
    maybe_current_user = flask_login.current_user
    if not maybe_current_user or maybe_current_user.is_authenticated == False:
        return jsonify({"message": "User not logged in"}), 401
    # must be a user - safe to cast
    current_user: User = maybe_current_user # pyright:ignore[reportAssignmentType]
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
@app.route("/notifications/<int:notif_id>/read", methods=["PUT"])
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
@app.route("/notifications/read", methods=["PUT"])
def read_all_user_notifications():
    maybe_current_user: MaybeUser = flask_login.current_user
    if not maybe_current_user or maybe_current_user.is_authenticated == False:
        return jsonify({"message": "User not logged in"}), 401
    # must be a user - safe to cast
    current_user: User = maybe_current_user # pyright:ignore[reportAssignmentType]
    user_id = current_user.id
    try:
        query = '''UPDATE notifications SET read = TRUE 
                  WHERE read = FALSE and user_id = ?'''
        conn = get_db()
        c = conn.cursor()
        _ = c.execute(query, [user_id])
        conn.commit()
        response = {}
        response["result"] = "Read all notifications successfully"
        return response
    except Exception as e:
        return {"error": "Failed to update notifications"}, 500


database = r"auction.db"
create_users_table = """CREATE TABLE IF NOT EXISTS users( 
    user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    first_name TEXT NOT NULL, 
    last_name TEXT NOT NULL, 
    contact_number TEXT NOT NULL UNIQUE, 
    email TEXT UNIQUE, 
    password TEXT NOT NULL);"""

# TODO(kurt): normalize database - don't keep seller_id and seller_email as separate fields
# use a foreign key to reference the user table instead
create_product_table = """CREATE TABLE IF NOT EXISTS product(prod_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, photo TEXT, seller_id INTEGER NOT NULL, seller_email TEXT NOT NULL, initial_price REAL NOT NULL, date TIMESTAMP NOT NULL, increment REAL, deadline_date TIMESTAMP NOT NULL, description TEXT,  FOREIGN KEY(seller_email) references users(email), FOREIGN KEY(seller_id) references users(user_id));"""

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


"""Create Connection to database"""
conn = sqlite3.connect(database_file, check_same_thread=False)

if conn is not None:
    create_table(conn, create_users_table)
    create_table(conn, create_product_table)
    create_table(conn, create_bids_table)
    create_table(conn, create_table_claims)

    create_table(conn, create_message_table)
    create_table(conn, create_notification_table)
    cursor = conn.cursor()
    conn.commit()

    conn.close()
else:
    print("Error! Cannot create the database connection")

if __name__ == "__main__":
    app.debug = True
    app.run()
