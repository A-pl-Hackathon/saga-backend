import os
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

load_dotenv()

SAGA_RPC_URL = os.getenv("SAGA_RPC_URL")

# Saga 스마트 컨트랙트의 ABI 로드
with open('abi/SagaToken.json') as f:
    SAGA_CONTRACT_ABI = json.load(f)['abi']

# Saga Chain RPC 연결 설정
w3_saga = Web3(Web3.HTTPProvider(SAGA_RPC_URL))
w3_saga.middleware_onion.inject(geth_poa_middleware, layer=0)

# 컨트랙트 인스턴스화

# Saga ERC-20 토큰 전송 함수
def send_saga_token(private_key: str, token_address: str, recipient_address: str, amount: float):
    account = w3_saga.eth.account.from_key(private_key)
    wallet_address = account.address
    saga_token_contract = w3_saga.eth.contract(
        address=w3_saga.to_checksum_address(token_address), 
        abi=SAGA_CONTRACT_ABI
    )
    decimals = saga_token_contract.functions.decimals().call()
    amount_in_wei = int(amount * (10 ** decimals))

    nonce = w3_saga.eth.get_transaction_count(wallet_address)

    tx = saga_token_contract.functions.transfer(
        w3_saga.to_checksum_address(recipient_address),
        amount_in_wei
    ).build_transaction({
        'from': wallet_address,
        'nonce': nonce,
        'gasPrice': w3_saga.eth.gas_price,
        'gas': 100000,
        'chainId': w3_saga.eth.chain_id
    })

    signed_tx = w3_saga.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3_saga.eth.send_raw_transaction(signed_tx.rawTransaction)

    return tx_hash.hex()

# NFT 민팅 함수 예시
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
