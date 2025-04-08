import sqlite3

# TODO: this is never used!
class NotificationService:
    try:
        conn = sqlite3.connect('auction.db', check_same_thread=False)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        print(e)

    def get_user_notifications(self,user_id):
        print(user_id)
        query = '''SELECT message,detail_page,time_sent 
                    FROM notifications 
                    WHERE user_id = ? AND read = FALSE'''
        message_details = [user_id]
        
        self.cursor.execute(query, message_details)
        results = list(self.cursor.fetchall())
        print(results)
        if len(results) == 0:
            return {"notifications": "[]"}
        else:
            return {"notifications": results}