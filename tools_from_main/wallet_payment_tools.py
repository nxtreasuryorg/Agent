"""
Wallet Payment Tools - Extracted from NxTreasury Application
These tools provide cryptocurrency wallet and payment functionality for CrewAI agents.
"""

import os
import json
import secrets
import requests
from datetime import datetime, timedelta
from web3 import Web3
from web3.exceptions import (
    TransactionNotFound, TimeExhausted, MismatchedABI, 
    InvalidTransaction, BlockNotFound, InvalidAddress, ValidationError
)
from cryptography.fernet import Fernet


class WalletPaymentTools:
    """
    A comprehensive toolkit for cryptocurrency wallet operations and payments.
    Supports ETH and USDT transactions on Ethereum mainnet.
    """
    
    def __init__(self, infura_key=None, fernet_key=None, usdt_contract_address=None):
        """
        Initialize the wallet payment tools.
        
        Args:
            infura_key (str): Infura API key for Ethereum connection
            fernet_key (str): Encryption key for private key storage
            usdt_contract_address (str): USDT contract address (defaults to mainnet)
        """
        self.infura_key = infura_key or os.getenv('INFURA_API_KEY')
        self.fernet_key = fernet_key or os.getenv('FERNET_KEY')
        self.usdt_contract_address = usdt_contract_address or '0xdAC17F958D2ee523a2206206994597C13D831ec7'
        
        # Initialize Web3
        self.w3 = None
        self.usdt_contract = None
        self.cipher_suite = None
        
        # Transaction settings
        self.max_usdt_gas = 401000
        self.max_eth_gas = 200000
        self.min_eth_balance_for_transaction = 0.0005
        
        self._initialize_web3()
        self._initialize_encryption()
        self._load_usdt_contract()
    
    def _initialize_web3(self):
        """Initialize Web3 connection to Ethereum mainnet."""
        if not self.infura_key:
            raise ValueError("Infura API key is required")
        
        self.w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{self.infura_key}'))
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Ethereum node")
        print("Connected to Ethereum mainnet")
    
    def _initialize_encryption(self):
        """Initialize Fernet encryption for private key storage."""
        if not self.fernet_key:
            raise ValueError("Fernet key is required for encryption")
        
        if isinstance(self.fernet_key, str):
            self.fernet_key = self.fernet_key.encode()
        
        self.cipher_suite = Fernet(self.fernet_key)
    
    def _load_usdt_contract(self):
        """Load USDT contract ABI and initialize contract instance."""
        # USDT contract ABI (simplified version with essential functions)
        usdt_abi = [
            {
                "constant": True,
                "inputs": [{"name": "who", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [],
                "type": "function"
            }
        ]
        
        self.usdt_contract = self.w3.eth.contract(
            address=self.usdt_contract_address, 
            abi=usdt_abi
        )
    
    def create_new_wallet(self):
        """
        Create a new Ethereum wallet with encrypted private key.
        
        Returns:
            tuple: (public_address, encrypted_private_key)
        """
        account = self.w3.eth.account.create()
        public_address = account.address
        private_key_hex = Web3.to_hex(account._private_key)
        
        # Encrypt the private key
        encrypted_private_key = self.cipher_suite.encrypt(private_key_hex.encode()).decode()
        
        return public_address, encrypted_private_key
    
    def decrypt_private_key(self, encrypted_key):
        """
        Decrypt a private key.
        
        Args:
            encrypted_key (str): Encrypted private key
            
        Returns:
            str: Decrypted private key or None if decryption fails
        """
        try:
            decrypted_key = self.cipher_suite.decrypt(encrypted_key.encode()).decode()
            return decrypted_key
        except Exception as e:
            print(f"Error decrypting private key: {str(e)}")
            return None
    
    def get_gas_price_gwei(self):
        """
        Get current gas price in Gwei.
        
        Returns:
            float: Gas price in Gwei
        """
        if not self.w3.is_connected():
            return None
        
        gas_price = self.w3.eth.gas_price
        gas_price_gwei = self.w3.from_wei(gas_price, 'gwei')
        return float(gas_price_gwei)
    
    def get_eth_balance(self, wallet_address):
        """
        Get ETH balance for a wallet address.
        
        Args:
            wallet_address (str): Ethereum wallet address
            
        Returns:
            tuple: (eth_balance, usd_value) or (None, None) if error
        """
        if not self.w3.is_connected():
            return None, None
        
        try:
            address = Web3.to_checksum_address(wallet_address)
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            
            # Get ETH price (optional - you might want to implement your own price feed)
            try:
                response = requests.get(
                    'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd',
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    eth_price = data['ethereum']['usd']
                    usd_value = float(balance_eth) * eth_price
                else:
                    usd_value = None
            except:
                usd_value = None
            
            return float(balance_eth), usd_value
        except Exception as e:
            print(f"Error getting ETH balance: {str(e)}")
            return None, None
    
    def get_usdt_balance(self, wallet_address):
        """
        Get USDT balance for a wallet address.
        
        Args:
            wallet_address (str): Ethereum wallet address
            
        Returns:
            float: USDT balance or None if error
        """
        if not self.w3.is_connected():
            return None
        
        try:
            address = Web3.to_checksum_address(wallet_address)
            balance_wei = self.usdt_contract.functions.balanceOf(address).call()
            balance_usdt = balance_wei / 10**6  # USDT has 6 decimal places
            return float(balance_usdt)
        except Exception as e:
            print(f"Error getting USDT balance: {str(e)}")
            return None
    
    def transfer_eth(self, from_private_key, to_address, amount_eth, gas_price_gwei=None):
        """
        Transfer ETH from one address to another.
        
        Args:
            from_private_key (str): Private key of sender (decrypted)
            to_address (str): Recipient address
            amount_eth (float): Amount of ETH to send
            gas_price_gwei (float): Gas price in Gwei (optional)
            
        Returns:
            str: Transaction hash or None if failed
        """
        try:
            # Create account from private key
            account = self.w3.eth.account.from_key(from_private_key)
            
            # Validate addresses
            recipient_address = Web3.to_checksum_address(to_address)
            
            # Check minimum amount
            if amount_eth < 0.0001:
                print(f"Amount too low: {amount_eth} ETH")
                return None
            
            # Get gas price
            if gas_price_gwei is None:
                gas_price_gwei = self.get_gas_price_gwei()
                if gas_price_gwei is None:
                    print("Could not get gas price")
                    return None
                gas_price_gwei = round(gas_price_gwei * 1.15)  # Add 15% buffer
            
            # Check balance
            balance_wei = self.w3.eth.get_balance(account.address)
            amount_wei = Web3.to_wei(amount_eth, 'ether')
            gas_cost = self.w3.to_wei(gas_price_gwei, 'gwei') * self.max_eth_gas
            
            if balance_wei < (amount_wei + gas_cost):
                print(f"Insufficient balance. Need: {self.w3.from_wei(amount_wei + gas_cost, 'ether')} ETH")
                return None
            
            # Build transaction
            transaction = {
                'chainId': 1,  # Ethereum mainnet
                'to': recipient_address,
                'value': amount_wei,
                'gas': self.max_eth_gas,
                'maxFeePerGas': self.w3.to_wei(str(gas_price_gwei), 'gwei'),
                'maxPriorityFeePerGas': self.w3.to_wei('4', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(account.address),
            }
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, from_private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex()
            
        except Exception as e:
            print(f"Error transferring ETH: {str(e)}")
            return None
    
    def transfer_usdt(self, from_private_key, to_address, amount_usdt, gas_price_gwei=None):
        """
        Transfer USDT from one address to another.
        
        Args:
            from_private_key (str): Private key of sender (decrypted)
            to_address (str): Recipient address
            amount_usdt (float): Amount of USDT to send
            gas_price_gwei (float): Gas price in Gwei (optional)
            
        Returns:
            str: Transaction hash or None if failed
        """
        try:
            # Create account from private key
            account = self.w3.eth.account.from_key(from_private_key)
            
            # Validate addresses
            recipient_address = Web3.to_checksum_address(to_address)
            
            # Check minimum amount
            if amount_usdt < 0.1:
                print(f"Amount too low: {amount_usdt} USDT")
                return None
            
            # Get gas price
            if gas_price_gwei is None:
                gas_price_gwei = self.get_gas_price_gwei()
                if gas_price_gwei is None:
                    print("Could not get gas price")
                    return None
                gas_price_gwei = round(gas_price_gwei * 1.35)  # Add 35% buffer for USDT
            
            # Check USDT balance
            usdt_balance = self.get_usdt_balance(account.address)
            if usdt_balance is None or usdt_balance < (amount_usdt + 0.1):
                print(f"Insufficient USDT balance: {usdt_balance}")
                return None
            
            # Check ETH balance for gas
            eth_balance, _ = self.get_eth_balance(account.address)
            gas_cost_eth = (gas_price_gwei * self.max_usdt_gas) / 1_000_000_000
            if eth_balance is None or eth_balance < gas_cost_eth:
                print(f"Insufficient ETH for gas: {eth_balance}")
                return None
            
            # Convert USDT amount to wei (6 decimals)
            usdt_amount_wei = int(amount_usdt * 10**6)
            
            # Build transaction
            transfer_function = self.usdt_contract.functions.transfer(
                recipient_address, 
                usdt_amount_wei
            )
            
            transaction = transfer_function.build_transaction({
                'chainId': 1,  # Ethereum mainnet
                'gas': self.max_usdt_gas,
                'maxFeePerGas': self.w3.to_wei(str(gas_price_gwei), 'gwei'),
                'maxPriorityFeePerGas': self.w3.to_wei('4', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(account.address),
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, from_private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex()
            
        except Exception as e:
            print(f"Error transferring USDT: {str(e)}")
            return None
    
    def get_transaction_history(self, wallet_address, api_key, token_type="eth"):
        """
        Get transaction history for a wallet address using Etherscan API.
        
        Args:
            wallet_address (str): Ethereum wallet address
            api_key (str): Etherscan API key
            token_type (str): "eth" for ETH transactions, "usdt" for USDT transactions
            
        Returns:
            list: List of transaction dictionaries
        """
        try:
            if token_type.lower() == "eth":
                url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=99999999&sort=desc&apikey={api_key}"
            elif token_type.lower() == "usdt":
                url = f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={self.usdt_contract_address}&address={wallet_address}&startblock=0&endblock=99999999&sort=desc&apikey={api_key}"
            else:
                print(f"Unsupported token type: {token_type}")
                return []
            
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1':
                    transactions = []
                    for txn in data.get('result', []):
                        tx_data = {
                            'hash': txn.get('hash'),
                            'from': txn.get('from'),
                            'to': txn.get('to'),
                            'timestamp': datetime.fromtimestamp(int(txn.get('timeStamp', 0))).isoformat(),
                            'gas_used': txn.get('gasUsed'),
                            'gas_price': txn.get('gasPrice'),
                        }
                        
                        if token_type.lower() == "eth":
                            tx_data['value_eth'] = float(Web3.from_wei(int(txn.get('value', 0)), 'ether'))
                        else:  # USDT
                            tx_data['value_usdt'] = float(int(txn.get('value', 0)) / 10**6)
                        
                        transactions.append(tx_data)
                    
                    return transactions
                else:
                    print(f"Etherscan API error: {data.get('message')}")
                    return []
            else:
                print(f"HTTP error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting transaction history: {str(e)}")
            return []
    
    def validate_address(self, address):
        """
        Validate if an address is a valid Ethereum address.
        
        Args:
            address (str): Address to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            Web3.to_checksum_address(address)
            return True
        except:
            return False
    
    def estimate_gas_cost(self, transaction_type="eth", gas_price_gwei=None):
        """
        Estimate gas cost for a transaction.
        
        Args:
            transaction_type (str): "eth" or "usdt"
            gas_price_gwei (float): Gas price in Gwei (optional)
            
        Returns:
            dict: Gas estimation details
        """
        if gas_price_gwei is None:
            gas_price_gwei = self.get_gas_price_gwei()
            if gas_price_gwei is None:
                return None
        
        if transaction_type.lower() == "eth":
            gas_limit = self.max_eth_gas
            adjusted_gas_price = gas_price_gwei * 1.15
        elif transaction_type.lower() == "usdt":
            gas_limit = self.max_usdt_gas
            adjusted_gas_price = gas_price_gwei * 1.35
        else:
            return None
        
        gas_cost_eth = (adjusted_gas_price * gas_limit) / 1_000_000_000
        
        return {
            'transaction_type': transaction_type,
            'gas_limit': gas_limit,
            'gas_price_gwei': gas_price_gwei,
            'adjusted_gas_price_gwei': adjusted_gas_price,
            'estimated_cost_eth': gas_cost_eth
        }


# Utility functions for CrewAI tools
def create_wallet_tools_instance():
    """
    Create a WalletPaymentTools instance using environment variables.
    
    Returns:
        WalletPaymentTools: Configured instance
    """
    return WalletPaymentTools()


def generate_new_wallet():
    """
    CrewAI tool: Generate a new Ethereum wallet.
    
    Returns:
        dict: Wallet information with public address and encrypted private key
    """
    tools = create_wallet_tools_instance()
    public_address, encrypted_private_key = tools.create_new_wallet()
    
    return {
        'success': True,
        'public_address': public_address,
        'encrypted_private_key': encrypted_private_key,
        'message': 'New wallet created successfully'
    }


def check_wallet_balance(wallet_address, token_type="both"):
    """
    CrewAI tool: Check wallet balance for ETH and/or USDT.
    
    Args:
        wallet_address (str): Ethereum wallet address
        token_type (str): "eth", "usdt", or "both"
        
    Returns:
        dict: Balance information
    """
    tools = create_wallet_tools_instance()
    
    if not tools.validate_address(wallet_address):
        return {
            'success': False,
            'error': 'Invalid wallet address'
        }
    
    result = {'success': True, 'wallet_address': wallet_address}
    
    if token_type.lower() in ["eth", "both"]:
        eth_balance, usd_value = tools.get_eth_balance(wallet_address)
        result['eth_balance'] = eth_balance
        result['eth_usd_value'] = usd_value
    
    if token_type.lower() in ["usdt", "both"]:
        usdt_balance = tools.get_usdt_balance(wallet_address)
        result['usdt_balance'] = usdt_balance
    
    return result


def send_cryptocurrency(from_private_key_encrypted, to_address, amount, token_type, fernet_key=None):
    """
    CrewAI tool: Send cryptocurrency (ETH or USDT) from one address to another.
    
    Args:
        from_private_key_encrypted (str): Encrypted private key of sender
        to_address (str): Recipient address
        amount (float): Amount to send
        token_type (str): "eth" or "usdt"
        fernet_key (str): Fernet key for decryption (optional if set in env)
        
    Returns:
        dict: Transaction result
    """
    try:
        if fernet_key:
            tools = WalletPaymentTools(fernet_key=fernet_key)
        else:
            tools = create_wallet_tools_instance()
        
        # Decrypt private key
        private_key = tools.decrypt_private_key(from_private_key_encrypted)
        if not private_key:
            return {
                'success': False,
                'error': 'Failed to decrypt private key'
            }
        
        # Validate recipient address
        if not tools.validate_address(to_address):
            return {
                'success': False,
                'error': 'Invalid recipient address'
            }
        
        # Send transaction
        if token_type.lower() == "eth":
            tx_hash = tools.transfer_eth(private_key, to_address, amount)
        elif token_type.lower() == "usdt":
            tx_hash = tools.transfer_usdt(private_key, to_address, amount)
        else:
            return {
                'success': False,
                'error': 'Invalid token type. Use "eth" or "usdt"'
            }
        
        if tx_hash:
            return {
                'success': True,
                'transaction_hash': tx_hash,
                'message': f'Successfully sent {amount} {token_type.upper()}'
            }
        else:
            return {
                'success': False,
                'error': 'Transaction failed'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Error sending cryptocurrency: {str(e)}'
        }


def get_gas_estimate(transaction_type="eth"):
    """
    CrewAI tool: Get current gas price estimate for transactions.
    
    Args:
        transaction_type (str): "eth" or "usdt"
        
    Returns:
        dict: Gas estimation information
    """
    tools = create_wallet_tools_instance()
    estimate = tools.estimate_gas_cost(transaction_type)
    
    if estimate:
        return {
            'success': True,
            **estimate
        }
    else:
        return {
            'success': False,
            'error': 'Failed to get gas estimate'
        } 