import pandas as pd
import numpy as np

class SimpleBacktest:
    def __init__(self, initial_cash=10000):
        self.cash = initial_cash
        self.shares = 0
        self.portfolio_history = []
        
    def buy(self, price):
        if self.cash >= price:
            self.shares += 1
            self.cash -= price
            self.record_trade('buy', price)
            
    def sell(self, price):
        if self.shares > 0:
            self.shares -= 1
            self.cash += price
            self.record_trade('sell', price)
        
    def record_trade(self, action, price):
        self.portfolio_history.append({
            'Action': action,
            'Price': price,
            'Shares': self.shares,
            'Cash': self.cash,
            'Portfolio Value': self.get_portfolio_value(price)
        })

    def get_portfolio_value(self, price):
        return self.cash + self.shares * price

    def run_backtest(self, df):
        for index, row in df.iterrows():
            if row['Close'] > row['Open']:
                self.buy(row['Close'])
            elif row['Close'] < row['Open']:
                self.sell(row['Close'])
            else:
                # Nothing happens if the closing price is equal to the opening price
                pass
        # Record final value with the last close price
        self.record_trade('hold', df.iloc[-1]['Close'])
        return pd.DataFrame(self.portfolio_history)

# Backtest execution
backtest = SimpleBacktest()
result = backtest.run_backtest(df)

print("Final Portfolio Value: $", backtest.get_portfolio_value(df.iloc[-1]['Close']))
result.head()