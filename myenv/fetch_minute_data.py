import yfinance as yf
import pandas as pd

def fetch_minute_data(ticker, start_date, end_date):
    """
    Fetch 1-minute interval data for a given ticker and time period.

    Parameters:
    ticker (str): The ticker symbol of the stock (e.g., 'AAPL').
    start_date (str): The start date in the format 'YYYY-MM-DD'.
    end_date (str): The end date in the format 'YYYY-MM-DD'.

    Returns:
    pd.DataFrame: A DataFrame containing 1-minute interval data.
    """

    # Fetching 1-minute interval data using yfinance
    data = yf.download(ticker, start=start_date, end=end_date, interval='1m')

    return data

if __name__ == "__main__":
    # Example usage
    ticker = 'Nu'  # Example ticker
    start_date = '2024-8-07'
    end_date = '2024-08-08'

    minute_data = fetch_minute_data(ticker, start_date, end_date)
    print(minute_data)
