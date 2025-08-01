import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

DATABASE_FILE = 'blockchain.db'
BLOCKCHAIN_FILE = 'blockchain.json'
STATE_FILE = 'state.json'
PENDING_FILE = 'pending_transactions.json'

class BlockchainStorage:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    private_key TEXT NOT NULL,
                    public_key TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blocks (
                    block_index INTEGER PRIMARY KEY,
                    block_hash TEXT NOT NULL,
                    parent_hash TEXT,
                    transaction_count INTEGER,
                    nonce INTEGER,
                    timestamp TEXT,
                    difficulty INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_index INTEGER,
                    sender TEXT,
                    receiver TEXT,
                    amount REAL,
                    transaction_hash TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (block_index) REFERENCES blocks (block_index)
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def save_user(self, username, private_key, public_key):
        """Save user to database"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (username, private_key, public_key)
                VALUES (?, ?, ?)
            ''', (username, private_key, public_key))
            conn.commit()
    
    def load_users(self):
        """Load all users from database"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT username, private_key, public_key FROM users')
            return {row['username']: {
                'private_key': row['private_key'],
                'public_key': row['public_key']
            } for row in cursor.fetchall()}
    
    def save_block_metadata(self, block, difficulty):
        """Save block metadata to database"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            content = block['content']

            cursor.execute('''
                INSERT OR REPLACE INTO blocks 
                (block_index, block_hash, parent_hash, transaction_count, nonce, timestamp, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                content['index'],
                block['hash'],
                content.get('parentHash'),
                content['transactionCount'],
                content['nonce'],
                content.get('timestamp', datetime.now().isoformat()),
                difficulty
            ))

            for transaction in content['transactions']:
                if transaction.get('transaction'):
                    tx = transaction['transaction']
                    sender = None
                    receiver = None
                    amount = 0
                    
                    for user, value in tx.items():
                        if value < 0:
                            sender = user
                            amount = abs(value)
                        elif value > 0:
                            receiver = user
                    
                    cursor.execute('''
                        INSERT INTO transactions 
                        (block_index, sender, receiver, amount, transaction_hash, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        content['index'],
                        sender,
                        receiver,
                        amount,
                        json.dumps(tx, sort_keys=True),
                        content.get('timestamp', datetime.now().isoformat())
                    ))
            
            conn.commit()
    
    def get_transaction_history(self, username=None, limit=50):
        """Get transaction history"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            if username:
                cursor.execute('''
                    SELECT * FROM transactions 
                    WHERE sender = ? OR receiver = ?
                    ORDER BY id DESC LIMIT ?
                ''', (username, username, limit))
            else:
                cursor.execute('''
                    SELECT * FROM transactions 
                    ORDER BY id DESC LIMIT ?
                ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_blockchain_stats(self):
        """Get blockchain statistics"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) as block_count FROM blocks')
            block_count = cursor.fetchone()['block_count']

            cursor.execute('SELECT COUNT(*) as tx_count FROM transactions')
            tx_count = cursor.fetchone()['tx_count']

            cursor.execute('SELECT SUM(amount) as total_volume FROM transactions')
            total_volume = cursor.fetchone()['total_volume'] or 0
            
            return {
                'block_count': block_count,
                'transaction_count': tx_count,
                'total_volume': total_volume
            }
    
    def save_blockchain(self, blockchain):
        """Save blockchain to file"""
        try:
            with open(BLOCKCHAIN_FILE, 'w') as f:
                json.dump(blockchain, f, indent=2, sort_keys=True)
            return True
        except Exception as e:
            print(f"Error saving blockchain: {e}")
            return False
    
    def load_blockchain(self):
        """Load blockchain from file"""
        try:
            if os.path.exists(BLOCKCHAIN_FILE):
                with open(BLOCKCHAIN_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading blockchain: {e}")
        return None
    
    def save_state(self, state):
        """Save current state to file"""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2, sort_keys=True)
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
    
    def load_state(self):
        """Load current state from file"""
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading state: {e}")
        return None
    
    def save_pending_transactions(self, pending_transactions):
        """Save pending transactions to file"""
        try:
            with open(PENDING_FILE, 'w') as f:
                json.dump(pending_transactions, f, indent=2, sort_keys=True)
            return True
        except Exception as e:
            print(f"Error saving pending transactions: {e}")
            return False
    
    def load_pending_transactions(self):
        """Load pending transactions from file"""
        try:
            if os.path.exists(PENDING_FILE):
                with open(PENDING_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading pending transactions: {e}")
        return []
    
    def backup_data(self, backup_dir='backups'):
        """Create backup of all data"""
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_files = {
                f'{backup_dir}/blockchain_{timestamp}.json': BLOCKCHAIN_FILE,
                f'{backup_dir}/state_{timestamp}.json': STATE_FILE,
                f'{backup_dir}/pending_{timestamp}.json': PENDING_FILE,
                f'{backup_dir}/database_{timestamp}.db': DATABASE_FILE
            }
            
            for backup_file, original_file in backup_files.items():
                if os.path.exists(original_file):
                    import shutil
                    shutil.copy2(original_file, backup_file)
            
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False