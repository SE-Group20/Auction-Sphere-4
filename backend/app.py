#import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta

from services.chat import ChatService
from pytest import param
from notification import NotificationService

app = Flask(__name__)
CORS(app)

chatService = ChatService()

global_email = None
global_id = None

def create_connection(db_file):
    conn = None
    conn = sqlite3.connect(db_file)
    return conn


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
    except Error as e:
        print(e)


def convertToBinaryData(filename):
    # Convert digital data to binary format

    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


database = r"auction.db"


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
    firstName = request.get_json()['firstName']
    lastName = request.get_json()['lastName']
    email = request.get_json()['email']
    contact = request.get_json()['contact']
    password = request.get_json()['password']

    conn = create_connection(database)
    c = conn.cursor()

    # check if email already exists
    query = "SELECT COUNT(*) FROM users WHERE email='" + str(email) + "';"
    c.execute(query)

    result = list(c.fetchall())
    response = {}
    if (result[0][0] == 0): #Email doesn't exist
        query = "SELECT COUNT(*) FROM users WHERE contact_number='" + \
                str(contact) + "';"
        c.execute(query)
        result = list(c.fetchall())

        if (result[0][0] != 0): #If contact number exists
            response["message"] = "An account with this contact already exists"
            return jsonify(response), 409
        else:
            query = "INSERT INTO users(first_name, last_name, email, contact_number, password) VALUES('" + str(
                firstName) + "','" + str(lastName) + "','" + str(email) + "','" + str(contact) + "','" + str(
                password) + "');"
            c.execute(query)
            conn.commit()
            response["message"] = "Added successfully"
    else:
        response["message"] = "An account with this email already exists"
        return jsonify(response), 409
    return response


"""
API end point for user login.
User email and password are extracted from the json.
These are validated from the data already available in users table.
If the email and password are correct, login is successful else user is asked to create an account.
"""


