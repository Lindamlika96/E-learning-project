import smtplib
from email.mime.text import MIMEText

sender = "daoudwissal2000@gmail.com"
password = "irba dgru woex smmg"  # sans espaces
to_email = "daoudwissal2000@gmail.com"

msg = MIMEText("Ceci est un test depuis FastAPI")
msg["Subject"] = "Test SMTP"
msg["From"] = sender
msg["To"] = to_email

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
    print("✅ Email envoyé")
except Exception as e:
    print("❌ Erreur SMTP :", e)
