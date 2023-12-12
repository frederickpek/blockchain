import json


ETH_PROVIDER_URL_1 = "https://eth.llamarpc.com"
ETH_PROVIDER_URL_2 = "https://rpc.ankr.com/eth"
ETH_PROVIDER_URL_3 = "https://cloudflare-eth.com"
ETH_PROVIDER_URL_4 = "https://eth-mainnet.public.blastapi.io"


with open("blockchain/abi/erc20_abi.json", "r") as file:
    ERC20_ABI = json.load(file)
