import yfinance as yf
import numpy as np
import pandas as pd

# Define the ticker for WTI Crude Oil
ticker = "CL=F"

# Define the key dates
initial_pricing_date = "2023-12-14"
final_pricing_date = "2025-12-15"

# Fetch initial price with error handling
def fetch_price(ticker, date, attempts=5):
    for i in range(attempts):
        start_date = pd.to_datetime(date) + pd.Timedelta(days=i)
        end_date = start_date + pd.Timedelta(days=1)
        data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        if not data.empty:
            return data['Close'].values[0]
    raise ValueError(f"No data found for {ticker} starting from {date} after {attempts} attempts")

# Example usage
initial_price = fetch_price(ticker, initial_pricing_date)
print(f"Initial Price on {initial_pricing_date}: ${initial_price:.2f}")

# Calculate upper and lower knock-out prices
upper_knock_out_price = 1.40 * initial_price
lower_knock_out_price = 0.60 * initial_price

# Simulation parameters
num_simulations = 100000
num_days = (pd.to_datetime(final_pricing_date) - pd.to_datetime(initial_pricing_date)).days
dt = 1 / 252  # Assuming 252 trading days in a year

# Fetch historical data to estimate drift and volatility
historical_data = yf.download(ticker, start="1980-01-01", end=initial_pricing_date)
log_returns = np.log(historical_data['Close'] / historical_data['Close'].shift(1)).dropna()
drift = log_returns.mean() - 0.5 * log_returns.var()
volatility = log_returns.std()

# Simulation function
def simulate_price_paths(initial_price, drift, volatility, dt, num_days, num_simulations):
    price_paths = np.zeros((num_days, num_simulations))
    price_paths[0] = initial_price
    for t in range(1, num_days):
        rand = np.random.standard_normal(num_simulations)
        price_paths[t] = price_paths[t-1] * np.exp(drift * dt + volatility * np.sqrt(dt) * rand)
    return price_paths

# Simulate price paths
price_paths = simulate_price_paths(initial_price, drift, volatility, dt, num_days, num_simulations)

# Check for knock-out events
upper_knock_out_events = (price_paths >= upper_knock_out_price)
lower_knock_out_events = (price_paths <= lower_knock_out_price)
knock_out_events = upper_knock_out_events | lower_knock_out_events
knock_out = np.any(knock_out_events, axis=0)

# Final prices at maturity
final_prices = price_paths[-1]

# Calculate payoffs
denomination = 1000  # USD
variation = abs(final_prices - initial_price) / initial_price
payoffs = np.where(knock_out, 
                   denomination * 1.06, 
                   np.where(variation < 0.06, 
                            denomination * 1.06, 
                            denomination * (1 + variation)))

# Expected payoff
expected_payoff = np.mean(payoffs)
print(f"Expected Payoff: ${expected_payoff:.2f}")
