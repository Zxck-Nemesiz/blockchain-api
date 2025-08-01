from flask import Flask, jsonify, request
import json, random
from datetime import datetime
import atexit

from transaction import makeTransaction
from state import updateState, isValid
from blockchain import makeBlock, checkBlockChain
from user import generateKeys, user_db
from hash_utils import hashMessage
from storage import BlockchainStorage

app = Flask(__name__)

storage = BlockchainStorage()

difficulty = 3
blockChain = []
current_state = {}
pending_transactions = []

def save_all_data():
    """Save all data to persistent storage"""
    storage.save_blockchain(blockChain)
    storage.save_state(current_state)
    storage.save_pending_transactions(pending_transactions)

def load_all_data():
    """Load all data from persistent storage"""
    global blockChain, current_state, pending_transactions, user_db
    
    loaded_users = storage.load_users()
    if loaded_users:
        user_db.update(loaded_users)
        print(f"Loaded {len(loaded_users)} users from database")
    
    loaded_blockchain = storage.load_blockchain()
    if loaded_blockchain:
        blockChain = loaded_blockchain
        print(f"Loaded blockchain with {len(blockChain)} blocks")
    
    loaded_state = storage.load_state()
    if loaded_state:
        current_state.update(loaded_state)
        print(f"Loaded state for {len(loaded_state)} users")
    
    loaded_pending = storage.load_pending_transactions()
    if loaded_pending:
        pending_transactions.extend(loaded_pending)
        print(f"Loaded {len(loaded_pending)} pending transactions")

def initialize_blockchain():
    """Initialize the blockchain with genesis block"""
    global blockChain, current_state
    
    load_all_data()
    
    if not blockChain:
        print("Creating new blockchain...")
        
        generateKeys('alice')
        generateKeys('bob')
        
        for username, user_info in user_db.items():
            storage.save_user(username, user_info['private_key'], user_info['public_key'])
        
        genesisTransaction = {
            'transaction': {'alice': 100, 'bob': 100},
            'publicKey': None,
            'signature': None
        }

        genesisBlockTransactions = [genesisTransaction]
        genesisBlockContent = {
            'index': 0,
            'parentHash': None,
            'transactionCount': 1,
            'transactions': genesisBlockTransactions,
            'nonce': 0,
            'timestamp': datetime.now().isoformat()
        }

        print("Mining genesis block...")
        while True:
            genesisBlockHash = hashMessage(genesisBlockContent)
            if genesisBlockHash.startswith('0' * difficulty):
                break
            genesisBlockContent['nonce'] += 1

        genesisBlock = {
            'hash': genesisBlockHash,
            'content': genesisBlockContent
        }
        
        blockChain = [genesisBlock]
        current_state = genesisTransaction['transaction'].copy()
        
        storage.save_block_metadata(genesisBlock, difficulty)
        
        save_all_data()
        print("Genesis block created and saved!")

@app.route('/')
def home():
    """API documentation"""
    return jsonify({
        "message": "Blockchain API with Persistent Storage",
        "endpoints": {
            "GET /": "This help message",
            "GET /blockchain": "Get the full blockchain",
            "GET /blockchain/length": "Get blockchain length",
            "GET /blockchain/stats": "Get blockchain statistics",
            "GET /block/<int:index>": "Get specific block by index",
            "GET /balance/<username>": "Get user balance",
            "GET /state": "Get current blockchain state",
            "GET /users": "Get all users",
            "GET /pending": "Get pending transactions",
            "GET /transactions": "Get transaction history",
            "GET /transactions/<username>": "Get user transaction history",
            "POST /users": "Create new user {username}",
            "POST /transaction": "Create transaction {sender, receiver, amount}",
            "POST /mine": "Mine pending transactions into a new block",
            "POST /validate": "Validate the entire blockchain",
            "POST /backup": "Create data backup",
            "POST /save": "Force save all data"
        },
        "storage_info": {
            "database_file": "blockchain.db",
            "blockchain_file": "blockchain.json",
            "state_file": "state.json",
            "pending_file": "pending_transactions.json"
        }
    })

@app.route('/blockchain/stats', methods=['GET'])
def get_blockchain_stats():
    """Get blockchain statistics"""
    stats = storage.get_blockchain_stats()
    stats.update({
        "current_block_height": len(blockChain) - 1,
        "pending_transactions": len(pending_transactions),
        "active_users": len(user_db),
        "difficulty": difficulty
    })
    return jsonify(stats)

@app.route('/transactions', methods=['GET'])
def get_all_transactions():
    """Get transaction history"""
    limit = request.args.get('limit', 50, type=int)
    transactions = storage.get_transaction_history(limit=limit)
    return jsonify({
        "transactions": transactions,
        "count": len(transactions)
    })

@app.route('/transactions/<username>', methods=['GET'])
def get_user_transactions(username):
    """Get user transaction history"""
    limit = request.args.get('limit', 50, type=int)
    transactions = storage.get_transaction_history(username=username, limit=limit)
    return jsonify({
        "username": username,
        "transactions": transactions,
        "count": len(transactions)
    })

@app.route('/backup', methods=['POST'])
def create_backup():
    """Create data backup"""
    if storage.backup_data():
        return jsonify({"message": "Backup created successfully"})
    else:
        return jsonify({"error": "Backup failed"}), 500

@app.route('/save', methods=['POST'])
def force_save():
    """Force save all data"""
    try:
        save_all_data()
        return jsonify({"message": "All data saved successfully"})
    except Exception as e:
        return jsonify({"error": f"Save failed: {str(e)}"}), 500

