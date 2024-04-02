# As anticipated, we don't have the `backtesting.py` package available in this environment. However, this should not deter us from preparing the code as needed. Let me continue to adapt the pseudo-code to script form as if the package were available.
#
# We'll use the provided CSV path '/mnt/data/BTC-USD-15m-2023-1-01T00_00 (1).csv' to load the historical data and create the strategy. Please upload the CSV file with the historical data to this path so I can access it and proceed with the backtesting script.
# To implement the RSI-based trading strategy described and backtest it using `backtesting.py`, we first need to install the package and load the necessary historical data. Then we'll set up the backtest according to the strategy rules.
#
# Given that the internet is disabled, I cannot install any external packages directly; however, I can use the packages already available in the environment. Let's first ensure that `backtesting.py` is available to use.
#
# If `backtesting.py` is not available, we'll proceed assuming its standard API and proceed with the code assuming that it is present. The code will define a strategy class that inherits from `backtesting.Strategy`, within which we'll implement the RSI calculations, confirmation checks, and trading signals as per the described rules.
#
# Please note that I'll need to work with the assumption of what the `backtesting.py` API looks like, as I can't verify the exact functionality without the package.
#
# We'll start by proceeding with the pseudo-code using some placeholders for parts of the strategy that cannot be exactly replicated without real data or further details (such as the exact method of price action confirmation or VWAP calculation). Then we can adjust the code for an actual backtest once we load the data and know which packages are available.
#
# Let me begin by writing the pseudo-code to outline the steps we will take.