@app.route("/login", methods=["POST"])
def login():
    global global_email
    global global_id
    email = request.get_json()['email']
    password = request.get_json()['password']

    conn = create_connection(database)
    c = conn.cursor()

    # check if email and password pair exists
    query = "SELECT * FROM users WHERE email='" + \
            str(email) + "' AND password='" + str(password) + "';"
    c.execute(query)
    result = list(c.fetchall())
    response = {}

    if (len(result) == 1):
        response["message"] = "Logged in successfully"

        global_email = str(email)
        global_id = result[0][0]
    else: 
        # check if email exists, but password is incorrect
        query = "SELECT COUNT(*) FROM users WHERE email='" + str(email) + "';"
        c.execute(query)
        result = list(c.fetchall())
        if (result[0][0] == 1):
            response["message"] = "Invalid credentials!"
        else:
            response["message"] = "Please create an account!"
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
    global global_email

    # create db connection
    conn = create_connection(database)
    c = conn.cursor()

    query = 'SELECT * FROM users WHERE email=\'' + str(global_email) + "\';"
    c.execute(query)
    result = list(c.fetchall())

    query_sell = 'SELECT COUNT(*) FROM product WHERE seller_email=\'' + str(global_email) + '\';'
    c.execute(query_sell)
    result_sell = list(c.fetchall())

    query_bid = 'SELECT COUNT(*) FROM bids WHERE email=\'' + str(global_email) + '\';'
    c.execute(query_bid)
    result_bid = list(c.fetchall())

    query_sell = 'SELECT prod_id, name, seller_email, initial_price, date, increment, deadline_date, description FROM product WHERE seller_email=\'' + str(
        global_email) + '\'ORDER BY date DESC LIMIT 10;'
    conn = create_connection(database)
    c = conn.cursor()
    c.execute(query_sell)
    products = list(c.fetchall())
    highestBids = []
    names = []
    for product in products:
        query = "SELECT email, MAX(bid_amount) FROM bids WHERE prod_id=" + str(product[0]) + ";"
        c.execute(query)
        result_bids = list(c.fetchall())
        if (result_bids[0][0] is not None):
            result_bids = result_bids[0]
            highestBids.append(result_bids[1])
            query = "SELECT first_name, last_name FROM users WHERE email='" + str(result_bids[0]) + "';"
            c.execute(query)
            names.append(list(c.fetchall())[0])
        else:
            highestBids.append(-1)
            names.append("N/A")

    query_2 = 'SELECT P.prod_id, P.name, P.seller_email, P.initial_price, P.date, P.increment, P.deadline_date, P.description FROM product P join bids B on P.prod_id = B.prod_id WHERE B.email = \'' + str(
        global_email) + '\';'
    print("Query 2:", query_2)

    c.execute(query_2)
    bid_products_1 = list(c.fetchall())
    highest_Bids = []
    names_bids = []

    for product in bid_products_1:
        query_products = "SELECT email, MAX(bid_amount) FROM bids WHERE prod_id=" + str(product[0]) + ";"
        c.execute(query_products)
        result_bid_products = list(c.fetchall())
        if (result_bid_products[0][0] is not None):
            result_bid_products = result_bid_products[0]
            highest_Bids.append(result_bid_products[1])
            query = "SELECT first_name, last_name FROM users WHERE email='" + str(result_bid_products[0]) + "';"
            c.execute(query)
            names_bids.append(list(c.fetchall())[0])
        else:
            highest_Bids.append(-1)
            names_bids.append("N/A")

    response = {}
    response['first_name'] = result[0][1]
    response['last_name'] = result[0][2]
    response['contact_no'] = result[0][3]
    response['email'] = result[0][4]
    response['no_products'] = result_sell[0][0]
    response['no_bids'] = result_bid[0][0]
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
    productId = request.get_json()['prodId']
    email = request.get_json()['email']
    amount = request.get_json()['bidAmount']

    # create db connection
    conn = create_connection(database)
    c = conn.cursor()

    # get initial price wanted by seller
    select_query = "SELECT initial_price FROM product WHERE prod_id='" + \
                   str(productId) + "';"
    c.execute(select_query)
    result = list(c.fetchall())
    response = {}

    #  if bid amount is less than price by seller then don't save in db
    if (result[0][0] > (float)(amount)):
        response["message"] = "Amount less than initial price"
    else:
        currentTime = int(datetime.utcnow().timestamp())
        # print(currentTime)
        insert_query = "INSERT OR REPLACE INTO bids(prod_id,email,bid_amount,created_at) VALUES ('" + str(
            productId) + "','" + str(email) + "','" + str(amount) + "','" + str(currentTime) + "');"
        c.execute(insert_query)
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
    conn = create_connection(database)
    c = conn.cursor()
    # get initial price wanted by seller
    select_query = "SELECT * FROM bids WHERE prod_id='" + \
        str(productID) + "';"
    c.execute(select_query)
    result = list(c.fetchall())
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
    productName = request.get_json()['productName']
    sellerEmail = request.get_json()['sellerEmail']
    initialPrice = request.get_json()['initialPrice']
    increment = request.get_json()['increment']
    photo = request.get_json()['photo']
    description = request.get_json()['description']
    biddingtime = request.get_json()['biddingTime']
    conn = create_connection(database)
    c = conn.cursor()
    response = {}
    currentdatetime = datetime.now()
    formatted_date = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    parsed_date = datetime.strptime(formatted_date, '%Y-%m-%d %H:%M:%S')
    #print(type(currentdatetime))
    #print(type(biddingtime))
    deadlineDate = parsed_date + timedelta(days=int(biddingtime))
    #print(deadlineDate)

    query = "INSERT INTO product(name, seller_email, photo, initial_price, date, increment, deadline_date, description) VALUES (?,?,?,?,?,?,?,?)"
    c.execute(
        query,
        (str(productName),
         str(sellerEmail),
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
    conn = create_connection(database)
    c = conn.cursor()
    c.execute(query)
    result = list(c.fetchall())
    response = {"result": result}
    return (response)


"""
API end point to get image from product ID.
This API is used to get image of the product on the basis of productId extracted from the json.
This returns photo from the product table.

"""


@app.route("/product/getImage", methods=["POST"])
def get_product_image():
    productId = request.get_json()['productID']
    query = "SELECT photo FROM product WHERE prod_id=" + str(productId) + ";"
    conn = create_connection(database)
    c = conn.cursor()
    c.execute(query)
    result = list(c.fetchall())
    response = {"result": result}
    return response

"""
API end point to get image from product ID.
This API is used to get image of the product on the basis of productId extracted from the json.
This returns photo from the product table.

"""


@app.route("/getOwner", methods=["POST"])
def get_product_owner():
    productId = request.get_json()['productID']
    query = "SELECT u.user_id FROM users u JOIN product p on u.email = p.seller_email WHERE p.prod_id=" + str(productId) + ";"
    conn = create_connection(database)
    c = conn.cursor()
    c.execute(query)
    result = list(c.fetchall())
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
    productID = request.get_json()['productID']

    conn = create_connection(database)
    c = conn.cursor()

    # gets product details
    query = "SELECT * FROM product WHERE prod_id=" + str(productID) + ";"
    c.execute(query)
    result = list(c.fetchall())

    # get highest 10 bids
    query = "SELECT users.first_name, users.last_name, bids.bid_amount FROM users INNER JOIN bids ON bids.email = users.email WHERE bids.prod_id=" + \
            str(productID) + " ORDER BY bid_amount DESC LIMIT 10;"
    c.execute(query)
    topbids = list(c.fetchall())

    response = {"product": result, "bids": topbids}
    return response

@app.route("/getName", methods=["GET"])
def get_product_name():
    productID = request.args.get('productID')
    query = "SELECT p.name FROM product p WHERE p.prod_id=" + str(productID) + ";"
    conn = create_connection(database)
    c = conn.cursor()
    c.execute(query)
    result = list(c.fetchall())
    response = {"result": result[0][0]}
    return response


@app.route("/product/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    query = "DELETE FROM product WHERE prod_id=" + str(product_id) + ";"
    conn = create_connection(database)
    c = conn.cursor()
    c.execute(query)
    conn.commit()

    return "Product deleted"

"""
API end point to update a product.
This API is used while updating the details of a product.
User provides productId, productName, initialPrice, deadlineDate, description and increment value which is extracted from the json.
These new values are updated in the product table on the basis of productId.
"""


@app.route("/product/update", methods=["POST"])
def update_product_details():
    productId = request.get_json()['productID']
    productName = request.get_json()['productName']
    initialPrice = request.get_json()['initialPrice']
    deadlineDate = request.get_json()['deadlineDate']
    description = request.get_json()['description']
    increment = request.get_json()['increment']

    query = "UPDATE product SET name='" + str(productName) + "',initial_price='" + str(
        initialPrice) + "',deadline_date='" + str(
        deadlineDate) + "',increment='" + str(increment) + "',description='" + str(
        description) + "' WHERE prod_id=" + str(productId) + ";"
    print(query)

    conn = create_connection(database)
    c = conn.cursor()
    c.execute(query)
    conn.commit()
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
    conn = create_connection(database)
    c = conn.cursor()
    c.execute(query)
    products = list(c.fetchall())
    #print("Products got:", products)
    highestBids = []
    names = []
    for product in products:
        query = "SELECT email, MAX(bid_amount) FROM bids WHERE prod_id=" + \
                str(product[0]) + ";"
        c.execute(query)
        result = list(c.fetchall())
        #print("Results got:", result)
        #print("\n0", result[0])
        #print("\n0,0", result[0][0])
        if (result[0][0] is not None):
            result = result[0]
            highestBids.append(result[1])
            query = "SELECT first_name, last_name FROM users WHERE email='" + \
                    str(result[0]) + "';"
            c.execute(query)
            names.append(list(c.fetchall())[0])
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
    conn = create_connection(database)
    c = conn.cursor()
    c.execute(query)
    products = list(c.fetchall())
    if products.__len__ == 0:
        print("No data found")
    response = {
        "products": products}
    return jsonify(response)


@app.route("/message", methods=["POST"])
def send_message():
    product_id = request.get_json()['product_id']
    sender_id = global_id
    recipient_id = request.get_json()['recipient_id']
    message = request.get_json()['message']

    return chatService.send_message(message, recipient_id, sender_id, product_id)

@app.route("/messages", methods=["GET"])
def get_messages():
    return chatService.get_messages(global_id)

@app.route("/message/product/<product_id>/bidder/<bidder_id>", methods=["GET"])
def read_message(product_id, bidder_id):
    return chatService.read_message(global_id,bidder_id, product_id)

  
"""
API end point for new notification creation.
This API is used to create new notifications for users.
Here, messages, recpients,  are extracted from the json.
These values are entered into the notification table.
"""

@app.route("/notifications", methods=["POST"])
def create_notification():
    user_id = request.get_json()['user_id']
    message = request.get_json()['message']
    detail_page = request.get_json()['detail_page']
    currentdatetime = datetime.now()
    formatted_date = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    conn = create_connection(database)
    c = conn.cursor()
    response = {}

    query = "INSERT INTO notifications(user_id, message, detail_page, time_sent, read) VALUES (?,?,?,?,?)"
    c.execute(
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
@app.route("/notifications/<int:user_id>", methods=["GET"])
def get_user_notifications(user_id):
        user_id = global_id
        query = '''SELECT notif_id,message,detail_page,time_sent 
                  FROM notifications 
                  WHERE user_id = ? AND read = FALSE'''
        conn = create_connection(database)
        c = conn.cursor()
        c.execute(query, [user_id])
        results = list(c.fetchall())
        if len(results) == 0:
            return {"notifications": "User has no unread notifications."}
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
        conn = create_connection(database)
        c = conn.cursor()
        c.execute(query, (notif_id,))
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
    user_id = global_id
    try:
        query = '''UPDATE notifications SET read = TRUE 
                  WHERE read = FALSE and user_id = ?'''
        conn = create_connection(database)
        c = conn.cursor()
        c.execute(query, [user_id])
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
conn = create_connection(database)
if conn is not None:
    create_table(conn, create_users_table)
    create_table(conn, create_product_table)
    create_table(conn, create_bids_table)
    create_table(conn, create_table_claims)

    create_table(conn, create_message_table)
    create_table(conn, create_notification_table)
    cursor = conn.cursor()
    conn.commit()

else:
    print("Error! Cannot create the database connection")

if __name__ == "__main__":
    app.debug = True
    app.run()
