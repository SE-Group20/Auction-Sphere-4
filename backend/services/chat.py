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

        return "Message sent successfully"
