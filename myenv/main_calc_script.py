import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from strategy_utils import count_drop_recovery_outcomes

# Monte Carlo simulation to find the optimal parameters for each ticker
def monte_carlo_simulation(ticker, start_date, end_date, recovery_days, num_simulations=1000):
    best_custom_value = -np.inf
    best_parameters = {}

    for _ in range(num_simulations):
        # Randomly select parameters within a reasonable range
        drop_percentage = np.random.uniform(0.01, 0.1)  # Drop percentage between 1% and 10%
        increase_percentage = np.random.uniform(0.01, 0.1)  # Increase percentage between 1% and 10%
        stop_loss_percentage = np.random.uniform(0.01, 0.1)  # Stop loss percentage between 1% and 10%

        custom_value = count_drop_recovery_outcomes(
            ticker,
            start_date,
            end_date,
            drop_percentage,
            increase_percentage,
            stop_loss_percentage,
            recovery_days
        )['Custom Calculated Value'].iloc[0]

        if custom_value > best_custom_value:
            best_custom_value = custom_value
            best_parameters = {
                'drop_percentage': drop_percentage,
                'increase_percentage': increase_percentage,
                'stop_loss_percentage': stop_loss_percentage,
                'custom_value': custom_value
            }

    return best_parameters

# Final result function to run the analysis with Monte Carlo simulation and then apply the best parameters to the next 30-day period
def final_result(tickers, start_date, end_date, recovery_days=10, num_simulations=1000):
    all_results = []
    best_parameters_list = []

    for ticker in tickers:
        # Step 1: Run the Monte Carlo simulation to find the best parameters for each ticker
        best_parameters = monte_carlo_simulation(ticker, start_date, end_date, recovery_days, num_simulations)
        best_parameters['Ticker'] = ticker  # Add the ticker symbol to the best parameters
        best_parameters_list.append(best_parameters)  # Append the best parameters to the list

        print(f"Best Parameters Found for {ticker}:")
        print(best_parameters)

        # Step 2: Calculate the next 30-day period
        new_start_date = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        new_end_date = (datetime.strptime(new_start_date, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d')

        # Step 3: Use the best parameters to run the original function on the next 30-day period
        summary = count_drop_recovery_outcomes(
            ticker,
            new_start_date,
            new_end_date,
            best_parameters['drop_percentage'],
            best_parameters['increase_percentage'],
            best_parameters['stop_loss_percentage'],
            recovery_days
        )

        all_results.append(summary)

    # Combine all ticker results into one DataFrame
    final_summary = pd.concat(all_results).reset_index(drop=True)

    # Convert the best parameters list into a DataFrame
    best_parameters_df = pd.DataFrame(best_parameters_list)

    # Step 4: Print the final combined summary results
    print("\nFinal Summary of Outcomes Using Best Parameters for Each Ticker:")
    print(final_summary)

    print("\nBest Parameters for Each Ticker:")
    print(best_parameters_df)

    return final_summary, best_parameters_df  # Return results and best parameters DataFrame

if __name__ == "__main__":
    tickers = ['TSLA', 'AAPL', 'MSFT']
    start_date = '2024-01-01'
    end_date = '2024-03-01'
    recovery_days = 10  # Number of days to check for recovery
    num_simulations = 1000  # Number of simulations to run

    final_summary, best_parameters_df = final_result(tickers, start_date, end_date, recovery_days, num_simulations)
