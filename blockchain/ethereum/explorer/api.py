from blockchain.ethereum.explorer.client import Client
from blockchain.ethereum.explorer.consts import WEI_TO_ETH


class EtherscanApi(Client):

    @staticmethod
    def wei_to_eth(wei) -> float:
        return float(wei) * WEI_TO_ETH

    def get_ether_balance(self, address: str, tag: str = "latest") -> float:
        """
        Returns the Ether balance of a given address.
        """
        wei_balance: str = self.get(
            "account",
            "balance",
            address=address,
            tag=tag
        )
        eth_balance = self.wei_to_eth(wei_balance)
        return eth_balance

    def get_erc20_token_balance(self, address: str, contractaddress: str, tag: str = "latest") -> float:
        """
        Returns the current balance of an ERC-20 token of an address.
        """
        erc20_token_balance = self.get(
            "account",
            "tokenbalance",
            address=address,
            contractaddress=contractaddress,
            tag=tag
        )
        return float(erc20_token_balance)
