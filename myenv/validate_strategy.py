import yfinance as yf  # Import yfinance for data fetching
import pandas as pd
from main_calc_script import final_result
from strategy_utils import count_drop_recovery_outcomes
from datetime import datetime, timedelta

def fetch_1m_data_in_chunks(ticker, start_date, end_date):
    """
    Fetch 1-minute data in 7-day chunks due to API limitations.
    
    Parameters:
    ticker (str): The ticker symbol.
    start_date (str): The start date in 'YYYY-MM-DD' format.
    end_date (str): The end date in 'YYYY-MM-DD' format.
    
    Returns:
    pd.DataFrame: The concatenated 1-minute data.
    """
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    all_data = []

    while start < end:
        chunk_end = min(start + timedelta(days=7), end)
        data = yf.download(ticker, start=start.strftime('%Y-%m-%d'), end=chunk_end.strftime('%Y-%m-%d'), interval='1m')
        all_data.append(data)
        start = chunk_end

    # Concatenate all the chunks
    all_data = pd.concat(all_data)
    return all_data

def calculate_gains(ticker, start_date, end_date, drop_percentage, increase_percentage, stop_loss_percentage, recovery_days):
    # Fetch 1-minute interval data in 7-day chunks
    data = fetch_1m_data_in_chunks(ticker, start_date, end_date)

    # Ensure the index is a DatetimeIndex
    data.index = pd.to_datetime(data.index)

    initial_cash = 10000  # Example initial investment amount
    cash = initial_cash
    shares = 0

    # Get the first opening price of each day
    data['Daily_Open'] = data['Open'].resample('D').first()

    # Forward fill the Daily_Open to ensure each minute has the same open value for the day
    data['Daily_Open'] = data['Daily_Open'].reindex(data.index, method='ffill')

    # Calculate the drop percentage based on the first opening price of the day
    data['Drop_Percentage'] = (data['Low'] - data['Daily_Open']) / data['Daily_Open']
    drop_days = data[data['Drop_Percentage'] <= -drop_percentage]

    for index, row in drop_days.iterrows():
        # Buy shares when the drop happens
        if cash > 0:
            shares = cash // row['Low']  # Buy as many shares as possible
            cash -= shares * row['Low']  # Deduct the spent cash

        drop_price = row['Low']
        stop_loss_price = drop_price * (1 - stop_loss_percentage)
        gain_price = drop_price * (1 + increase_percentage)

        recovered = False
        stop_loss_hit = False
        last_price = drop_price  # Initialize last price as drop price

        for i in range(1, recovery_days + 1):  # Check the next `recovery_days` minutes
            next_day_index = index + pd.Timedelta(minutes=i)
            if next_day_index in data.index:
                next_day_data = data.loc[next_day_index]
                last_price = next_day_data['Close']  # Update last price to the closing price of the current interval

                # Sell on stop loss
                if next_day_data['Low'] <= stop_loss_price:
                    cash += shares * stop_loss_price
                    shares = 0  # Sell all shares
                    stop_loss_hit = True
                    break

                # Sell on recovery
                if next_day_data['High'] >= gain_price:
                    cash += shares * gain_price
                    shares = 0  # Sell all shares
                    recovered = True
                    break

        # If neither recovery nor stop loss, sell at the last price
        if not recovered and not stop_loss_hit:
            cash += shares * last_price
            shares = 0  # Sell all shares

    return cash - initial_cash  # Return the profit or loss

def log_trades(ticker, start_date, end_date, drop_percentage, increase_percentage, stop_loss_percentage, recovery_days):
    # Fetch 1-minute interval data in 7-day chunks
    data = fetch_1m_data_in_chunks(ticker, start_date, end_date)

    # Ensure the index is a DatetimeIndex
    data.index = pd.to_datetime(data.index)

    trade_log = []

    # Get the first opening price of each day
    data['Daily_Open'] = data['Open'].resample('D').first()

    # Forward fill the Daily_Open to ensure each minute has the same open value for the day
    data['Daily_Open'] = data['Daily_Open'].reindex(data.index, method='ffill')

    # Calculate the drop percentage based on the first opening price of the day
    data['Drop_Percentage'] = (data['Low'] - data['Daily_Open']) / data['Daily_Open']
    drop_days = data[data['Drop_Percentage'] <= -drop_percentage]

    for index, row in drop_days.iterrows():
        # Log buy action
        trade_log.append({
            'Action': 'BUY',
            'Date': index.strftime('%Y-%m-%d %H:%M'),
            'Price': row['Low']
        })

        drop_price = row['Low']
        stop_loss_price = drop_price * (1 - stop_loss_percentage)
        gain_price = drop_price * (1 + increase_percentage)

        recovered = False
        stop_loss_hit = False
        last_price = drop_price

        for i in range(1, recovery_days + 1):
            next_day_index = index + pd.Timedelta(minutes=i)
            if next_day_index in data.index:
                next_day_data = data.loc[next_day_index]
                last_price = next_day_data['Close']

                # Log sell action on stop loss
                if next_day_data['Low'] <= stop_loss_price:
                    trade_log.append({
                        'Action': 'SELL (Stop Loss)',
                        'Date': next_day_index.strftime('%Y-%m-%d %H:%M'),
                        'Price': stop_loss_price
                    })
                    stop_loss_hit = True
                    break

                # Log sell action on recovery
                if next_day_data['High'] >= gain_price:
                    trade_log.append({
                        'Action': 'SELL (Recovered)',
                        'Date': next_day_index.strftime('%Y-%m-%d %H:%M'),
                        'Price': gain_price
                    })
                    recovered = True
                    break

        # Log sell action if neither recovery nor stop loss was hit
        if not recovered and not stop_loss_hit:
            trade_log.append({
                'Action': 'SELL (Not Recovered)',
                'Date': next_day_index.strftime('%Y-%m-%d %H:%M'),
                'Price': last_price
            })

    trade_log_df = pd.DataFrame(trade_log)
    return trade_log_df

def validate_strategy(tickers, start_date, end_date, recovery_days):
    # Call final_result from the main_script.py to get the best parameters
    _, best_parameters_df = final_result(tickers, start_date, end_date, recovery_days)

    # Move the date range to the next 30 days
    validation_start_date = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    validation_end_date = (datetime.strptime(validation_start_date, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d')

    for index, row in best_parameters_df.iterrows():
        ticker = row['Ticker']
        drop_percentage = row['drop_percentage']
        increase_percentage = row['increase_percentage']
        stop_loss_percentage = row['stop_loss_percentage']

        # Calculate gains based on the best parameters in the next 30-day period
        profit = calculate_gains(ticker, validation_start_date, validation_end_date, drop_percentage, increase_percentage, stop_loss_percentage, recovery_days)
        print(f"{ticker}: Profit/Loss = ${profit:.2f}")

        # Log and display trades in the next 30-day period
        trades_df = log_trades(ticker, validation_start_date, validation_end_date, drop_percentage, increase_percentage, stop_loss_percentage, recovery_days)
        print(f"\nTrade Log for {ticker} (Validation Period):\n{trades_df}")

if __name__ == "__main__":
    tickers = ['nu']
    start_date = '2024-07-01'
    end_date = '2024-08-01'
    recovery_days = 10  # Number of days to check for recovery

    validate_strategy(tickers, start_date, end_date, recovery_days)
