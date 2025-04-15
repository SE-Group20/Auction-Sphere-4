import sqlite3

from flask_login import current_user

class ChatService:
    """
    send_message adds a new message to the messages table using the provided parameters of
    message, recipient_id, sender_id, product_id
    """
    def send_message(self, conn, message, recipient_id, sender_id, product_id):
        query= '''INSERT INTO messages (sender_id, recipient_id, product_id, message) 
            VALUES (?, ?, ?, ?)'''
        message_details = [sender_id, recipient_id, product_id, message]
        cursor = conn.cursor()
        cursor.execute(query, message_details)
        conn.commit()

        return {"message": "Message sent successfully"}

    """
    user_is_product_seller tests if user_id is the user_id of the specified product
    """
    def user_is_product_seller(self, conn, product_id, user_id):
        query= '''SELECT EXISTS(SELECT 1 FROM product WHERE prod_id = ? AND seller_id = ?)'''
        cursor = conn.cursor()
        cursor.execute(query, (product_id, user_id))
        return cursor.fetchone()[0]

    """
    set_messages_to_read sets the status of mesesages to read given the user ids
    """
    def set_messages_to_read(self, conn, product_id, current_user, sender_id):
        query = '''UPDATE messages SET read = 1 WHERE product_id = ? AND recipient_id = ? AND sender_id = ?'''
        cursor = conn.cursor()
        cursor.execute(query, (product_id, current_user, sender_id))
        conn.commit()


    """
    read_message sends an sql query to return all messages for a given conversation on a product
    by providing the current user_id, the bidder's user_id, and the product_id
    """
    def read_message(self, conn, user_id, bidder_user_id, product_id):
        query = '''SELECT 
        u.first_name,
        u.last_name,
        p.name AS product_name,
        m.message_id AS message_id,
        m.message,
        m.read,
        m.time_sent,
        m.sender_id,
        p.prod_id AS product_id,
        m.recipient_id
         FROM messages AS m
        LEFT JOIN users AS u ON u.user_id = m.sender_id 
        LEFT JOIN product AS p ON p.prod_id = m.product_id 
          WHERE 
        (sender_id = ? OR recipient_id = ?) 
        AND product_id = ? 
        ORDER BY time_sent DESC'''
        message_details = [bidder_user_id, user_id, product_id]
        # print("message details: ", message_details)
        cursor = conn.cursor()
        cursor.execute(query, message_details)
        results = list(cursor.fetchall())
        new_results = []
        for result in results:
            new_result = {
                "first_name": result[0],
                "last_name": result[1],
                "product_name": result[2],
                "message_id": result[3],
                "message": result[4],
                "read": result[5],
                "time_sent": result[6],
                "sender_id": result[7],
                "product_id": result[8],
                "recipient_id": result[9],
            }
            new_results.append(new_result)
        results = new_results
        print("got results: ", results)
        if len(results) == 0:
            return []
        else:
            self.set_messages_to_read(conn, product_id, user_id, results[0]["sender_id"])
            return results

    """
    get_messages returns a list a of the last conversation messasges for each conversation user_id is involved in
    """
    def get_messages(self, conn, user_id):
        print(user_id)
        query = '''WITH conversation_set AS (
    SELECT
        m.sender_id AS sender_id,
        m.recipient_id,
        m.product_id,
        ROW_NUMBER() OVER (PARTITION BY m.product_id ORDER BY m.message_id DESC) AS message_id_rank,
        m.message_id AS message_id
    FROM
        messages m
    WHERE
        (m.recipient_id = ? OR m.sender_id = ?)
)
SELECT
    u.first_name,
    u.last_name,
    p.name AS product_name,
    cs.message_id AS message_id,
    m.message,
    m.read,
    m.time_sent,
    p.prod_id AS product_id,
    m.recipient_id,
    m.sender_id,
    p.seller_id,
    p.deadline_date as deadline_date

FROM
    conversation_set cs
JOIN
    messages m ON cs.product_id = m.product_id AND cs.message_id_rank = 1
LEFT JOIN
    users u ON ((cs.sender_id = u.user_id AND ? != cs.sender_id) OR
                (cs.recipient_id = u.user_id AND ? != cs.recipient_id))
LEFT JOIN
    product p ON m.product_id = p.prod_id
ORDER BY m.time_sent DESC'''

        message_details = [user_id, user_id, user_id, user_id]

        cursor = conn.cursor()
        cursor.execute(query, message_details)
        results = list(cursor.fetchall())
        new_results = []
        for result in results:
            print("result: ", result)
            new_result = {
                "first_name": result[0],
                "last_name": result[1],
                "product_name": result[2],
                "message_id": result[3],
                "message": result[4],
                "read": result[5],
                "time_sent": result[6],
                "product_id": result[7],
                "recipient_id": result[8],
                "sender_id": result[9],
                "seller_id": result[10],
                "deadline_date": result[11],
            }

            # if the sender id is this user, use their first and last name
            # look up the user, and get their first and last name
            if new_result["sender_id"] == user_id:
                new_result["first_name"] = current_user.first_name
                new_result["last_name"] = current_user.last_name

            new_results.append(new_result)

        results = new_results

        if len(results) == 0:
            return {"message": "User has not messaged regarding this product."}
        else:
            return {"results": results}