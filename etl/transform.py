from math import isnan
import pandas as pd


def __clean_val(val):
    """
    Converts NaNs and non-finite numbers to None for SQL execution. Thus, missing values
    may become None when entering into the db. The database does support nullable fields
    for price data as well as fundamental metrics, or info, but not tickers and symbols.
    """
    if (val is None or pd.isna(val)) or (isinstance(val, float) and isnan(val)):
        return None
    return val



def __extract_fundamental_metrics(info):
    """
    Extracts the raw data related to fundamental metrics within the fundamental metrics
    database table.
    """
    info_dict = info if isinstance(info, dict) else {}
    pe_ratio = __clean_val(info_dict.get("trailingPE"))
    eps = __clean_val(info_dict.get("trailingEps"))
    ytd_return = __clean_val(info_dict.get("ytdReturn"))
    dividend = __clean_val(info_dict.get("dividendRate"))
    return pe_ratio, eps, ytd_return, dividend



def __extract_price_data(history, pe_ratio, eps, ytd_return, dividend) -> list:
    """
    Extracts the raw price data related to the price metrics within the price metrics
    table from the pipeline database.    
    """
    records = []
    if history is not None and not history.empty:
        for date_idx, row in history.iterrows():
            lookup_date = date_idx.strftime('%Y-%m-%d')
            price_entry = {
                "lookup_date": lookup_date,
                "high_price": __clean_val(row.get("High")),
                "low_price": __clean_val(row.get("Low")),
                "close_price": __clean_val(row.get("Close")),
            }
            fundamental_entry = {
                "pe_ratio": pe_ratio,
                "eps": eps,
                "ytd_return": ytd_return,
                "dividend": dividend
            }
            records.append({
                "price": price_entry,
                "fundamental": fundamental_entry
            })
    return records



def transform_raw_data(raw_data: dict) -> dict:
    """
    Receives a dict with the raw API data parts, where each part contains specific 
    pieces of information from each asset associated with the tickers. Transforms the 
    raw API responses into structured dictionaries matching the pipeline's SQL schema.
    """
    symbol = raw_data["symbol"]
    info = raw_data.get("info") or {}
    history = raw_data.get("history")
    asset_data = {
        "symbol": symbol,
        "asset_name": __clean_val(info.get("shortName") or info.get("longName")),
        "sector": __clean_val(info.get("sector"))
    }
    pe, eps, ytd, dividend = __extract_fundamental_metrics(info)
    records = __extract_price_data(history, pe, eps, ytd, dividend)
    return {"asset": asset_data, "records": records}
