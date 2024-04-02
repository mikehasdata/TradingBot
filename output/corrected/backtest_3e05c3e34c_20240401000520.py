# Import necessary libraries
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

# Set initial variables
cash_balance = 10000
short_ma = 20 # Short-term moving average
long_ma = 50 # Long-term moving average

# Load the data
data = pd.read_csv('mock_data.csv')

# Calculate moving averages
data['Short_MA'] = data['Close'].rolling(window=short_ma).mean()
data['Long_MA'] = data['Close'].rolling(window=long_ma).mean()

# Generate signals
data['Signal'] = np.where(data['Short_MA'] > data['Long_MA'], 1, 0) # 1 for buy signal, 0 for sell signal

# Backtest the strategy
for index, row in data.iterrows():
    if row['Signal'] == 1: # Buy signal
        shares_to_buy = cash_balance // row['Close'] # Calculate number of shares to buy based on available cash balance
        cash_balance -= shares_to_buy * row['Close'] # Update cash balance
    elif row['Signal'] == 0: # Sell signal
        cash_balance += shares_to_buy * row['Close'] # Update cash balance
        shares_to_buy = 0 # Reset shares to buy
    data.loc[index, 'Shares'] = shares_to_buy # Record number of shares held at each time step
    data.loc[index, 'Portfolio_Value'] = cash_balance + (shares_to_buy * row['Close']) # Calculate portfolio value at each time step

# Calculate total return
total_return = (data['Portfolio_Value'].iloc[-1] - 10000) / 10000 * 100 # Final portfolio value - initial cash balance / initial cash balance * 100

# Print results
print('Final portfolio value: $', round(data['Portfolio_Value'].iloc[-1], 2))
print('Total return: ', round(total_return, 2), '%')

# Plot portfolio value over time
data['Portfolio_Value'].plot()
plt.title('Portfolio Value over Time')
plt.xlabel('Time')
plt.ylabel('Portfolio Value ($)')
plt.show()