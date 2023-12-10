import requests
from blockchain.ethereum.explorer.consts import BASE_URL


class Client:
    def __init__(self, api_key):
        self.api_key = api_key

    def get(self, module: str, action: str, api_key: str = None, **kwargs):
        kwargs["module"] = module
        kwargs["action"] = action
        kwargs["api_key"] = api_key or self.api_key
        query_params = "&".join(f"{k}={v}" for k, v in kwargs.items())
        url = BASE_URL + "?" + query_params
        response = requests.get(url)
        data: dict = response.json()
        status = data.get("status")
        if status != "1":
            raise ValueError(data)
        return data["result"]
