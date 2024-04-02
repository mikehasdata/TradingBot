# Certainly! Below is the corrected Python script:

# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Generate mock data
date_range = pd.date_range(start="2020-01-01", end="2020-12-31", freq='D')
np.random.seed(42)
prices = np.random.lognormal(mean=0, sigma=0.1, size=len(date_range))
volume = np.random.randint(100, 1000, size=len(date_range))

df = pd.DataFrame({
    'Open': prices,
    'High': prices * np.random.uniform(1, 1.1, size=len(date_range)),
    'Low': prices * np.random.uniform(0.9, 1, size=len(date_range)),
    'Close': prices,
    'Volume': volume
}, index=date_range)

# Calculate moving averages
short_window = 10
long_window = 50

df['Short_MA'] = df['Close'].rolling(window=short_window, min_periods=1).mean()
df['Long_MA'] = df['Close'].rolling(window=long_window, min_periods=1).mean()

# Define the strategy
df['Signal'] = 0
df['Signal'][short_window:] = np.where(df['Short_MA'][short_window:] > df['Long_MA'][short_window:], 1, 0)
df['Position'] = df['Signal'].diff()

# Simulate trading
initial_cash = 10000
cash = initial_cash
shares_held = 0
portfolio_value = []

for index, row in df.iterrows():
    if row['Position'] == 1: # Buy signal
        shares_held += 1
        cash -= row['Close']
    elif row['Position'] == -1 and shares_held > 0: # Sell signal
        shares_held -= 1
        cash += row['Close']
    
    portfolio_value.append(cash + shares_held * row['Close'])

# Record portfolio value into the DataFrame and plot results
df['Portfolio_Value'] = portfolio_value

# Plot portfolio value over time
df['Portfolio_Value'].plot()
plt.title('Portfolio Value Over Time')
plt.xlabel('Date')
plt.ylabel('Portfolio Value')
plt.show()

# Print final portfolio and cash
print(f"Final Portfolio Value: {df['Portfolio_Value'].iloc[-1]:.2f}")
print(f"Final Cash: {cash:.2f}")
print(f"Shares Held: {shares_held}")

# The script is now corrected and can be executed to backtest the moving average crossover strategy. Some assumptions were made, such as the absence of transaction costs and slippage, which may affect the results in a real-world scenario. Additionally, the script could be further improved by incorporating risk management techniques and optimizing the strategy parameters.