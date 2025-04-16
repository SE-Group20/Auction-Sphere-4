import sqlite3
import smtplib
from email.mime.text import MIMEText
import tomllib
from flask import current_app as app

def send_email_notification(new_bid_info):
    try:
        database_file = app.config['DATABASE']
        conn = sqlite3.connect(database_file, check_same_thread=False)
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
        # verify that we're connected to the server
        # https://stackoverflow.com/a/14678470
        try:
            status = server.noop()[0]
        except:
            status = -1

        if status != 250:
            if not app.testing:
                print("Server not connected - email will not be sent")
                # try anyway?
            else:
                # testing mode, skip
                return
        # start TLS for security
        server.starttls()
        server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
        server.sendmail(msg['From'], recipients, msg.as_string())
