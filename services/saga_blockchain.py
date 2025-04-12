import os
import json
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import logging
from dotenv import load_dotenv
from decimal import Decimal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

SAGA_RPC_URL = os.getenv("SAGA_RPC_URL")
logger.info(f"Using Saga RPC URL: {SAGA_RPC_URL}")

w3_saga = Web3(Web3.HTTPProvider(SAGA_RPC_URL))
w3_saga.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)


def send_saga_token(private_key: str, recipient_address: str, amount: float):
    try:
        account = w3_saga.eth.account.from_key(private_key)
        wallet_address = account.address
        logger.info(f"Sender wallet address: {wallet_address}")
        logger.info(f"Recipient address: {recipient_address}")
        
        token_balance = w3_saga.eth.get_balance(wallet_address)
        logger.info(f"Saga token balance: {w3_saga.from_wei(token_balance, 'ether')} SAGA")
        
        amount_in_wei = w3_saga.to_wei(amount, 'ether')
        logger.info(f"Amount to send in wei: {amount_in_wei}")
        
        if token_balance < amount_in_wei:
            error_msg = f"Insufficient Saga tokens: have {w3_saga.from_wei(token_balance, 'ether')} SAGA, need {amount} SAGA"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        nonce = w3_saga.eth.get_transaction_count(wallet_address)
        logger.info(f"Nonce: {nonce}")
        
        gas_price = w3_saga.eth.gas_price
        logger.info(f"Gas price: {w3_saga.from_wei(gas_price, 'gwei')} gwei")
        
        gas_limit = 21000
        
        tx_cost_wei = gas_limit * gas_price
        logger.info(f"Estimated transaction cost: {w3_saga.from_wei(tx_cost_wei, 'ether')} SAGA")
        
        if token_balance < (amount_in_wei + tx_cost_wei):
            error_msg = f"Insufficient balance for transfer + gas: have {w3_saga.from_wei(token_balance, 'ether')} SAGA, need {w3_saga.from_wei(amount_in_wei + tx_cost_wei, 'ether')} SAGA"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        tx = {
            'from': wallet_address,
            'to': w3_saga.to_checksum_address(recipient_address),
            'value': amount_in_wei,
            'nonce': nonce,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': w3_saga.eth.chain_id
        }
        
        logger.info(f"Chain ID: {w3_saga.eth.chain_id}")
        logger.info(f"Transaction built: {tx}")
        
        signed_tx = w3_saga.eth.account.sign_transaction(tx, private_key)
        logger.info("Transaction signed successfully")
        
        tx_hash = w3_saga.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash_hex = tx_hash.hex()
        logger.info(f"Transaction sent successfully. Hash: {tx_hash_hex}")
        
        return tx_hash_hex
    except Exception as e:
        logger.error(f"Error in send_saga_token: {str(e)}")
        raise

def mint_saga_nft(private_key: str, token_uri: str):
    account = w3_saga.eth.account.from_key(private_key)
    wallet_address = account.address

    nonce = w3_saga.eth.get_transaction_count(wallet_address)

    tx = saga_token_contract.functions.mintNFT(
        wallet_address, token_uri
    ).build_transaction({
        'from': wallet_address,
        'nonce': nonce,
        'gasPrice': w3_saga.eth.gas_price,
        'gas': 300000,
        'chainId': w3_saga.eth.chain_id
    })

    signed_tx = w3_saga.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3_saga.eth.send_raw_transaction(signed_tx.rawTransaction)

    return tx_hash.hex()
