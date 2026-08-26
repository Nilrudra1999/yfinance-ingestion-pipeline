import argparse
import json
import sys
from pathlib import Path

from etl import fetch_ticker_data
from etl import transform_raw_data
from etl import load_data


def read_tickers(file_path: str = "tickers.txt") -> list[str]:
    path = Path(file_path)
    if not path.exists():
        print(f"Error: {file_path} not found.")
        sys.exit(1)
    content = path.read_text()
    tickers = [t.strip().upper()
               for t in content.replace(",", "\n").splitlines()
               if t.strip()]
    return tickers



def run_remote_transform_only(tickers: list[str]) -> list[dict]:
    """
    Runs extract and transform stages remotely. Because GitHub Actions runs in a cloud
    virtual machine, it cannot natively connect directly to localhost\SQLEXPRESS. Fetch
    yfinance data runs remotely, sending JSON payload back build Artifact for db upload.
    """
    transformed_records = []
    print("Starting Remote ETL Extraction & Transformation...")
    for symbol in tickers:
        print(f"--> [Remote] Fetching and Transforming: {symbol}")
        raw_data = fetch_ticker_data(symbol)
        transformed = transform_raw_data(raw_data)
        transformed_records.append(transformed)
    return transformed_records



def run_local_load_only(data_file: str):
    """
    Loads pre-transformed data into local MS SQL Server. A local Bash/Python runner that
    triggers the GitHub Actions workflow via the GitHub CLI (gh), waits for completion,
    downloads the extracted/transformed data, and loads it into the local SQL Server.
    """
    print("\nStarting Local Database Load...")
    with open(data_file, "r") as f:
        transformed_records = json.load(f)
    for item in transformed_records:
        symbol = item["asset"]["symbol"]
        print(f"--> [Local] Loading into SQL Express: {symbol}")
        load_data(item)
    print("\nLocal Database Load Completed Successfully!")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Pipeline Execution")
    parser.add_argument("--mode", choices=["full", "remote-extract", "local-load"],
                        default="full",)
    parser.add_argument("--tickers-file", default="tickers.txt")
    parser.add_argument("--input-json", default="transformed_data.json")
    args = parser.parse_args()
    if args.mode == "remote-extract":
        tickers = read_tickers(args.tickers_file)
        results = run_remote_transform_only(tickers)
        with open("transformed_data.json", "w") as f:
            json.dump(results, f, indent=2)
        print("Remote extraction completed. Output to transformed_data.json.")
    elif args.mode == "local-load":
        run_local_load_only(args.input_json)
    elif args.mode == "full":
        tickers = read_tickers(args.tickers_file)
        for symbol in tickers:
            raw = fetch_ticker_data(symbol)
            transformed = transform_raw_data(raw)
            load_data(transformed)

