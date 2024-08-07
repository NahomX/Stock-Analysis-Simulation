import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.model_selection import RandomizedSearchCV
from sklearn.base import BaseEstimator, ClassifierMixin

from Monte_Carlo_Intutive_mth import monte_carlo_simulation
from fiveday_1u_hypothesis import check_price_drop
from fiveday_1u_price_recovery import check_price_drop_and_recovery

def main():
    # Define common parameters
    tickers = ['AAPL', 'GOOG', 'MSFT', 'TSLA']
    
    # Prompt user for start and end dates
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")
    
    drop_percentage = 0.05
    increase_percentage = 0.01

    # Run 5% Drop Hypothesis Test
    print("Running 5% Drop Hypothesis Test:")
    drop_results = check_price_drop(tickers, start_date, end_date)
    print(drop_results)

    # Run 5% Drop and Recovery Test
    print("\nRunning 5% Drop and Recovery Test:")
    recovered_results, non_recovered_results = check_price_drop_and_recovery(
        tickers, start_date, end_date, drop_percentage, increase_percentage
    )
    print("Recovered Results:")
    print(recovered_results)
    print("\nNon-Recovered Results:")
    print(non_recovered_results)

    # Run Monte Carlo Simulation with Optimization
    print("\nRunning Monte Carlo Simulation:")
    num_simulations = 100
    best_params = monte_carlo_simulation(tickers, start_date, end_date, num_simulations)
    print("Best Parameters Found:")
    print(best_params)

if __name__ == "__main__":
    main()
