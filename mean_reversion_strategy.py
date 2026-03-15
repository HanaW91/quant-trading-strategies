import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------------
# Download historical stock data
# -----------------------------------

ticker = "AAPL"
data = yf.download(ticker, start="2015-01-01", end="2024-01-01")

# -----------------------------------
# Compute moving average
# -----------------------------------

data["MA20"] = data["Close"].rolling(window=20).mean()

# -----------------------------------
# Generate trading signals
# -----------------------------------

data["signal"] = 0

# Buy when price is below moving average
data.loc[data["Close"] < data["MA20"], "signal"] = 1

# Sell when price is above moving average
data.loc[data["Close"] > data["MA20"], "signal"] = -1

# -----------------------------------
# Compute strategy returns
# -----------------------------------

data["returns"] = data["Close"].pct_change()
data["strategy_returns"] = data["returns"] * data["signal"].shift(1)

# -----------------------------------
# Plot price and moving average
# -----------------------------------

plt.figure(figsize=(10,5))
plt.plot(data["Close"], label="Price")
plt.plot(data["MA20"], label="20-day MA")
plt.title("Mean Reversion Strategy")
plt.legend()
plt.show()

# -----------------------------------
# Evaluate performance
# -----------------------------------

cumulative_returns = (1 + data["strategy_returns"]).cumprod()

plt.figure(figsize=(10,5))
plt.plot(cumulative_returns)
plt.title("Strategy Performance")
plt.show()

print("Final cumulative return:", cumulative_returns.iloc[-1])
