import json
from keys import verifySign

def updateState(state, transaction):
    newState = state.copy()
    for key in transaction:
        newState[key] = newState.get(key, 0) + transaction[key]
    return newState

def isValid(state, signedTransaction):
    transaction = signedTransaction['transaction']
    publicKey = signedTransaction['publicKey']
    signature = signedTransaction['signature']
    
    if sum(transaction.values()) != 0:
        return False
    
    for key in transaction:
        if state.get(key, 0) + transaction[key] < 0:
            return False
        
    message = json.dumps(transaction, sort_keys=True)
    if not verifySign(message, signature, publicKey):
        return False
    
    return True