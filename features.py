def extract_features(df):
    df = df.copy()
    df["email_length"] = df["email"].apply(len)
    df["has_number"] = df["username"].apply(lambda x: int(any(c.isdigit() for c in x)))
    df["name_length"] = df["full_name"].apply(len)
    df["suspicious_words"] = df["username"].apply(lambda x: int(any(w in x.lower() for w in ["bot", "free", "$", "test", "fake"])))
    return df[["email_length", "has_number", "name_length", "suspicious_words"]]
