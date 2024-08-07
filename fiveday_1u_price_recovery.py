import yfinance as yf
import pandas as pd

# Function to check for a specified price drop from the opening price and a specified price increase within the following 5 days for a given set of stocks over a specified period
def check_price_drop_and_recovery(tickers, start_date, end_date, drop_percentage, increase_percentage):
    results = []
    non_recovery_results = []
    
    for ticker in tickers:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            continue
        data['Drop_Percentage'] = (data['Low'] - data['Open']) / data['Open']
        drop_days = data[data['Drop_Percentage'] <= -drop_percentage]  # Specified price drop
        for index, row in drop_days.iterrows():
            recovered = False
            for i in range(1, 6):  # Check the next 5 days
                next_day_index = index + pd.Timedelta(days=i)
                if next_day_index in data.index:
                    next_day_data = data.loc[next_day_index]
                    if not next_day_data.empty:
                        next_day_increase = (next_day_data['Close'] - next_day_data['Open']) / next_day_data['Open']
                        if next_day_increase >= increase_percentage:  # Specified price increase
                            results.append({
                                'Ticker': ticker,
                                'Date_Drop': index,
                                'Open_Drop': row['Open'],
                                'Low_Drop': row['Low'],
                                'Drop_Percentage': row['Drop_Percentage'],
                                'Date_Recovery': next_day_index,
                                'Open_Recovery': next_day_data['Open'],
                                'Close_Recovery': next_day_data['Close'],
                                'Increase_Percentage': next_day_increase,
                                'Result': f'Dropped {drop_percentage*100}% and Recovered {increase_percentage*100}% within 5 days'
                            })
                            recovered = True
                            break  # Stop checking further days once the condition is met
            if not recovered:
                non_recovery_results.append({
                    'Ticker': ticker,
                    'Date_Drop': index,
                    'Open_Drop': row['Open'],
                    'Low_Drop': row['Low'],
                    'Drop_Percentage': row['Drop_Percentage'],
                    'Result': f'Dropped {drop_percentage*100}% and Did Not Recover {increase_percentage*100}% within 5 days'
                })
    
    recovered_df = pd.DataFrame(results)
    non_recovered_df = pd.DataFrame(non_recovery_results)
    return recovered_df, non_recovered_df

# Main function to run the hypothesis test with specified parameters
def main(tickers, start_date, end_date, drop_percentage=0.05, increase_percentage=0.02):
    recovered_results, non_recovered_results = check_price_drop_and_recovery(tickers, start_date, end_date, drop_percentage, increase_percentage)
    print("Recovered Results:")
    print(recovered_results)
    print("\nNon-Recovered Results:")
    print(non_recovered_results)

# Example usage
if __name__ == "__main__":
    tickers = ['AAPL', 'GOOG', 'MSFT', 'TSLA']
    start_date = '2024-04-01'
    end_date = '2024-04-30'
    drop_percentage = 0.05  # 5% price drop
    increase_percentage = 0.01  # 2% price increase

    main(tickers, start_date, end_date, drop_percentage, increase_percentage)
