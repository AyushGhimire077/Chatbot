import smtplib
from dotenv import load_dotenv
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException


load_dotenv()

USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASS = os.getenv("USER_PASS")

if not USER_EMAIL or not USER_PASS:
    raise ValueError("USER_EMAIL or USER_PASS environment variable is not set")

def sendMail(to, subject, body):
    print("to", to, )
    print("subject", subject)
    print("body", body)
    try:
        if not to or not subject or not body:
            raise ValueError("Invalid email parameters")
        
        message = MIMEMultipart()
        message['From'] = USER_EMAIL
        message['To'] = to
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(USER_EMAIL, USER_PASS)
        text = message.as_string()
        server.sendmail(USER_EMAIL, to, text)
        print("Email sent successfully")
        server.quit()
        
        return True
    except Exception as e:
        print("Error sending email:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    