#!/usr/bin/env python3
"""
Basic blockchain functionality test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain import makeBlock, checkBlockChain
from transaction import makeTransaction
from user import generateKeys
from hash_utils import hashMessage
import json

def test_basic_functionality():
    print("Testing basic blockchain functionality...")
    
    # Generate users
    print("1. Generating users...")
    generateKeys('alice')
    generateKeys('bob')
    
    # Create genesis block
    print("2. Creating genesis block...")
    genesis_tx = {
        'transaction': {'alice': 50, 'bob': 50},
        'publicKey': None,
        'signature': None
    }
    
    genesis_content = {
        'index': 0,
        'parentHash': None,
        'transactionCount': 1,
        'transactions': [genesis_tx],
        'nonce': 0
    }
    
    # Mine genesis
    while True:
        genesis_hash = hashMessage(genesis_content)
        if genesis_hash.startswith('00'):  
            break
        genesis_content['nonce'] += 1
    
    genesis_block = {'hash': genesis_hash, 'content': genesis_content}
    blockchain = [genesis_block]
    
    # Create transactions
    print("3. Creating transactions...")
    transactions = []
    for i in range(3):
        tx = makeTransaction('alice', 'bob', 1)
        transactions.append(tx)
    
    # Mine block
    print("4. Mining block...")
    block = makeBlock(blockchain, transactions, difficulty=2)
    blockchain.append(block)
    
    # Validate blockchain
    print("5. Validating blockchain...")
    chain_json = json.dumps(blockchain, sort_keys=True)
    final_state = checkBlockChain(chain_json, difficulty=2)
    print(f"   Final state: {final_state}")
    
    print("All tests passed!")

if __name__ == "__main__":
    test_basic_functionality()