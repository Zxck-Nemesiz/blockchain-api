import hashlib
from user import user_db

def signMessage(message, priv_key):
    return hashlib.sha256((message + priv_key).encode()).hexdigest()

def verifySign(message, signature, pub_key):
    for user_info in user_db.values():
        priv_key = user_info['private_key']
        expected_public = hashlib.sha256(priv_key.encode()).hexdigest()
        if expected_public == pub_key:
            expected_sign = hashlib.sha256((message + priv_key).encode()).hexdigest()
            return expected_sign == signature
    return False
        