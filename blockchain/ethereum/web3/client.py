import functools
from web3 import Web3
from typing import List
from collections import deque
from web3.contract.contract import Contract
from blockchain.ethereum.web3.consts import (
    ETH_PROVIDER_URL_1,
    ETH_PROVIDER_URL_2,
    ETH_PROVIDER_URL_3,
    ETH_PROVIDER_URL_4,
    ERC20_ABI,
)


def refresh_provider_url(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        if not isinstance(self, EthWeb3Client):
            raise ValueError("Used outside context")
        provider_url = self.provider_url_queue.popleft()
        self.provider_url_queue.append(provider_url)
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.provider_url = provider_url
        return func(*args, **kwargs)

    return wrapper


class EthWeb3Client:
    def __init__(self, wallet_address, provider_urls: List[str] = None):
        if not Web3.is_address(wallet_address):
            raise ValueError(f"Not a valid address: {wallet_address}")
        self.wallet_address = wallet_address
        provider_urls = provider_urls or [
            ETH_PROVIDER_URL_1,
            ETH_PROVIDER_URL_2,
            ETH_PROVIDER_URL_3,
            ETH_PROVIDER_URL_4,
        ]
        self.provider_url_queue = deque(provider_urls)
        self.provider_url: str = None
        self.w3: Web3 = None

    @refresh_provider_url
    def get_eth_balance(self) -> float:
        print(f"get_eth_balance with provider url - {self.provider_url}")
        wei_balance = self.w3.eth.get_balance(self.wallet_address)
        eth_balance = self.w3.from_wei(wei_balance, "ether")
        return eth_balance

    @refresh_provider_url
    def get_erc20_token_balance(
        self, token_contract_address: str, decimals: int
    ) -> float:
        print(f"get_erc20_token_balance with provider url - {self.provider_url}")
        erc20_token: Contract = self.w3.eth.contract(
            address=token_contract_address, abi=ERC20_ABI
        )
        token_balance = erc20_token.functions.balanceOf(self.wallet_address).call()
        token_balance = token_balance / 10**decimals
        return token_balance
