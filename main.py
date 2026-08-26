from etl import fetch_ticker_data
from etl import transform_raw_data
from etl import load_data


def run_pipeline(tickers: list[str]):
    """Starts the ETL pipeline execution"""
    print("Starting ETL Pipeline Execution...")
    for symbol in tickers:
        print(f"--> Fetching data for: {symbol}")
        raw_data = fetch_ticker_data(symbol)
        transformed_data = transform_raw_data(raw_data)
        load_data(transformed_data)
    print("\nETL Execution completed successfully!")



if __name__ == "__main__":
    TEST_TICKERS = ["AAPL", "SPY"]
    run_pipeline(TEST_TICKERS)
