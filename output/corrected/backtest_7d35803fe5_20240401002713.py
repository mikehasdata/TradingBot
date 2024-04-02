# Import necessary libraries
import pandas as pd
import numpy as np

# Generate mock data
np.random.seed(42)
dates = pd.date_range(start='2020-01-01', end='2020-12-31', freq='D')
prices = np.random.randint(50, 100, size=len(dates))
df = pd.DataFrame({'Date': dates, 'Closing Price': prices})

# Set initial cash balance and create empty lists to track transactions and portfolio value
initial_balance = 10000
cash_balance = initial_balance
portfolio_value = [initial_balance]
transactions = []

# Loop through each row in the DataFrame
for i in range(1, len(df)):
    # Get previous day's closing price and today's closing price
    prev_price = df.loc[i-1, 'Closing Price']
    today_price = df.loc[i, 'Closing Price']
    # Check if today's closing price is higher than previous day's closing price
    if today_price > prev_price:
        # Buy one share at today's closing price
        cash_balance -= today_price
        transactions.append({'Date': df.loc[i, 'Date'], 'Action': 'Buy', 'Price': today_price})
    # Check if today's closing price is lower than previous day's closing price
    elif today_price < prev_price:
        # Sell all shares at today's closing price
        cash_balance += today_price
        transactions.append({'Date': df.loc[i, 'Date'], 'Action': 'Sell', 'Price': today_price})
    # Calculate portfolio value and append to list
    portfolio_value.append(cash_balance)

# Convert portfolio value list to DataFrame and add to original DataFrame
df['Portfolio Value'] = portfolio_value
# Print final portfolio value and profit
print('Final Portfolio Value: ${:.2f}'.format(portfolio_value[-1]))
print('Profit: ${:.2f}'.format(portfolio_value[-1] - initial_balance))
# Calculate return percentage
return_pct = (portfolio_value[-1] - initial_balance) / initial_balance * 100
print('Return Percentage: {:.2f}%'.format(return_pct))

# Print DataFrame
print(df)