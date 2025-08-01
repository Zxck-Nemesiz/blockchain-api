# Blockchain Implementation Project

A simple blockchain implementation with web API built in Python.

## Project Overview

This project implements a basic blockchain system with the following features:
- Block creation and mining
- Transaction processing
- User wallet management
- RESTful API interface
- Data persistence with SQLite

## Files Structure

```
blockchain-project/
├── main.py           # Main Flask API server
├── blockchain.py     # Core blockchain functions
├── transaction.py    # Transaction handling
├── state.py         # Blockchain state management
├── user.py          # User and wallet management
├── keys.py          # Digital signatures
├── hash_utils.py    # Hashing functions
├── storage.py       # Database operations
└── requirements.txt # Python dependencies
```

## Installation and Setup

1. **Install Python 3.7+**

2. **Install required packages:**
```bash
pip install flask
```

3. **Run the application:**
```bash
python main.py
```

4. **Access the API at:** `http://localhost:5000`

## How to Use

### 1. Start the Server
```bash
python main.py
```

### 2. Create a New User
```bash
curl -X POST http://localhost:5000/users -H "Content-Type: application/json" -d '{"username": "student1"}'
```

### 3. Check User Balance
```bash
curl http://localhost:5000/balance/alice
```

### 4. Create a Transaction
```bash
curl -X POST http://localhost:5000/transaction -H "Content-Type: application/json" -d '{"sender": "alice", "receiver": "student1", "amount": 10}'
```

### 5. Mine a Block
```bash
curl -X POST http://localhost:5000/mine
```

### 6. View the Blockchain
```bash
curl http://localhost:5000/blockchain
```

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Show all available endpoints |
| GET | `/blockchain` | Get the complete blockchain |
| GET | `/users` | List all users |
| POST | `/users` | Create a new user |
| GET | `/balance/<username>` | Check user balance |
| POST | `/transaction` | Create a new transaction |
| GET | `/pending` | View pending transactions |
| POST | `/mine` | Mine pending transactions |
| POST | `/validate` | Validate the blockchain |

## Key Concepts Implemented

### 1. Block Structure
Each block contains:
- Index (block number)
- Previous block hash
- Transactions
- Nonce (for mining)
- Block hash

### 2. Mining Process
- Uses Proof of Work algorithm
- Finds a hash starting with zeros (difficulty = 3)
- Requires computational effort to create blocks

### 3. Transaction Validation
- Checks if sender has sufficient balance
- Verifies digital signatures
- Prevents double spending

### 4. Data Persistence
- Stores blockchain in JSON files
- Uses SQLite for user and transaction data
- Automatic data loading on restart

## Example Usage Session

```bash
# 1. Start server
python main.py

# 2. Check initial users (Alice and Bob start with 100 coins each)
curl http://localhost:5000/users

# 3. Create a new user
curl -X POST http://localhost:5000/users -H "Content-Type: application/json" -d '{"username": "charlie"}'

# 4. Alice sends 10 coins to Charlie
curl -X POST http://localhost:5000/transaction -H "Content-Type: application/json" -d '{"sender": "alice", "receiver": "charlie", "amount": 10}'

# 5. Mine the transaction
curl -X POST http://localhost:5000/mine

# 6. Check Charlie's balance (should be 10)
curl http://localhost:5000/balance/charlie

# 7. Check Alice's balance (should be 90)
curl http://localhost:5000/balance/alice
```

## Technical Details

### Hashing
- Uses SHA-256 for all hash calculations
- Each block hash depends on all transactions in the block

### Digital Signatures
- Simple signature scheme using private keys
- Each transaction is signed by the sender
- Signatures are verified before processing

### Mining Difficulty
- Current difficulty: 3 (hash must start with "000")
- Can be adjusted in the code
- Higher difficulty = more secure but slower mining

## Testing

Basic test to verify functionality:
```bash
# Test blockchain creation and validation
python -c "
from blockchain import *
from user import generateKeys
from transaction import makeTransaction
import json

# Create users
generateKeys('test1')
generateKeys('test2')

# Create transaction
tx = makeTransaction('test1', 'test2', 5)
print('Transaction created successfully')

# This will test the core blockchain functions
print('All basic functions working!')
"
```

## Project Learning Outcomes

This project demonstrates understanding of:
1. **Blockchain fundamentals** - blocks, chains, hashing
2. **Cryptography** - digital signatures, hash functions
3. **Web APIs** - RESTful services with Flask
4. **Database operations** - SQLite integration
5. **Data structures** - managing blockchain state
6. **Software engineering** - modular code organization

## Limitations

This is an educational implementation with simplified:
- Cryptography (not production-secure)
- Network layer (no peer-to-peer networking)
- Transaction types (only simple transfers)

## Requirements

- Python 3.7 or higher
- Flask library
- Basic understanding of:
  - Python programming
  - HTTP requests
  - JSON data format
  - Command line usage

## Troubleshooting

**If you get "Module not found" error:**
```bash
pip install flask
```

**If port 5000 is busy:**
- Change the port in main.py: `app.run(port=5001)`

**If data seems lost:**
- Check if `.json` and `.db` files exist in project folder
- These files store your blockchain data

## Author

[Muhammad Zakuan bin Zulkarnain]  

## MIT License

This project is for educational purposes only.
