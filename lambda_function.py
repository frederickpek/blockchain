import time
import json
import asyncio
import logging
import traceback
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from blockchain.birdeye.BirdeyeApi import BirdeyeApi
from blockchain.utils.TelegramBot import telegram_bot_sendtext
from blockchain.utils.YFinanceApi import YFinanceApi
from blockchain.utils.GoogleSheetsClient import GoogleSheetsClient
from blockchain.utils.ascii_chart import gen_ascii_plot
from blockchain.secret import (
    CHAIN_WALLET_MAPPING,
    BIRDEYE_API_KEY,
    SPREADSHEET_ID,
)

GSDB_DEFI_EXTERNAL_ASSETS_CELL = "B3"
GSDB_DEFI_WALLET_BALANCES_CELL = "B2"


def main():
    start_time = time.time()
    birdeye_api = BirdeyeApi(api_key=BIRDEYE_API_KEY)
    gsdb = GoogleSheetsClient(
        "./blockchain/credentials.json", spreadsheet_id=SPREADSHEET_ID
    )

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

    cached_prices = dict()

    # WALLET ASSETS
    rows = []
    all_wallets_total_usd = 0
    for chain, wallet, data in chain_wallet_data:
        all_wallets_total_usd += data.get("totalUsd", 0)
        items = data.get("items", [])
        for item in items:
            symbol = item.get("symbol")
            value = item.get("valueUsd")
            price = item.get("priceUsd")
            if not all([symbol, value, price]):
                continue
            rows.append(
                {
                    "chain": chain[:3].upper(),
                    "wallet": wallet[:5],
                    "symbol": symbol,
                    "value": value,
                }
            )
            cached_prices[symbol] = price

    # EXTERNAL ASSETS
    external_chain_assets: list = json.loads(
        gsdb.get_cell(GSDB_DEFI_EXTERNAL_ASSETS_CELL)
    )
    for info in external_chain_assets:
        chain = info.get("chain")
        wallet = info.get("wallet")
        assets = info.get("assets")
        for asset in assets:
            symbol = asset.get("symbol")
            alias = asset.get("alias")
            qty = asset.get("qty")
            price = cached_prices.get(symbol, cached_prices.get(alias, 0))
            value = qty * price
            all_wallets_total_usd += value
            rows.append(
                {
                    "chain": chain[:3].upper(),
                    "wallet": wallet[:5],
                    "symbol": symbol,
                    "value": value,
                }
            )

    df = pd.DataFrame(rows)
    df = df.sort_values(by=["chain", "wallet", "value"], ascending=False)
    df["value"] = df["value"].apply(lambda x: f"${x:,.2f}")
    breakdown_table = df.to_string(index=False)

    all_wallets_total_sgd = all_wallets_total_usd / sgd_usd
    balances = pd.Series(
        data={
            "Usd Balance:": f"${all_wallets_total_usd:,.2f}",
            "Sgd Balance:": f"${all_wallets_total_sgd:,.2f}",
        }
    ).to_string()

    # CHART
    max_num_points = 32
    ts_now = datetime.now().replace(minute=0, second=0, microsecond=0).timestamp()
    point_now = {str(int(ts_now)): all_wallets_total_usd}
    series: dict = json.loads(gsdb.get_cell(GSDB_DEFI_WALLET_BALANCES_CELL))
    series.update(point_now)
    series = [(ts, bal) for ts, bal in series.items()]
    series.sort(key=lambda x: x[0])
    series = series[-max_num_points:]
    points = list(map(lambda x: x[1], series))
    chart = gen_ascii_plot(points=points)

    # Save Data
    series_dict = {ts: bal for ts, bal in series}
    gsdb.update_cell(GSDB_DEFI_WALLET_BALANCES_CELL, json.dumps(series_dict))

    time_fmt = " %d %B %Y, %H:%M %p"
    time_zone = ZoneInfo("Asia/Singapore")
    dt = datetime.now(tz=time_zone).strftime(time_fmt)

    end_time = time.time()
    duration = f"[Finished in {end_time - start_time:,.3f}s]"

    msg = "\n\n".join([dt, breakdown_table, balances, chart, duration])
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
