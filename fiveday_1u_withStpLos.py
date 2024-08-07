import yfinance as yf
import pandas as pd

# Function to check for a specified price drop from the opening price and a specified price increase within the following 5 days for a given set of stocks over a specified period, including stop loss check
def check_price_drop_and_recovery(tickers, start_date, end_date, drop_percentage, increase_percentage, stop_loss_percentage):
    results = []
    loss_results = []
    
    for ticker in tickers:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            continue
        data['Drop_Percentage'] = (data['Low'] - data['Open']) / data['Open']
        drop_days = data[data['Drop_Percentage'] <= -drop_percentage]  # Specified price drop
        
        for index, row in drop_days.iterrows():
            drop_price = row['Open'] * (1 - drop_percentage)
            stop_loss_price = drop_price * (1 - stop_loss_percentage)
            gain_price = row['Open'] * (1 + increase_percentage)
            recovered = False
            stop_loss_hit = False
            
            for i in range(1, 6):  # Check the next 5 days
                next_day_index = index + pd.Timedelta(days=i)
                if next_day_index in data.index:
                    next_day_data = data.loc[next_day_index]
                    if next_day_data['Low'] <= stop_loss_price:  # Stop loss hit
                        loss_results.append({
                            'Ticker': ticker,
                            'Date_Drop': index,
                            'Open_Drop': row['Open'],
                            'Low_Drop': row['Low'],
                            'Drop_Percentage': row['Drop_Percentage'],
                            'Date_Stop_Loss': next_day_index,
                            'Stop_Loss_Price': stop_loss_price,
                            'Low_Stop_Loss': next_day_data['Low'],
                            'Result': f'Dropped {drop_percentage*100}% and Hit Stop Loss at {stop_loss_percentage*100}% before Recovery'
                        })
                        stop_loss_hit = True
                        break  # Stop checking further days once the stop loss is hit
                    if next_day_data['High'] >= gain_price:  # Specified price increase
                        results.append({
                            'Ticker': ticker,
                            'Date_Drop': index,
                            'Open_Drop': row['Open'],
                            'Low_Drop': row['Low'],
                            'Drop_Percentage': row['Drop_Percentage'],
                            'Date_Recovery': next_day_index,
                            'Open_Recovery': next_day_data['Open'],
                            'Close_Recovery': next_day_data['Close'],
                            'Increase_Percentage': (next_day_data['Close'] - next_day_data['Open']) / next_day_data['Open'],
                            'Result': f'Dropped {drop_percentage*100}% and Recovered {increase_percentage*100}% within 5 days'
                        })
                        recovered = True
                        break  # Stop checking further days once the condition is met
            if not recovered and not stop_loss_hit:
                loss_results.append({
                    'Ticker': ticker,
                    'Date_Drop': index,
                    'Open_Drop': row['Open'],
                    'Low_Drop': row['Low'],
                    'Drop_Percentage': row['Drop_Percentage'],
                    'Result': f'Dropped {drop_percentage*100}% and Did Not Recover {increase_percentage*100}% within 5 days'
                })
    
    recovered_df = pd.DataFrame(results)
    loss_df = pd.DataFrame(loss_results)
    return recovered_df, loss_df

# Main function to run the hypothesis test with specified parameters
def main(tickers, start_date, end_date, drop_percentage=0.05, increase_percentage=0.02, stop_loss_percentage=0.03):
    recovered_results, loss_results = check_price_drop_and_recovery(tickers, start_date, end_date, drop_percentage, increase_percentage, stop_loss_percentage)
    print("Recovered Results:")
    print(recovered_results)
    print("\nLoss Results:")
    print(loss_results)


if __name__ == "__main__":
    tickers = ['APP','TEM','KOSS','EGHT','CHGG','THMO','ZAPP']
    start_date = '2024-07-17'
    end_date = '2024-07-18'

    
    drop_percentage = 0.05  
    increase_percentage = 0.02  
    stop_loss_percentage = 0.10  

    main(tickers, start_date, end_date, drop_percentage, increase_percentage, stop_loss_percentage)
