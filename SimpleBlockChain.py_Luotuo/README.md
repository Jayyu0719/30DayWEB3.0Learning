# Python Blockchain Implementation

This is a Python conversion of the JavaScript blockchain demo from the LuotuoCoin project. It implements a complete cryptocurrency blockchain with digital signatures, proof-of-work mining, and transaction validation.

## Features

- **Digital Signatures**: Uses elliptic curve cryptography (SECP256K1) for transaction signing
- **Proof-of-Work Mining**: Adjustable difficulty mining algorithm
- **Transaction Validation**: Verifies transaction signatures and integrity
- **Blockchain Integrity**: Validates the entire chain for tampering
- **Mining Rewards**: Automatic miner reward system
- **Transaction Pool**: Manages pending transactions

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from BlockchainDemoPY import Chain, Transaction, generate_key_pair

# Create blockchain with difficulty 4
blockchain = Chain(difficulty=4)

# Generate key pairs for users
private_key1, address1 = generate_key_pair()
private_key2, address2 = generate_key_pair()
miner_address = generate_key_pair()[1]

# Create and sign a transaction
transaction = Transaction(address1, address2, 100)
transaction.sign(private_key1)

# Add transaction to pool
blockchain.add_transaction(transaction)

# Mine the transaction pool
blockchain.mine_transaction_pool(miner_address)

# Validate the chain
is_valid = blockchain.validate_chain()
print(f"Blockchain is valid: {is_valid}")
```

### Running the Demo

Simply run the Python file to see a complete demo:

```bash
python BlockchainDemoPY.py
```

## Classes

### Transaction
- `__init__(from_address, to_address, amount)`: Create a new transaction
- `compute_hash()`: Generate SHA256 hash of transaction data
- `sign(private_key)`: Sign the transaction with a private key
- `is_valid()`: Verify the transaction signature

### Block
- `__init__(transactions, previous_hash)`: Create a new block
- `compute_hash()`: Generate SHA256 hash of block data
- `mine(difficulty)`: Perform proof-of-work mining
- `validate_transactions()`: Verify all transactions in the block

### Chain
- `__init__(difficulty)`: Create a new blockchain
- `add_transaction(transaction)`: Add transaction to the pool
- `mine_transaction_pool(miner_address)`: Mine all pending transactions
- `validate_chain()`: Verify the entire blockchain integrity
- `set_difficulty(difficulty)`: Adjust mining difficulty

## Key Differences from JavaScript Version

1. **Cryptography Library**: Uses Python's `cryptography` library instead of `elliptic`
2. **Type Hints**: Added Python type hints for better code clarity
3. **Error Handling**: Uses Python exceptions instead of JavaScript errors
4. **JSON Serialization**: Uses Python's `json` module for data serialization
5. **Key Generation**: Includes utility function for generating key pairs

## Security Features

- **Digital Signatures**: All transactions are cryptographically signed
- **Hash Verification**: Block integrity is verified through hash checking
- **Chain Validation**: Complete blockchain validation prevents tampering
- **Transaction Pool**: Pending transactions are validated before mining

## Mining Algorithm

The proof-of-work algorithm finds a hash that starts with a specified number of zeros (difficulty). The higher the difficulty, the more computational work is required to mine a block.

## Example Output

```
Address 1: 02a1b2c3d4e5f6...
Address 2: 02f6e5d4c3b2a1...
Miner Address: 021234567890ab...
{'from_address': '02a1b2c3d4e5f6...', 'to_address': '02f6e5d4c3b2a1...', 'amount': 100, 'signature': b'...'}
Mining completed: 0000a1b2c3d4e5f6...
Blockchain is valid: True
Blockchain length: 2
Latest block hash: 0000a1b2c3d4e5f6...
```
