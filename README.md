# TwinWinOption
Pricing of a Complex Financial Derivative Using Black-Scholes Formula and Monte Carlo Simulation

Project Overview

This project implements a Monte Carlo simulation to estimate the pricing of a complex financial derivative, specifically tied to WTI Crude Oil (symbol: CL=F). It simulates the price path of the underlying asset over time and evaluates the derivative’s payoff under specific conditions using knock-out barriers. Additionally, we use historical data to estimate the drift and volatility required for the simulation and apply the Black-Scholes formula to approximate price movements.

Key features of this project include:

	•	Fetching historical data using the yfinance library.
	•	Simulating price paths using Monte Carlo methods.
	•	Applying upper and lower knock-out conditions.
	•	Calculating the expected payoff of the derivative.

Prerequisites

Ensure that you have the following Python packages installed:

pip install yfinance numpy pandas

How It Works

1. Fetching the Initial Price

The script begins by fetching the initial price of WTI Crude Oil on a specific start date (e.g., "2023-12-14"). If data is unavailable for the exact date, the script attempts to fetch the closest available data within a certain number of days.

# Example to fetch the price for the start date
initial_price = fetch_price(ticker="CL=F", date="2023-12-14")
print(f"Initial Price on 2023-12-14: ${initial_price:.2f}")

2. Defining Knock-Out Prices

The derivative has upper and lower knock-out barriers, calculated as:

	•	Upper Knock-Out: 1.40 times the initial price.
	•	Lower Knock-Out: 0.60 times the initial price.

upper_knock_out_price = 1.40 * initial_price
lower_knock_out_price = 0.60 * initial_price

3. Estimating Drift and Volatility

To perform the simulation, we need to estimate the drift and volatility of the underlying asset using historical data. The drift is adjusted by subtracting half the variance of the log returns.

# Fetch historical data to estimate drift and volatility
historical_data = yf.download(ticker, start="1980-01-01", end=initial_pricing_date)
log_returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1)).dropna()
drift = log_returns.mean() - 0.5 * log_returns.var()
volatility = log_returns.std()

4. Monte Carlo Simulation

We simulate multiple price paths of the asset over the derivative’s lifetime (in this case, two years), using the estimated drift and volatility. Each path is updated based on the Geometric Brownian Motion model.

price_paths = simulate_price_paths(initial_price, drift, volatility, dt, num_days, num_simulations)

5. Check for Knock-Out Events

During the simulation, the code checks whether the price path hits the upper or lower knock-out barrier at any point. If a knock-out occurs, a specific payoff condition is applied.

upper_knock_out_events = (price_paths >= upper_knock_out_price)
lower_knock_out_events = (price_paths <= lower_knock_out_price)
knock_out = np.any(upper_knock_out_events | lower_knock_out_events, axis=0)

6. Calculate Payoffs

The payoffs for each simulation are calculated based on whether a knock-out event occurred. The payoff structure includes:

	•	A fixed denomination of $1000.
	•	A 6% increase in value if there is no significant variation or a knock-out event.
	•	Payoff proportional to the price variation if there is no knock-out and the price has varied significantly.

payoffs = np.where(knock_out, 
                   denomination * 1.06, 
                   np.where(variation < 0.06, 
                            denomination * 1.06, 
                            denomination * (1 + variation)))

7. Expected Payoff

Finally, the expected payoff is calculated by taking the mean of all simulated payoffs.

expected_payoff = np.mean(payoffs)
print(f"Expected Payoff: ${expected_payoff:.2f}")

Project Files

	•	pricing_simulation.py: The main Python script that contains all the necessary code to run the pricing simulation, including price fetching, knock-out condition checks, Monte Carlo simulations, and payoff calculations.

How to Run

	1.	Clone the repository and navigate to the project folder:

git clone <repository-url>
cd pricing_simulation

	2.	Install the required dependencies:

pip install yfinance numpy pandas

	3.	Run the script:

You can run the main pricing simulation using the following command:

python pricing_simulation.py

Key Parameters

	•	ticker: The ticker symbol for the asset (e.g., "CL=F" for WTI Crude Oil).
	•	initial_pricing_date: The start date of the derivative.
	•	final_pricing_date: The maturity date of the derivative.
	•	num_simulations: Number of Monte Carlo simulations (default is 100,000).
	•	denomination: The notional amount of the derivative (default is $1000).

Output

	•	The script prints the initial price of the underlying asset, the expected payoff of the derivative, and various internal parameters such as the knock-out prices.
	•	The expected payoff is calculated based on the knock-out conditions and Monte Carlo simulation results.
