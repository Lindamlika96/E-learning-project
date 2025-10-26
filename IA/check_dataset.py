import pandas as pd

# Lis ton fichier comme un CSV (même si l'extension est .xlsx)
df = pd.read_csv("emails.csv", encoding="latin-1")

print(df.head())
print(df.columns)
