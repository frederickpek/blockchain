from blockchain.ethereum.explorer.api import EtherscanApi
from blockchain.secret import ETHERSCAN_API_KEY, ETH_WALLET_ADDR
from blockchain.ethereum.web3.client import EthWeb3Client


def main():
    api = EtherscanApi(ETHERSCAN_API_KEY)
    eth = api.get_ether_balance(ETH_WALLET_ADDR)
    print(eth)

    tokens = [
        ("OKB", "0x75231F58b43240C9718Dd58B4967c5114342a86c", 18),
        ("LINK", "0x514910771AF9Ca656af840dff83E8264EcF986CA", 18),
        ("UNI", "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", 18),
    ]

    for token, contract_addr, precision in tokens:
        bal = api.get_erc20_token_balance(ETH_WALLET_ADDR, contract_addr)
        bal = float(bal) / 10**precision
        print(token, bal)


def main2():
    # web3 client test
    wallet_address = "0xf1790Dd7b24b9B6e57aD4b392A9A5fDd4a07220e"
    token_definitions = [
        ("RIO", "0xf21661D0D1d76d3ECb8e1B9F1c923DBfffAe4097", 18),
        ("NXRA", "0x644192291cc835A93d6330b24EA5f5FEdD0eEF9e", 18),
        ("VRA", "0xF411903cbC70a74d22900a5DE66A2dda66507255", 18),
        ("ROUTE", "0x16ECCfDbb4eE1A85A33f3A9B21175Cd7Ae753dB4", 18),
        ("DAG", "0xA8258AbC8f2811dd48EccD209db68F25E3E34667", 8),
        ("PEPE", "0x6982508145454Ce325dDbE47a25d4ec3d2311933", 18),
    ]
    client = EthWeb3Client(wallet_address=wallet_address)
    for token, token_contract_address, decimals in token_definitions:
        balance = client.get_erc20_token_balance(
            token_contract_address, decimals=decimals
        )
        print(f"{token} balance: {balance:,.3f}")


def lambda_handler(event=None, context=None):
    main2()


if __name__ == "__main__":
    lambda_handler()
