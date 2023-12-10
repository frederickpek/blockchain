from blockchain.ethereum.explorer.api import EtherscanApi
from blockchain.secret import ETHERSCAN_API_KEY, ETH_WALLET_ADDR

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
        bal = float(bal) / 10 ** precision
        print(token, bal)


def lambda_handler(event=None, context=None):
    main()


if __name__ == "__main__":
    lambda_handler()
