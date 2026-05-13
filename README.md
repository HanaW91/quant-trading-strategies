# Quant Trading Strategies

This repository contains implementations of algorithmic trading strategies and
backtesting experiments using Python.

The goal of this project is to explore quantitative trading ideas, evaluate their
performance using historical market data, and understand the statistical
properties of trading strategies.

## Strategies

Planned implementations include:

- Mean Reversion Strategy
- Momentum Strategy
- Pairs Trading (Statistical Arbitrage)
- Volatility-based Strategies

## Tools

Python
Pandas
NumPy
Matplotlib
Jupyter Notebook

## Data

Market data is obtained using the Python library yfinance. Committed CSV outputs
live in `data/`.

## Strategy Dashboard

The `dashboard/` folder includes a static GitHub Pages dashboard for AAPL, NVDA,
Samsung, SK Hynix, KOSPI, and additional growth/AI infrastructure tickers across
the 20/60 MA + MACD and 50/200 SMA + RSI + Stop Loss strategies.

GitHub Pages URL:
`https://hanaw91.github.io/quant-trading-strategies/`

The hosted Pages version uses the committed CSV and PNG outputs. The live
yfinance refresh endpoint requires the local Python server and is not available
on GitHub Pages.

## Project Structure

- `dashboard/` - static GitHub Pages dashboard
- `charts/` - generated PNG charts
- `data/` - CSV backtest results and summaries
- `scripts/` - Python backtest and refresh scripts
- `boeing_airbus_return_and_risk_analysis.ipynb` - notebook experiment
- `README.md`

## Goal

Build a collection of quantitative trading experiments and improve understanding
of financial markets, statistical modelling, and trading strategy evaluation.

## Example Strategy: Mean Reversion

The repository currently includes an implementation of a simple mean reversion
strategy.

Idea:
If the price deviates significantly from its moving average, it may revert back
to the mean.

Trading rule:

Buy when price < 20-day moving average
Sell when price > 20-day moving average

The strategy downloads historical market data and evaluates performance using
cumulative returns.

See:
`scripts/mean_reversion_strategy.py`

## Boeing vs Airbus Return and Risk Analysis

This notebook compares Boeing and Airbus stock performance using:

- daily returns
- monthly returns
- cumulative returns
- correlation and risk analysis

File:
`boeing_airbus_return_and_risk_analysis.ipynb`
