import sqlite3


class ChatService:

    try:
        conn = sqlite3.connect('auction.db', check_same_thread=False)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        print(e)

    def send_message(self, message, recipient_id, sender_id, product_id):
        query= '''INSERT INTO messages (sender_id, recipient_id, product_id, message) 
            VALUES (?, ?, ?, ?)'''
        message_details = [sender_id, recipient_id, product_id, message]

        self.cursor.execute(query, message_details)
        self.conn.commit()

        return {"message": "Message sent successfully"}

    def read_message(self, user_id, product_id):
        print((user_id, product_id))
        query = '''SELECT * FROM messages WHERE (sender_id = ? OR recipient_id = ?) AND product_id = ? ORDER BY time_sent DESC'''
        message_details = [user_id, user_id, product_id]

        self.cursor.execute(query, message_details)
        results = list(self.cursor.fetchall())
        if len(results) == 0:
            return {"message": "User has not messaged regarding this product."}
        else:
            return results

    def get_messages(self, user_id):
        query = '''SELECT DISTINCT product.prod_id AS product_id, product.name AS product_name,
            users.user_id AS user_id, users.first_name AS first_name,
            users.last_name AS last_name, messages.message AS message,
            messages.time_sent AS time_sent, messages.read AS read
        FROM messages
        JOIN users
            ON messages.recipient_id = users.user_id OR messages.sender_id = users.user_id
        JOIN product
            ON messages.product_id = product.prod_id
        WHERE
            (recipient_id = ? AND users.user_id = sender_id)  OR
            (sender_id = ? AND users.user_id = messages.recipient_id)
        GROUP BY product.prod_id, messages.sender_id, messages.recipient_id
        ORDER BY messages.time_sent DESC'''

        message_details = [user_id, user_id]

        self.cursor.execute(query, message_details)
        results = list(self.cursor.fetchall())
        if len(results) == 0:
            return {"message": "User has not messaged regarding this product."}
        else:
            return {"results": results}