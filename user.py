import hashlib

user_db = {}

def generateKeys(name):
    priv_key = f"{name}_private"
    pub_key = hashlib.sha256(priv_key.encode()).hexdigest()
    user_db[name] = {
        'private_key': priv_key,
        'public_key': pub_key
    }
    return priv_key, pub_key

def getPublicKey(name):
    return user_db[name]['public_key']

def getPrivateKey(name):
    return user_db[name]['private_key']