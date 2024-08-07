import yfinance as yf
import pandas as pd

# Function to check for a 5% drop from the opening price for a given set of stocks over a specified period
def check_price_drop(tickers, start_date, end_date):
    results = []
    
    for ticker in tickers:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            continue
        data['Drop_Percentage'] = (data['Low'] - data['Open']) / data['Open']
        drop_days = data[data['Drop_Percentage'] <= -0.05]  # 5% price drop
        for index, row in drop_days.iterrows():
            results.append({
                'Ticker': ticker,
                'Date': index,
                'Open': row['Open'],
                'Low': row['Low'],
                'Drop_Percentage': row['Drop_Percentage'],
                'Result': 'Dropped 5% or more'
            })
    
    results_df = pd.DataFrame(results)
    return results_df

# Example usage
if __name__ == "__main__":
    tickers = ['AAPL', 'GOOG', 'MSFT', 'TSLA']
    start_date = '2022-01-01'
    end_date = '2022-01-28'

    results = check_price_drop(tickers, start_date, end_date)
    print(results)
