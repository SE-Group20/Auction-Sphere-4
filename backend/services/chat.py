import sqlite3


class ChatService:

    try:
        conn = sqlite3.connect('auction.db', check_same_thread=False)
    except sqlite3.Error as e:
        print(e)

    """
    send_message adds a new message to the messages table using the provided parameters of
    message, recipient_id, sender_id, product_id
    """
    def send_message(self, message, recipient_id, sender_id, product_id):
        query= '''INSERT INTO messages (sender_id, recipient_id, product_id, message) 
            VALUES (?, ?, ?, ?)'''
        message_details = [sender_id, recipient_id, product_id, message]
        cursor = self.conn.cursor()
        cursor.execute(query, message_details)
        self.conn.commit()

        return {"message": "Message sent successfully"}

    """
    user_is_product_seller tests if user_id is the user_id of the specified product
    """
    def user_is_product_seller(self, product_id, user_id):
        query= '''SELECT EXISTS(SELECT 1 FROM product WHERE prod_id = ? AND seller_id = ?)'''
        cursor = self.conn.cursor()
        cursor.execute(query, (product_id, user_id))
        return cursor.fetchone()[0]

    """
    set_messages_to_read sets the status of mesesages to read given the user ids
    """
    def set_messages_to_read(self, product_id, current_user, sender_id):
        query = '''UPDATE messages SET read = 1 WHERE product_id = ? AND recipient_id = ? AND sender_id = ?'''
        cursor = self.conn.cursor()
        cursor.execute(query, (product_id, current_user, sender_id))
        self.conn.commit()


    """
    read_message sends an sql query to return all messages for a given conversation on a product
    by providing the current user_id, the bidder's user_id, and the product_id
    """
    def read_message(self, user_id, bidder_user_id, product_id):
        query = '''SELECT 
        u.first_name,
        u.last_name,
        p.name AS product_name,
        m.message_id AS message_id,
        m.message,
        m.read,
        m.time_sent,
        m.sender_id,
        p.prod_id AS product_id
         FROM messages AS m
        LEFT JOIN users AS u ON u.user_id = m.sender_id 
        LEFT JOIN product AS p ON p.prod_id = m.product_id 
          WHERE 
        (sender_id = ? OR recipient_id = ?) 
        AND product_id = ? 
        ORDER BY time_sent DESC'''
        message_details = [bidder_user_id, user_id, product_id]
        print("message details: ", message_details)
        cursor = self.conn.cursor()
        cursor.execute(query, message_details)
        results = list(cursor.fetchall())
        print("got results: ", results)
        if len(results) == 0:
            return []
        else:
            self.set_messages_to_read(product_id, user_id, results[0][7])
            return results

    """
    get_messages returns a list a of the last conversation messasges for each conversation user_id is involved in
    """
    def get_messages(self, user_id):
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

        cursor = self.conn.cursor()
        cursor.execute(query, message_details)
        results = list(cursor.fetchall())

        if len(results) == 0:
            return {"message": "User has not messaged regarding this product."}
        else:
            return {"results": results}