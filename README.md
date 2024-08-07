# Stock Price Analysis and Simulation

This project provides a set of scripts for analyzing stock price movements using various hypothesis tests and simulations. It includes tools for detecting price drops, recoveries, and running Monte Carlo simulations to optimize trading parameters.

## Project Structure

- **main.py**: The main script that orchestrates the execution of various tests and simulations.
- **fiveday_1u_hypothesis.py**: Script to check for a 5% price drop from the opening price over a specified period.
- **fiveday_1u_price_recovery.py**: Script to check for a specified price drop and a subsequent price increase within a given time frame.
- **fiveday_1u_validator.py**: Validates stock price events for specific conditions such as drops and gains within a day.
- **fiveday_1u_withStpLos.py**: Enhanced recovery check with stop-loss validation.
- **iteration_1.py**: Implements a hypothesis testing model and performs Monte Carlo simulation with parameter optimization.
- **Monte_Carlo_Intutive_mth.py**: Provides Monte Carlo simulation with intuitive methods for stock price movement analysis.
