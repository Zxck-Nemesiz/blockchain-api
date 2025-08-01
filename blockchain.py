from hash_utils import hashMessage
from state import isValid, updateState

def makeBlock(blockChain, transactions, difficulty=2):
    parentBlock = blockChain[-1]
    parentBlockHash = parentBlock['hash']
    blockContent = {
        'index': len(blockChain),
        'parentHash': parentBlockHash,
        'transactionCount': len(transactions),
        'transactions': transactions,
        'nonce': 0
    }
    
    while True:
        blockHash = hashMessage(blockContent)
        if blockHash.startswith('0' * difficulty):
            break
        blockContent['nonce'] += 1
    
    return {'hash': blockHash, 'content': blockContent}

def checkBlockHash(block, difficulty=2):
    expectedHash = hashMessage(block['content'])
    if expectedHash != block['hash']:
        raise Exception(f"Block hash is invalid: block {block['content']['index']}")
    if not block['hash'].startswith('0' * difficulty):
        raise Exception(f"Block hash does not meet difficulty at index {block['content']['index']}")

def checkBlockValidity(block, parentBlock, state, difficulty=2):
    checkBlockHash(block, difficulty)
    if block['content']['index'] != parentBlock['content']['index'] + 1:
        raise Exception(f"Block index is invalid: block {block['content']['index']}")
    if block['content']['parentHash'] != parentBlock['hash']:
        raise Exception(f"Block parent hash is invalid: block {block['content']['index']}")
    
    temp_state = state.copy()
    
    for transaction in block['content']['transactions']:
        if 'transaction' not in transaction:
            print("Malformed transaction:", transaction)
            raise Exception("Missing 'transaction' field")

        if not isValid(temp_state, transaction):
            raise Exception(f"Block contains invalid transaction at index {block['content']['index']}")
        temp_state = updateState(temp_state, transaction['transaction'])
        
    return temp_state

def checkBlockChain(blockChain, difficulty=2):
    import json
    if not blockChain:
        raise Exception("Block chain is empty")

    if isinstance(blockChain, str):
        try:
            blockChain = json.loads(blockChain)
        except:
            raise Exception("Block chain is not a valid JSON object")

    if not isinstance(blockChain, list):
        raise Exception("Block chain is not a list")

    genesis_transaction = blockChain[0]['content']['transactions'][0]
    state = genesis_transaction['transaction'].copy()

    checkBlockHash(blockChain[0], difficulty)
    parent = blockChain[0]

    for block in blockChain[1:]:
        try:
            state = checkBlockValidity(block, parent, state, difficulty)
        except Exception as e:
            raise Exception(f"Block {block['content']['index']} is invalid: {e}")
        parent = block

    return state
