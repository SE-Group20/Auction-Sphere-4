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
        (m.recipient_id = ? OR m.sender_id ?)
)
SELECT
    u.first_name,
    u.last_name,
    p.name AS product_name,
    cs.message_id AS message_id,
    m.message,
    m.read,
    m.time_sent

FROM
    conversation_set cs
JOIN
    messages m ON cs.product_id = m.product_id AND cs.message_id_rank = 1
LEFT JOIN
    users u ON (cs.sender_id IN (SELECT user_id FROM users) OR cs.recipient_id IN (SELECT user_id FROM users)) = (SELECT first_name FROM users WHERE last_name = u.last_name)
LEFT JOIN
    product p ON m.product_id = p.prod_id
ORDER BY m.time_sent DESC'''

        message_details = [user_id, user_id]

        self.cursor.execute(query, message_details)
        results = list(self.cursor.fetchall())
        if len(results) == 0:
            return {"message": "User has not messaged regarding this product."}
        else:
            return {"results": results}