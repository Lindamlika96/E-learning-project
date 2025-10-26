import math
from collections import Counter

# Liste d'exemples de domaines jetables
DISPOSABLE_DOMAINS = {
    "yopmail.com", "mailinator.com", "tempmail.com", "10minutemail.com"
}

# Liste d'exemples de mots blacklistés
BLACKLIST = {"killer", "admin", "root", "test", "hack", "xxx"}


def entropy(s: str) -> float:
    """Calcule l'entropie d'une chaîne"""
    if not s:
        return 0.0
    probs = [freq / len(s) for freq in Counter(s).values()]
    return round(-sum(p * math.log2(p) for p in probs), 3)


def ratio_digits(s: str) -> float:
    return round(sum(c.isdigit() for c in s) / len(s), 3) if s else 0.0


def ratio_alpha(s: str) -> float:
    return round(sum(c.isalpha() for c in s) / len(s), 3) if s else 0.0


def ratio_vowels(s: str) -> float:
    return round(sum(c.lower() in "aeiouy" for c in s) / len(s), 3) if s else 0.0


def has_nonlatin(s: str) -> int:
    return int(any(ord(c) > 127 for c in s))


def is_blacklisted(s: str) -> int:
    s_lower = s.lower()
    return int(any(bad in s_lower for bad in BLACKLIST))


def is_disposable(email: str) -> int:
    domain = email.split("@")[-1].lower() if email and "@" in email else ""
    return int(domain in DISPOSABLE_DOMAINS)


def domain_known(email: str) -> int:
    """Retourne 1 si le domaine est connu (gmail, yahoo, outlook, hotmail, icloud), sinon 0"""
    known = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "live.com"}
    domain = email.split("@")[-1].lower() if email and "@" in email else ""
    return int(domain in known)


def username_email_similarity(username: str, email: str) -> float:
    """Mesure la similarité entre username et la partie locale de l'email"""
    if not username or not email or "@" not in email:
        return 0.0
    local = email.split("@")[0].lower()
    u = username.lower()
    common = sum(1 for c in u if c in local)
    return round(common / max(len(u), len(local)), 3)


def build_features(username: str, email: str, full_name: str, time_to_submit_ms: float = 60000.0) -> dict:
    """
    Construit un dictionnaire de features à partir des infos utilisateur.
    """
    local = email.split("@")[0] if email and "@" in email else ""
    return {
        "is_disposable_domain": is_disposable(email),
        "is_known_domain": domain_known(email),
        "digits_ratio_local": ratio_digits(local),
        "local_entropy": entropy(local),
        "alpha_ratio": ratio_alpha(username),
        "vowel_ratio": ratio_vowels(full_name),
        "nonlatin_flag": has_nonlatin(full_name),
        "blacklist_hit": is_blacklisted(username),
        "username_length": len(username) if username else 0,
        "similarity_username_email": username_email_similarity(username, email)
    }
