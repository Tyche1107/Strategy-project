"""
fetch_data.py — Download BTC and ETH perpetual futures data from Binance public API.

This script fetches funding rates and 1h OHLCV candlestick data for BTC-USDT-PERP
and ETH-USDT-PERP over a specified date range. No API key required; Binance's
/fapi/v1/ endpoints are publicly accessible.

Usage:
    python data/fetch_data.py --start 2020-01-01 --end 2024-12-31
    python data/fetch_data.py --start 2020-01-01 --end 2024-12-31 --symbols BTC ETH
"""

import argparse
import time
import os
import requests
import pandas as pd
from datetime import datetime, timezone

BASE_URL = "https://fapi.binance.com"


def to_ms(dt_str: str) -> int:
    """Convert a date string like '2020-01-01' to milliseconds since epoch."""
    dt = datetime.strptime(dt_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def fetch_funding_rates(symbol: str, start_ms: int, end_ms: int) -> pd.DataFrame:
    """
    Fetch all funding rate records for a given symbol over a date range.

    Binance returns at most 1000 records per request, so we paginate by
    advancing startTime to the timestamp of the last record + 1ms.

    Args:
        symbol: e.g. 'BTCUSDT'
        start_ms: start time in milliseconds
        end_ms: end time in milliseconds

    Returns:
        DataFrame with columns: timestamp, fundingRate, fundingTime
    """
    url = f"{BASE_URL}/fapi/v1/fundingRate"
    all_records = []
    current_start = start_ms

    while current_start < end_ms:
        params = {
            "symbol": symbol,
            "startTime": current_start,
            "endTime": end_ms,
            "limit": 1000,
        }
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            break

        all_records.extend(data)

        # Advance past the last record we received
        last_time = data[-1]["fundingTime"]
        current_start = last_time + 1

        # If we got fewer than 1000, we've reached the end
        if len(data) < 1000:
            break

        time.sleep(0.2)  # be polite to the API

    if not all_records:
        return pd.DataFrame()

    df = pd.DataFrame(all_records)
    df["fundingTime"] = pd.to_datetime(df["fundingTime"], unit="ms", utc=True)
    df["fundingRate"] = df["fundingRate"].astype(float)
    df = df.sort_values("fundingTime").reset_index(drop=True)
    df = df[df["fundingTime"] <= pd.Timestamp(end_ms, unit="ms", tz="UTC")]
    return df[["fundingTime", "fundingRate", "symbol"]]


def fetch_ohlcv(symbol: str, interval: str, start_ms: int, end_ms: int) -> pd.DataFrame:
    """
    Fetch OHLCV klines for a symbol over a date range.

    Binance returns at most 1500 klines per request. We paginate similarly
    to funding rates, advancing startTime by the close time of the last candle.

    Args:
        symbol: e.g. 'BTCUSDT'
        interval: e.g. '1h'
        start_ms: start time in milliseconds
        end_ms: end time in milliseconds

    Returns:
        DataFrame with standard OHLCV columns plus volume
    """
    url = f"{BASE_URL}/fapi/v1/klines"
    all_candles = []
    current_start = start_ms

    while current_start < end_ms:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_start,
            "endTime": end_ms,
            "limit": 1500,
        }
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            break

        all_candles.extend(data)

        # Each element: [open_time, open, high, low, close, volume, close_time, ...]
        last_close_time = data[-1][6]
        current_start = last_close_time + 1

        if len(data) < 1500:
            break

        time.sleep(0.2)

    if not all_candles:
        return pd.DataFrame()

    cols = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "n_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ]
    df = pd.DataFrame(all_candles, columns=cols)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    df = df.sort_values("open_time").reset_index(drop=True)
    return df[["open_time", "open", "high", "low", "close", "volume", "close_time"]]


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Binance perpetual futures data (funding rates + OHLCV)"
    )
    parser.add_argument("--start", default="2020-01-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default="2024-12-31", help="End date YYYY-MM-DD")
    parser.add_argument(
        "--symbols", nargs="+", default=["BTC", "ETH"],
        help="List of base assets to fetch (default: BTC ETH)"
    )
    parser.add_argument("--interval", default="1h", help="OHLCV interval (default: 1h)")
    parser.add_argument("--outdir", default="data", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    start_ms = to_ms(args.start)
    end_ms = to_ms(args.end)

    for base in args.symbols:
        symbol = f"{base}USDT"
        print(f"\nFetching {symbol} funding rates ({args.start} to {args.end})...")
        try:
            fr_df = fetch_funding_rates(symbol, start_ms, end_ms)
            if fr_df.empty:
                print(f"  No funding rate data returned for {symbol}.")
            else:
                out_path = os.path.join(args.outdir, f"{base.lower()}_funding.csv")
                fr_df.to_csv(out_path, index=False)
                print(f"  Saved {len(fr_df)} records to {out_path}")
        except Exception as e:
            print(f"  ERROR fetching funding rates for {symbol}: {e}")

        print(f"Fetching {symbol} {args.interval} OHLCV...")
        try:
            ohlcv_df = fetch_ohlcv(symbol, args.interval, start_ms, end_ms)
            if ohlcv_df.empty:
                print(f"  No OHLCV data returned for {symbol}.")
            else:
                out_path = os.path.join(args.outdir, f"{base.lower()}_ohlcv_{args.interval}.csv")
                ohlcv_df.to_csv(out_path, index=False)
                print(f"  Saved {len(ohlcv_df)} records to {out_path}")
        except Exception as e:
            print(f"  ERROR fetching OHLCV for {symbol}: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
