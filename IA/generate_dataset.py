import pandas as pd
import random

# Nombre de lignes à générer
N = 2000  

# Quelques bases pour générer des données réalistes
usernames = ["wissal", "student", "bot", "spammer", "normal", "test", "alpha", "beta", "gamma", "user"]
domains_legit = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "example.com"]
domains_spam = ["tempmail.com", "spam.com", "fraud.net", "fake.org"]

rows = []
for i in range(N):
    base = random.choice(usernames)
    username = f"{base}{i}"
    
    # Choisir domaine
    if random.random() < 0.3:  # 30% de chance que ce soit un domaine spam
        domain = random.choice(domains_spam)
    else:
        domain = random.choice(domains_legit)
    
    email = f"{username}@{domain}"
    full_name = f"User {i}"
    time_to_submit_ms = random.randint(100, 3000)

    # Règles pour label
    if domain in domains_spam or time_to_submit_ms < 400:
        label = 1  # spam/risky
    else:
        label = 0  # normal

    rows.append([username, email, full_name, time_to_submit_ms, label])

# Sauvegarde en CSV
df = pd.DataFrame(rows, columns=["username", "email", "full_name", "time_to_submit_ms", "label"])
df.to_csv("IA/emails_dataset.csv", index=False, encoding="utf-8")

print("✅ Dataset généré avec succès : IA/emails_dataset.csv (2000 lignes)")
