import aiohttp
from blockchain.birdeye.const import (
    BASE_URL,
    WALLET_PORTFOLIO,
)


class BirdeyeApi:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_headers(self, header_params: dict):
        return {
            "X-API-KEY": self.api_key,
            **header_params,
        }

    async def request(
        self, endpoint: str, header_params: dict = None, query_params: dict = None
    ):
        url = BASE_URL + endpoint
        headers = self.get_headers(header_params or {})
        if query_params:
            url += "?" + "&".join(f"{k}={v}" for k, v in query_params.items())
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()

    async def get_wallet_portfolio(self, chain: str, wallet: str) -> dict:
        header_params = {"x-chain": chain}
        query_params = {"wallet": wallet}
        response = await self.request(
            endpoint=WALLET_PORTFOLIO,
            header_params=header_params,
            query_params=query_params,
        )
        return response.get("data", {})
