# auth.py
import hashlib
from database import fetch_one

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(user_id, password, status):
    hashed = hash_password(password)

    row = fetch_one(
        """SELECT name FROM users 
           WHERE id=%s AND password=%s AND status=%s""",
        (user_id, hashed, status)
    )

    if row:
        return True, row[0]  # (success, name)
    return False, None
