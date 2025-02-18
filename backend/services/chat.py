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
        print(results)
        if len(results) == 0:
            return {"message": "User has not messaged regarding this product."}
        else:
            return results