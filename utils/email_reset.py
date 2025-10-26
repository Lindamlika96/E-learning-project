import random
from utils.send_email import send_email  # ton utilitaire existant

def generate_reset_code():
    return str(random.randint(100000, 999999))

def send_reset_code(email: str, username: str, code: str):
    subject = "🔐 Réinitialisation du mot de passe"
    body = f"""
Bonjour {username},

Voici votre code de réinitialisation : {code}

Ce code est valable 10 minutes.
Si vous n'avez pas demandé cela, ignorez ce message.
"""
    send_email(email, subject, body)
