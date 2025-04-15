import sqlite3
import smtplib
from email.mime.text import MIMEText
import tomllib
from flask import current_app as app

def send_email_notification(new_bid_info):
    try:
        conn = sqlite3.connect('auction.db', check_same_thread=False)
        c = conn.cursor()
    except sqlite3.Error as e:
        print(e)
        return
    
    c.execute("SELECT email FROM users WHERE email_opt_in = 1;")
    recipients = [row[0] for row in c.fetchall()]

    if not recipients:
        return

    subject = "🚨 New Bid Alert!"
    body = f"A new bid was placed: {new_bid_info}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "cloud@kurtw.dev"
    msg['To'] = ", ".join(recipients)

    with smtplib.SMTP(app.config['SMTP_SERVER'], 587) as server:
        server.starttls()
        server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
        server.sendmail(msg['From'], recipients, msg.as_string())

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
