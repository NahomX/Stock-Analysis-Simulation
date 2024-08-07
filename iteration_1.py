import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.model_selection import RandomizedSearchCV
from sklearn.base import BaseEstimator, ClassifierMixin

# Function to filter tickers with volume, price, and volatility conditions
def filter_tickers(tickers, start_date, end_date, volume_threshold, price_threshold, volatility_threshold):
    filtered_tickers = []
    for ticker in tickers:
        data = yf.download(ticker, start=start_date, end=end_date)
        data = data[(data['Volume'] > volume_threshold) & (data['Close'] > price_threshold) & (data['Close'].rolling(window=1).std() > volatility_threshold)]
        if not data.empty:
            filtered_tickers.append(ticker)
    return filtered_tickers

# Class to test the hypothesis for each day
class HypothesisTester(BaseEstimator, ClassifierMixin):
    def __init__(self, tickers, start_date, end_date, price_drop_percentage=0.05, volume_threshold=500000, price_threshold=10, volatility_threshold=0.1):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.price_drop_percentage = price_drop_percentage
        self.volume_threshold = volume_threshold
        self.price_threshold = price_threshold
        self.volatility_threshold = volatility_threshold

    def fit(self, X, y=None):
        return self

    def score(self, X, y=None):
        results = self.test_hypothesis(self.tickers, self.start_date, self.end_date, self.price_drop_percentage, self.volume_threshold, self.price_threshold, self.volatility_threshold)
        success_rate = self.evaluate_success_rate(results)
        return success_rate

    def test_hypothesis(self, tickers, start_date, end_date, price_drop_percentage, volume_threshold, price_threshold, volatility_threshold):
        results = pd.DataFrame(columns=['Ticker', 'Date', 'Result'])
        for day in pd.date_range(start_date, end_date):
            filtered_tickers = filter_tickers(tickers, day, day + pd.Timedelta(days=1), volume_threshold, price_threshold, volatility_threshold)
            for ticker in filtered_tickers:
                data = yf.download(ticker, start=day, end=day + pd.Timedelta(days=1))
                data['Price_Drop'] = (data['Low'] - data['Open']) / data['Open']
                price_drop_days = data[data['Price_Drop'] <= -price_drop_percentage]
                if price_drop_days.empty:
                    result = f'Condition not satisfied for ticker {ticker} on date {day}'
                else:
                    price_drop_days['Next_Day_Increase'] = (price_drop_days['Close'].shift(-1) - price_drop_days['Open'].shift(-1)) / price_drop_days['Open'].shift(-1)
                    eligible_days = price_drop_days[price_drop_days['Next_Day_Increase'] >= 0.02]
                    if eligible_days.empty:
                        result = f'Hypothesis failed for ticker {ticker} on date {day}'
                    else:
                        average_increase = eligible_days['Next_Day_Increase'].mean()
                        result = f'Hypothesis passed for ticker {ticker} on date {day}'
                results = results.append({'Ticker': ticker, 'Date': day, 'Result': result}, ignore_index=True)
        return results

    def evaluate_success_rate(self, results):
        success_rate = (results['Result'] == 'Hypothesis passed').mean()
        return success_rate

# Monte Carlo simulation with optimization
def monte_carlo_simulation(tickers, start_date, end_date, num_simulations):
    param_grid = {
        'price_drop_percentage': np.arange(0.01, 0.1, 0.01),
        'volume_threshold': np.arange(100000, 1000000, 100000),
        'price_threshold': np.arange(5, 50, 5),
        'volatility_threshold': np.arange(0.05, 0.2, 0.05)
    }
    model = HypothesisTester(tickers, start_date, end_date)
    random_search = RandomizedSearchCV(model, param_distributions=param_grid, n_iter=num_simulations, cv=3, scoring='accuracy', random_state=42, n_jobs=-1)
    # Create a dummy dataset
    dummy_X = np.zeros((len(tickers), 1))
    dummy_y = np.zeros(len(tickers))
    random_search.fit(dummy_X, dummy_y)
    return random_search.best_params_

# Test the hypothesis for a list of tickers
tickers = ['AAPL', 'GOOG', 'MSFT']
start_date = '2022-01-01'
end_date = '2022-01-31'
num_simulations = 100
best_params = monte_carlo_simulation(tickers, start_date, end_date, num_simulations)
print(best_params)
