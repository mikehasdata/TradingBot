# Import necessary libraries
import numpy as np
import pandas as pd

# Set initial variables
initial_cash = 10000
shares_held = 0
total_value = initial_cash
trades = []
positions = []

# Generate mock data
np.random.seed(42) # Set random seed for reproducibility
dates = pd.date_range(start='2021-01-01', end='2021-12-31', freq='D')
open_prices = np.random.randint(50, 150, size=len(dates))
close_prices = open_prices + np.random.randint(-10, 10, size=len(dates))

# Define buy/sell strategy
def strategy(open_price, close_price):
    if close_price > open_price:
        return 'BUY'
    elif close_price < open_price:
        return 'SELL'
    else:
        return 'HOLD'

# Implement backtesting logic
for i in range(len(dates)):
    date = dates[i]
    open_price = open_prices[i]
    close_price = close_prices[i]
    
    # Apply strategy
    action = strategy(open_price, close_price)
    
    # Update positions and cash
    if action == 'BUY':
        shares_held += 1
        total_value -= close_price
        trades.append([date, action, 1, close_price])
        positions.append([date, shares_held])
    elif action == 'SELL':
        shares_held -= 1
        total_value += close_price
        trades.append([date, action, 1, close_price])
        positions.append([date, shares_held])
    else:
        continue # Do nothing if HOLD
        
# Calculate performance metrics
final_cash = total_value
final_shares = shares_held
final_value = final_cash + final_shares * close_prices[-1]
profit_loss = final_value - initial_cash

# Print results
print("Final cash remaining: ${:.2f}".format(final_cash))
print("Shares held at the end of the period: {} shares".format(final_shares))
print("Total value of the portfolio (cash + shares' value): ${:.2f}".format(final_value))
print("Profit or loss: ${:.2f}".format(profit_loss))

# Visualize results
trades_df = pd.DataFrame(trades, columns=['Date', 'Action', 'Shares', 'Price'])
positions_df = pd.DataFrame(positions, columns=['Date', 'Shares'])
positions_df.set_index('Date', inplace=True)

# Plot portfolio value over time
portfolio_value = [initial_cash]
for i in range(len(trades)):
    date = trades[i][0]
    shares = positions_df.loc[date, 'Shares']
    price = trades[i][3]
    portfolio_value.append(portfolio_value[-1] + shares * price)
    
portfolio_value = pd.Series(portfolio_value, index=trades_df['Date'])
portfolio_value.plot(figsize=(10,6), title='Portfolio Value over Time')