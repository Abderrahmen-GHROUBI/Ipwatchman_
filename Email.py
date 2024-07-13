import smtplib
from config import config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


config = config()

smtp_server = config['email']['smtp_server']
port = config['email']['port']
username = config['email']['username']
password = config['email']['password']

def send_email(subject, message, to_email):
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(username, password)
        server.sendmail(username, to_email, msg.as_string())
        print(f"Email sent successfully to {to_email}")

    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        server.quit()
