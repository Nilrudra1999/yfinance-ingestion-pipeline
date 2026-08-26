DB_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': r'localhost\SQLEXPRESS',
    'database': 'financial_market_data',
    'trusted_connection': 'yes'
}

def get_db_connection():
    """
    Connects to the local Microsoft SQL express database and returns a database
    connection string object, used by the cursor for queries and inserts.
    """
    from pyodbc import connect # keeping inside to prevent remote import errors
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
    )
    return connect(conn_str)



def __execute_load_asset(cursor, asset) -> int:
    """
    Adds the structured data to the local database after the transform script is finished
    extracting from raw API json data. It returns an int indicating the db cursor pos.
    """
    cursor.execute("SELECT tickerID FROM assets WHERE symbol = ?", (asset["symbol"],))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(
        """
        INSERT INTO assets (symbol, asset_name, sector)
        OUTPUT INSERTED.tickerID
        VALUES (?, ?, ?);
        """,
        (asset["symbol"], asset["asset_name"], asset["sector"])
    )
    return cursor.fetchone()[0]



def __execute_insert_price(cursor, price, ticker_id: int) -> int:
    """
    Add the structured price data to the local database after the transformer script has
    finished extracting price information from the raw API json data. Returns a cursor pos.
    """
    cursor.execute(
        "SELECT priceID FROM price_metrics WHERE tickerID = ? AND lookup_date = ?",
        (ticker_id, price["lookup_date"])
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(
        """
        INSERT INTO price_metrics (tickerID, lookup_date, high_price, low_price, close_price)
        OUTPUT INSERTED.priceID
        VALUES (?, ?, ?, ?, ?);
        """,
        (ticker_id, price["lookup_date"], price["high_price"], price["low_price"], 
         price["close_price"])
    )
    return cursor.fetchone()[0]



def __execute_insert_fundamental(cursor, fdmtl, ticker_id: int, price_id: int) -> None:
    """
    Adds the structured fundamental metric data to the local database after the transformer
    script has finished extracting the fundamental metrics from the raw API json data. It
    returns a cursor pos after the insertion is complete.
    """
    cursor.execute("SELECT priceID FROM fundamental_metrics WHERE priceID = ?", (price_id,))
    if not cursor.fetchone():
        cursor.execute(
            """
            INSERT INTO fundamental_metrics (tickerID, priceID, pe_ratio, eps, ytd_return, dividend)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (ticker_id, price_id, fdmtl["pe_ratio"], fdmtl["eps"], 
             fdmtl["ytd_return"], fdmtl["dividend"]))



def load_data(transformed_data: dict) -> None:
    """
    Loads transformed stock data into the local Microsoft SQL Express Server while handling
    foreign key, unique, and primary key constraints using a cursor pos for key retrieval.
    """
    asset = transformed_data["asset"]
    records = transformed_data["records"]
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        ticker_id = __execute_load_asset(cursor, asset)
        for record in records:
            price = record["price"]
            fdmtl = record["fundamental"]
            price_id = __execute_insert_price(cursor, price, ticker_id)
            __execute_insert_fundamental(cursor, fdmtl, ticker_id, price_id)
        conn.commit()
    except Exception as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()
        conn.close()
