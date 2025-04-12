# services/blockchain.py
import os
import json
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from dotenv import load_dotenv
from decimal import Decimal

load_dotenv()

NODE_RPC_URL = os.getenv("RPC_URL")

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
    account = w3.eth.account.from_key(private_key)
    wallet_address = account.address

    token_contract = w3.eth.contract(address=w3.to_checksum_address(token_address), abi=ERC20_ABI)
    decimals = token_contract.functions.decimals().call()

    amount_in_wei = int(Decimal(amount) * (10 ** decimals))

    nonce = w3.eth.get_transaction_count(wallet_address)

    tx = token_contract.functions.transfer(
        w3.to_checksum_address(recipient_address),
        amount_in_wei
    ).build_transaction({
        'from': wallet_address,
        'nonce': nonce,
        'gasPrice': w3.eth.gas_price,
        'gas': 100000,
        'chainId': w3.eth.chain_id
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    return tx_hash.hex()

