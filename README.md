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

Market data will be obtained using the Python library yfinance.

## Project Structure

quant-trading-strategies  
│  
├── notebooks  
│   └── strategy experiments  

├── src  
│   └── backtesting scripts  

├── data  
│   └── market datasets  

└── README.md

## Goal

Build a collection of quantitative trading experiments and improve understanding
of financial markets, statistical modelling, and trading strategy evaluation.

## Example Strategy: Mean Reversion

The repository currently includes an implementation of a simple mean reversion strategy.

Idea:
If the price deviates significantly from its moving average, it may revert back to the mean.

Trading rule:

Buy when price < 20-day moving average  
Sell when price > 20-day moving average  

The strategy downloads historical market data and evaluates performance using
cumulative returns.

See:

mean_reversion_strategy.ipynb
