import pandas as pd
import numpy as np
from pandas_ta import df

# Initialize the position and total_profit variables
position = 0  # No position initially
cash = 10000  # Starting cash
total_profit = 0

# Define the percentage for buy/sell trigger
threshold = 0.01

# List to keep track of portfolio value over time
portfolio_values = []

# Backtesting logic
for index, row in df.iterrows():
    price_change = (row['Close'] - row['Open']) / row['Open']
    
    if price_change <= -threshold and cash >= row['Close']:
        # Buy logic
        position += 1
        cash -= row['Close']
        print(f"Bought on {index.date()}, Close Price: {row['Close']:.2f}, Cash remaining: {cash:.2f}")
        
    elif price_change >= threshold and position > 0:
        # Sell logic
        position -= 1
        cash += row['Close']
        profit = row['Close'] - df.loc[df.index < index, 'Close'].iloc[-1]  # Profit from this trade
        total_profit += profit
        print(f"Sold on {index.date()}, Close Price: {row['Close']:.2f}, Cash: {cash:.2f}, Profit: {profit:.2f}")
    
    # Update portfolio value
    portfolio_value = cash + position * row['Close']
    portfolio_values.append(portfolio_value)

# Final portfolio value after last day
final_portfolio_value = cash + position * df.iloc[-1]['Close']
total_profit += position * (df.iloc[-1]['Close'] - df.iloc[-(position+1)]['Close']) if position > 0 else 0

# Output the results of the backtest
print(f"Final Portfolio Value: {final_portfolio_value:.2f}")
print(f"Total Profit/Loss: {total_profit:.2f}")

# Create a DataFrame for portfolio values
portfolio_df = pd.DataFrame(data=portfolio_values, columns=['Portfolio_Value'], index=df.index)

# Let's plot the portfolio value over time
portfolio_df.plot(title="Portfolio Value over Time", figsize=(10, 5))