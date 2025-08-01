import random, json
from user import getPrivateKey, getPublicKey
from keys import signMessage

def makeTransaction(sender, receiver, maxValue=3):
    value = random.randint(1, maxValue)
    transaction = {sender: -value, receiver: value}
    message = json.dumps(transaction, sort_keys=True)
    
    priv_key = getPrivateKey(sender)
    pub_key = getPublicKey(sender)
    signature = signMessage(message, priv_key)
    
    return {
        'transaction': transaction,
        'publicKey': pub_key,
        'signature': signature
    }

