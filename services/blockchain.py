# services/blockchain.py
import os
import json
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import logging
from dotenv import load_dotenv
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

NODE_RPC_URL = os.getenv("RPC_URL")
logger.info(f"Using RPC URL: {NODE_RPC_URL}")

ERC20_ABI = json.loads("""
[
    {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"stateMutability":"view","type":"function"},
    {"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},
    {"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"stateMutability":"view","type":"function"}
]
""")

w3 = Web3(Web3.HTTPProvider(NODE_RPC_URL))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

def send_erc20_token(private_key, token_address, recipient_address, amount):
    try:
        account = w3.eth.account.from_key(private_key)
        wallet_address = account.address
        logger.info(f"Sender wallet address: {wallet_address}")
        logger.info(f"Token contract address: {token_address}")
        logger.info(f"Recipient address: {recipient_address}")
        
        # Check ETH balance first
        eth_balance = w3.eth.get_balance(wallet_address)
        logger.info(f"ETH balance: {w3.from_wei(eth_balance, 'ether')} ETH")
        
        token_contract = w3.eth.contract(address=w3.to_checksum_address(token_address), abi=ERC20_ABI)
        
        # Check token balance
        try:
            token_balance = token_contract.functions.balanceOf(wallet_address).call()
            decimals = token_contract.functions.decimals().call()
            logger.info(f"Token decimals: {decimals}")
            logger.info(f"Token balance: {token_balance / (10 ** decimals)}")
        except Exception as e:
            logger.error(f"Error checking token balance: {str(e)}")
        
        amount_in_wei = int(Decimal(amount) * (10 ** decimals))
        logger.info(f"Amount to send in token units: {amount_in_wei}")

        nonce = w3.eth.get_transaction_count(wallet_address)
        logger.info(f"Nonce: {nonce}")
        
        gas_price = w3.eth.gas_price
        logger.info(f"Gas price: {w3.from_wei(gas_price, 'gwei')} gwei")
        
        # Estimate gas
        try:
            estimated_gas = token_contract.functions.transfer(
                w3.to_checksum_address(recipient_address),
                amount_in_wei
            ).estimate_gas({'from': wallet_address})
            logger.info(f"Estimated gas: {estimated_gas}")
        except Exception as e:
            logger.error(f"Gas estimation failed: {str(e)}")
            estimated_gas = 100000  # Default fallback
            logger.info(f"Using default gas limit: {estimated_gas}")
        
        # Calculate transaction cost
        tx_cost_wei = estimated_gas * gas_price
        logger.info(f"Estimated transaction cost: {w3.from_wei(tx_cost_wei, 'ether')} ETH")
        
        # Check if enough ETH for gas
        if eth_balance < tx_cost_wei:
            error_msg = f"Insufficient ETH for gas: have {w3.from_wei(eth_balance, 'ether')} ETH, need {w3.from_wei(tx_cost_wei, 'ether')} ETH"
            logger.error(error_msg)
            raise Exception(error_msg)

        tx = token_contract.functions.transfer(
            w3.to_checksum_address(recipient_address),
            amount_in_wei
        ).build_transaction({
            'from': wallet_address,
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': estimated_gas,
            'chainId': w3.eth.chain_id
        })
        
        logger.info(f"Chain ID: {w3.eth.chain_id}")
        logger.info(f"Transaction built: {tx}")

        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        logger.info("Transaction signed successfully")
        
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        logger.info(f"Transaction sent successfully. Hash: {tx_hash_hex}")

        return tx_hash_hex
    except Exception as e:
        logger.error(f"Error in send_erc20_token: {str(e)}")
        raise

