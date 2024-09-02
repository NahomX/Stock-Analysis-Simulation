import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

def count_drop_recovery_outcomes(ticker, start_date, end_date, drop_percentage, increase_percentage, stop_loss_percentage, recovery_days):
    dropped_and_recovered = 0
    hit_stop_loss = 0
    dropped_not_recovered = 0
    percentage_change_not_recovered = []  # Store the percentage changes for 'Dropped and Not Recovered'
    
    # Extend the end_date by the recovery period days
    extended_end_date = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=recovery_days)).strftime('%Y-%m-%d')
    
    # Suppress yfinance output
    sys.stdout = open(os.devnull, 'w')
    data = yf.download(ticker, start=start_date, end=extended_end_date)
    sys.stdout = sys.__stdout__  # Reset to default

    if data.empty:
        return pd.DataFrame()  # Return an empty DataFrame if no data

    data['Drop_Percentage'] = (data['Low'] - data['Open']) / data['Open']
    drop_days = data[data['Drop_Percentage'] <= -drop_percentage]  # Specified price drop
    
    for index, row in drop_days.iterrows():
        drop_price = row['Low']  # Use Low_Drop as the base for gain calculations
        stop_loss_price = drop_price * (1 - stop_loss_percentage)
        gain_price = drop_price * (1 + increase_percentage)
        recovered = False
        stop_loss_hit = False
        last_price = drop_price  # Initialize last price as drop price
        
        for i in range(1, recovery_days + 1):  # Check the next `recovery_days` days
            next_day_index = index + pd.Timedelta(days=i)
            if next_day_index in data.index:
                next_day_data = data.loc[next_day_index]
                last_price = next_day_data['Close']  # Update last price to the closing price of the current day
                if next_day_data['Low'] <= stop_loss_price:  # Stop loss hit
                    hit_stop_loss += 1
                    stop_loss_hit = True
                    break  # Stop checking further days once the stop loss is hit
                if next_day_data['High'] >= gain_price:  # Specified price increase from the low drop
                    dropped_and_recovered += 1
                    recovered = True
                    break  # Stop checking further days once the condition is met
        
        if not recovered and not stop_loss_hit:
            dropped_not_recovered += 1
            # Calculate the percentage of the latest price relative to the drop price
            percentage_change = ((last_price - drop_price) / drop_price) * 100
            percentage_change_not_recovered.append(percentage_change)
    
    # Calculate the average % change for 'Dropped and Not Recovered'
    avg_percentage_change_not_recovered = sum(percentage_change_not_recovered) / len(percentage_change_not_recovered) if percentage_change_not_recovered else 0

    # Convert the average % change to a positive decimal
    positive_avg_change_decimal = abs(avg_percentage_change_not_recovered) / 100

    # Perform the custom value calculation
    custom_value = (
        dropped_and_recovered * increase_percentage
        - (hit_stop_loss * stop_loss_percentage)
        - (dropped_not_recovered * positive_avg_change_decimal)
    )

    # Create a DataFrame to summarize the results
    summary_df = pd.DataFrame({
        'Ticker': [ticker],
        'Dropped and Recovered': [dropped_and_recovered],
        'Hit Stop Loss': [hit_stop_loss],
        'Dropped and Not Recovered': [dropped_not_recovered],
        'Avg % Change Not Recovered': [avg_percentage_change_not_recovered],
        'Custom Calculated Value': [custom_value]
    })

    return summary_df
