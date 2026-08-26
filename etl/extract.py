import yfinance as yf


def fetch_ticker_data(symbol: str, history_period: str = "2d") -> dict:
    """
    Extracts metadata and price history for a given ticker. Note that the ticker doesn't
    have to be associated with a stock, it can be a fund or an ETF the method returns all
    it finds, which may include missing price values or fundamental metrics.
    """
    ticker = yf.Ticker(symbol)
    info = ticker.info
    history = ticker.history(period=history_period)
    return {"symbol": symbol, "info": info, "history": history}
