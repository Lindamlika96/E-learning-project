import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "daoudwissal2000@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "irba dgru woex smmg")  # utilise un mot de passe d'application Gmail

def send_welcome_email(to_email: str, username: str):
    subject = "Bienvenue sur notre plateforme 🎉"
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color:#f9f9f9; padding:20px;">
        <div style="max-width:600px; margin:auto; background:white; padding:20px; border-radius:8px;">
          <h2 style="color:#4CAF50;">Bienvenue {username} 👋</h2>
          <p>Nous sommes ravis de vous compter parmi nous sur notre plateforme 🎓.</p>
          <p>Vous pouvez dès maintenant vous connecter et explorer toutes les fonctionnalités.</p>
          <a href="http://127.0.0.1:3000/login" 
             style="display:inline-block; padding:10px 20px; background:#4CAF50; color:white; text-decoration:none; border-radius:5px;">
             Se connecter
          </a>
          <p style="margin-top:20px; font-size:12px; color:#888;">À très vite,<br>L'équipe Support</p>
        </div>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_USERNAME
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            print(f"✅ Email envoyé à {to_email}")
    except Exception as e:
        print("❌ Erreur envoi email :", e)
