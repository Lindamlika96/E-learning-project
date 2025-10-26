import random
import string
import smtplib
from email.mime.text import MIMEText

def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_code(to_email, code):
    sender = "daoudwissal2000@gmail.com"
    password = "irba dgru woex smmg"

    msg = MIMEText(f"Bonjour,\n\nVoici votre code de vérification : {code}")
    msg["Subject"] = "Code de vérification"
    msg["From"] = sender
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
