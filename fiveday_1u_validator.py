import yfinance as yf
import pandas as pd

def check_stock_events(ticker, date, drop_percentage=0.05, increase_percentage=0.02, stop_loss_percentage=0.03):
    start_date = date.strftime('%Y-%m-%d')
    end_date = (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    data = yf.download(ticker, start=start_date, end=end_date, interval='1m')

    if data.empty:
        return "No data available for this ticker and date."

    results = {
        'Ticker': ticker,
        'Date': date,
        'Open_Price': None,
        'Drop_5%_Timestamp': None,
        'Drop_5%_Price': None,
        'Gain_2%_Timestamp': None,
        'Gain_2%_Price': None,
        'Stop_Loss_Timestamp': None,
        'Stop_Loss_Price': None
    }

    # Find the opening price of the specified date
    open_price_data = data.between_time('09:30', '09:31')
    if not open_price_data.empty:
        open_price = open_price_data.iloc[0]['Open']
        results['Open_Price'] = open_price
    else:
        return "No opening price available for this ticker on the specified date."

    drop_level = open_price * (1 - drop_percentage)
    stop_loss_level = open_price * (1 - stop_loss_percentage)
    gain_level = open_price * (1 + increase_percentage)

    for timestamp, row in data.iterrows():
        # Check for a 5% drop
        if row['Low'] <= drop_level and not results['Drop_5%_Timestamp']:
            results['Drop_5%_Timestamp'] = timestamp
            results['Drop_5%_Price'] = row['Low']

        # Check for a 2% gain after the drop
        if results['Drop_5%_Timestamp'] and row['High'] >= gain_level and not results['Gain_2%_Timestamp']:
            results['Gain_2%_Timestamp'] = timestamp
            results['Gain_2%_Price'] = row['High']

        # Check for stop loss after the drop and before the gain
        if results['Drop_5%_Timestamp'] and not results['Gain_2%_Timestamp'] and row['Low'] <= stop_loss_level and not results['Stop_Loss_Timestamp']:
            results['Stop_Loss_Timestamp'] = timestamp
            results['Stop_Loss_Price'] = row['Low']

        # Stop if all conditions are met
        if results['Drop_5%_Timestamp'] and results['Gain_2%_Timestamp'] and results['Stop_Loss_Timestamp']:
            break

    return results

# Example usage
if __name__ == "__main__":
    specific_ticker = 'nvda'
    specific_date = pd.Timestamp('2024-06-05')
    drop_percentage = 0.05  # 5% price drop
    increase_percentage = 0.02  # 2% price increase
    stop_loss_percentage = 0.05  # 3% stop loss from the drop

    result = check_stock_events(specific_ticker, specific_date, drop_percentage, increase_percentage, stop_loss_percentage)
    print("Checker Result:")
    print(result)