@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    """Get the full blockchain"""
    return jsonify({
        "blockchain": blockChain,
        "length": len(blockChain)
    })

@app.route('/blockchain/length', methods=['GET'])
def get_blockchain_length():
    """Get blockchain length"""
    return jsonify({"length": len(blockChain)})

@app.route('/block/<int:index>', methods=['GET'])
def get_block(index):
    """Get specific block by index"""
    if index < 0 or index >= len(blockChain):
        return jsonify({"error": "Block index out of range"}), 404
    
    return jsonify({"block": blockChain[index]})

@app.route('/balance/<username>', methods=['GET'])
def get_balance(username):
    """Get user balance"""
    balance = current_state.get(username, 0)
    return jsonify({
        "username": username,
        "balance": balance
    })

@app.route('/state', methods=['GET'])
def get_state():
    """Get current blockchain state"""
    return jsonify({"state": current_state})

@app.route('/users', methods=['GET'])
def get_users():
    """Get all users"""
    users = []
    for username in user_db:
        users.append({
            "username": username,
            "balance": current_state.get(username, 0),
            "public_key": user_db[username]['public_key']
        })
    return jsonify({"users": users})

@app.route('/users', methods=['POST'])
def create_user():
    """Create new user"""
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({"error": "Username required"}), 400
    
    username = data['username']
    if username in user_db:
        return jsonify({"error": "User already exists"}), 400
    
    priv_key, pub_key = generateKeys(username)
    current_state[username] = 0
    
    storage.save_user(username, priv_key, pub_key)
    save_all_data()
    
    return jsonify({
        "message": f"User {username} created successfully",
        "username": username,
        "public_key": pub_key,
        "balance": 0
    })

@app.route('/pending', methods=['GET'])
def get_pending_transactions():
    """Get pending transactions"""
    return jsonify({
        "pending_transactions": pending_transactions,
        "count": len(pending_transactions)
    })

@app.route('/transaction', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    data = request.get_json()
    if not data or not all(k in data for k in ('sender', 'receiver', 'amount')):
        return jsonify({"error": "sender, receiver, and amount required"}), 400
    
    sender = data['sender']
    receiver = data['receiver']
    amount = data['amount']

    if sender not in user_db:
        return jsonify({"error": f"Sender {sender} does not exist"}), 400
    
    if receiver not in user_db:
        return jsonify({"error": f"Receiver {receiver} does not exist"}), 400
    
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
    
    if current_state.get(sender, 0) < amount:
        return jsonify({"error": "Insufficient balance"}), 400
    
    try:
        transaction = {sender: -amount, receiver: amount}
        message = json.dumps(transaction, sort_keys=True)
        
        from user import getPrivateKey, getPublicKey
        from keys import signMessage
        
        priv_key = getPrivateKey(sender)
        pub_key = getPublicKey(sender)
        signature = signMessage(message, priv_key)
        
        signed_transaction = {
            'transaction': transaction,
            'publicKey': pub_key,
            'signature': signature,
            'timestamp': datetime.now().isoformat()
        }
        
        if isValid(current_state, signed_transaction):
            pending_transactions.append(signed_transaction)
            save_all_data()
            return jsonify({
                "message": "Transaction created and added to pending pool",
                "transaction": signed_transaction
            })
        else:
            return jsonify({"error": "Invalid transaction"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Transaction creation failed: {str(e)}"}), 500

@app.route('/mine', methods=['POST'])
def mine_block():
    """Mine pending transactions into a new block"""
    global current_state, pending_transactions
    
    if not pending_transactions:
        return jsonify({"error": "No pending transactions to mine"}), 400
    
    valid_transactions = []
    temp_state = current_state.copy()
    
    for transaction in pending_transactions:
        if isValid(temp_state, transaction):
            valid_transactions.append(transaction)
            temp_state = updateState(temp_state, transaction['transaction'])
    
    if not valid_transactions:
        return jsonify({"error": "No valid transactions to mine"}), 400
    
    try:
        block = makeBlock(blockChain, valid_transactions, difficulty)
        blockChain.append(block)
        
        storage.save_block_metadata(block, difficulty)
        
        for transaction in valid_transactions:
            current_state = updateState(current_state, transaction['transaction'])
        
        for transaction in valid_transactions:
            if transaction in pending_transactions:
                pending_transactions.remove(transaction)
        
        save_all_data()
        
        return jsonify({
            "message": f"Block mined successfully with {len(valid_transactions)} transactions",
            "block": block,
            "transactions_mined": len(valid_transactions),
            "remaining_pending": len(pending_transactions)
        })
        
    except Exception as e:
        return jsonify({"error": f"Mining failed: {str(e)}"}), 500

@app.route('/validate', methods=['POST'])
def validate_blockchain():
    """Validate the entire blockchain"""
    try:
        chain_json = json.dumps(blockChain, sort_keys=True)
        final_state = checkBlockChain(chain_json, difficulty)
        return jsonify({
            "valid": True,
            "message": "Blockchain is valid",
            "final_state": final_state
        })
    except Exception as e:
        return jsonify({
            "valid": False,
            "error": str(e)
        }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

atexit.register(save_all_data)

if __name__ == '__main__':
    initialize_blockchain()
    print("Blockchain with persistent storage initialized successfully!")
    print("Starting Flask API server...")
    print("Access the API at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)