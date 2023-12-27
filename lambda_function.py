import time
import asyncio
import logging
import traceback
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from blockchain.birdeye.BirdeyeApi import BirdeyeApi
from blockchain.utils.TelegramBot import telegram_bot_sendtext
from blockchain.utils.YFinanceApi import YFinanceApi
from blockchain.secret import (
    CHAIN_WALLET_MAPPING,
    BIRDEYE_API_KEY,
)


def main():
    start_time = time.time()
    birdeye_api = BirdeyeApi(api_key=BIRDEYE_API_KEY)

    async def collect_chain_wallet_balances(chain, wallet):
        data = await birdeye_api.get_wallet_portfolio(chain=chain, wallet=wallet)
        return chain, wallet, data

    chain_wallets = []
    for chain, wallets in CHAIN_WALLET_MAPPING.items():
        for wallet in wallets:
            chain_wallets.append((chain, wallet))

    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    sgd_usd, *chain_wallet_data = loop.run_until_complete(
        asyncio.gather(
            YFinanceApi.async_get_yfinance_ticker_price(ticker="SGDUSD=X"),
            *[
                collect_chain_wallet_balances(chain, wallet)
                for chain, wallet in chain_wallets
            ],
        )
    )

    rows = []
    all_wallets_total_usd = 0
    for chain, wallet, data in chain_wallet_data:
        all_wallets_total_usd += data.get("totalUsd", 0)
        items = data.get("items", [])
        for item in items:
            symbol = item.get("symbol")
            value = item.get("valueUsd")
            if not all([symbol, value]):
                continue
            rows.append(
                {
                    "chain": chain[:3].upper(),
                    "wallet": wallet[:5],
                    "symbol": symbol,
                    "val": value,
                }
            )

    df = pd.DataFrame(rows)
    df = df.sort_values(by=["chain", "wallet", "val"], ascending=False)
    df["val"] = df["val"].apply(lambda x: f"${x:,.2f}")
    breakdown_table = df.to_string(index=False)

    all_wallets_total_sgd = all_wallets_total_usd / sgd_usd
    balances = pd.Series(
        data={
            "Usd Balance:": f"${all_wallets_total_usd:,.2f}",
            "Sgd Balance:": f"${all_wallets_total_sgd:,.2f}",
        }
    ).to_string()

    time_fmt = " %d %B %Y, %H:%M %p"
    time_zone = ZoneInfo("Asia/Singapore")
    dt = datetime.now(tz=time_zone).strftime(time_fmt)

    end_time = time.time()
    duration = f"[Finished in {end_time - start_time:,.3f}s]"

    msg = "\n\n".join([dt, breakdown_table, balances, duration])
    telegram_bot_sendtext("```" + msg + "```")


def lambda_handler(event=None, context=None):
    try:
        main()
        return {"statusCode": 200}
    except Exception as err:
        error_msg = f"{err}\n{traceback.format_exc()}"
        logging.error(error_msg)
        telegram_bot_sendtext(error_msg)
    return {"statusCode": 500}


if __name__ == "__main__":
    lambda_handler()
