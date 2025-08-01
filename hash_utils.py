def hashMessage(message):
    import hashlib, json
    if type(message) != str:
        message = json.dumps(message, sort_keys=True)
    return hashlib.sha256(str(message).encode('utf-8')).hexdigest()