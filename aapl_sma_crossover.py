"""
Download price data with yfinance and run a 50/50 portfolio strategy:
50% buy-and-hold plus 50% active trading using an MA20/MA60 crossover
with MACD confirmation.

Install dependencies:
    pip install yfinance pandas matplotlib

Example:
    python aapl_sma_crossover.py --tickers AAPL NVDA --start 2020-01-01 --end 2026-01-01
"""

from __future__ import annotations

import argparse
import math
import re

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


def safe_output_prefix(ticker: str) -> str:
    """Return a lowercase filename-safe prefix for ticker-specific outputs."""
    prefix = re.sub(r"[^a-zA-Z0-9]+", "_", ticker).strip("_").lower()
    return prefix or "ticker"


def download_prices(ticker: str, start: str, end: str | None) -> pd.DataFrame:
    """Download daily OHLCV data and return a clean DataFrame."""
    data = yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
    )

    if data.empty:
        raise ValueError(f"No data returned for {ticker}. Check the ticker/date range.")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data.dropna()


def download_prices_for_tickers(
    tickers: list[str],
    start: str,
    end: str | None,
) -> dict[str, pd.DataFrame]:
    """Download prices for one or more tickers in a single yfinance request."""
    if len(tickers) == 1:
        return {tickers[0]: download_prices(tickers[0], start, end)}

    data = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        group_by="ticker",
        threads=True,
    )

    if data.empty:
        raise ValueError(f"No data returned for {', '.join(tickers)}.")

    prices: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        if not isinstance(data.columns, pd.MultiIndex):
            raise ValueError("Expected multi-ticker data but yfinance returned flat columns.")

        level_0 = data.columns.get_level_values(0)
        level_1 = data.columns.get_level_values(1)
        if ticker in level_0:
            ticker_data = data[ticker]
        elif ticker in level_1:
            ticker_data = data.xs(ticker, axis=1, level=1)
        else:
            raise ValueError(f"No data returned for {ticker}.")

        ticker_data = ticker_data.dropna()
        if ticker_data.empty:
            raise ValueError(f"No usable data returned for {ticker}.")
        prices[ticker] = ticker_data

    return prices


def add_ma_macd_strategy(
    data: pd.DataFrame,
    short_window: int,
    long_window: int,
    macd_fast: int,
    macd_slow: int,
    macd_signal: int,
    buy_hold_weight: float,
) -> pd.DataFrame:
    """Add MA/MACD signals and 50/50 sleeve-level performance."""
    if short_window >= long_window:
        raise ValueError("short_window must be smaller than long_window.")
    if macd_fast >= macd_slow:
        raise ValueError("macd_fast must be smaller than macd_slow.")
    if not 0 <= buy_hold_weight <= 1:
        raise ValueError("buy_hold_weight must be between 0 and 1.")

    active_weight = 1 - buy_hold_weight
    result = data.copy()
    result["ma_short"] = result["Close"].rolling(window=short_window).mean()
    result["ma_long"] = result["Close"].rolling(window=long_window).mean()
    result["macd"] = result["Close"].ewm(span=macd_fast, adjust=False).mean() - result[
        "Close"
    ].ewm(span=macd_slow, adjust=False).mean()
    result["macd_signal"] = result["macd"].ewm(span=macd_signal, adjust=False).mean()
    result["macd_histogram"] = result["macd"] - result["macd_signal"]

    trend_is_bullish = result["ma_short"] > result["ma_long"]
    macd_confirms = result["macd"] > result["macd_signal"]
    result["signal"] = (trend_is_bullish & macd_confirms).astype(int)
    result.loc[result[["ma_short", "ma_long", "macd", "macd_signal"]].isna().any(axis=1), "signal"] = 0
    result["position_change"] = result["signal"].diff().fillna(0)
    result["active_position"] = result["signal"]
    result["total_exposure"] = buy_hold_weight + active_weight * result["active_position"]

    result["market_return"] = result["Close"].pct_change()
    result["active_return"] = result["active_position"].shift(1) * result["market_return"]
    result["market_equity"] = (1 + result["market_return"].fillna(0)).cumprod()
    result["active_equity"] = (1 + result["active_return"].fillna(0)).cumprod()
    result["portfolio_equity"] = (
        buy_hold_weight * result["market_equity"] + active_weight * result["active_equity"]
    )
    result["portfolio_return"] = result["portfolio_equity"].pct_change()
    result["buy_hold_weight"] = buy_hold_weight
    result["active_weight"] = active_weight

    return result


def max_drawdown_pct(equity: pd.Series) -> float:
    running_peak = equity.cummax()
    return float((equity / running_peak - 1).min() * 100)


def sharpe_ratio(returns: pd.Series) -> float:
    clean_returns = returns.dropna()
    volatility = clean_returns.std()
    if clean_returns.empty or volatility == 0:
        return float("nan")
    return float((clean_returns.mean() / volatility) * math.sqrt(252))


def summarize_strategy(results: pd.DataFrame) -> dict[str, float | int | str]:
    """Return a compact performance summary for the strategy."""
    completed = results.dropna(subset=["ma_short", "ma_long", "macd", "macd_signal"]).copy()

    if completed.empty:
        raise ValueError("Not enough data to calculate indicators.")

    buy_signals = int((completed["position_change"] == 1).sum())
    sell_signals = int((completed["position_change"] == -1).sum())
    market_total = completed["market_equity"].iloc[-1]
    active_total = completed["active_equity"].iloc[-1]
    portfolio_total = completed["portfolio_equity"].iloc[-1]
    active_days = int(completed["active_position"].sum())

    return {
        "start": completed.index[0].strftime("%Y-%m-%d"),
        "end": completed.index[-1].strftime("%Y-%m-%d"),
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "final_active_signal": int(completed["active_position"].iloc[-1]),
        "active_days": active_days,
        "active_days_pct": active_days / len(completed) * 100,
        "buy_hold_return_pct": (market_total - 1) * 100,
        "active_sleeve_return_pct": (active_total - 1) * 100,
        "portfolio_return_pct": (portfolio_total - 1) * 100,
        "portfolio_sharpe_ratio": sharpe_ratio(completed["portfolio_return"]),
        "buy_hold_max_drawdown_pct": max_drawdown_pct(completed["market_equity"]),
        "active_sleeve_max_drawdown_pct": max_drawdown_pct(completed["active_equity"]),
        "portfolio_max_drawdown_pct": max_drawdown_pct(completed["portfolio_equity"]),
    }


def plot_price_signals(
    results: pd.DataFrame,
    ticker: str,
    output: str,
    short_window: int,
    long_window: int,
) -> None:
    """Save a price chart with MA/MACD buy and reduce markers."""
    completed = results.dropna(subset=["ma_short", "ma_long", "macd", "macd_signal"]).copy()

    if completed.empty:
        raise ValueError("Not enough data to plot indicators.")

    buys = completed[completed["position_change"] == 1]
    sells = completed[completed["position_change"] == -1]

    fig, (price_ax, macd_ax) = plt.subplots(
        2,
        1,
        figsize=(14, 9),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )
    price_ax.plot(completed.index, completed["Close"], label="Close", color="#1f2937", linewidth=1.4)
    price_ax.plot(
        completed.index,
        completed["ma_short"],
        label=f"MA{short_window}",
        color="#2563eb",
        linewidth=1.1,
    )
    price_ax.plot(
        completed.index,
        completed["ma_long"],
        label=f"MA{long_window}",
        color="#d97706",
        linewidth=1.1,
    )
    price_ax.scatter(
        buys.index,
        buys["Close"],
        marker="^",
        color="#16a34a",
        edgecolor="white",
        linewidth=0.8,
        s=90,
        label="Add active sleeve",
        zorder=5,
    )
    price_ax.scatter(
        sells.index,
        sells["Close"],
        marker="v",
        color="#dc2626",
        edgecolor="white",
        linewidth=0.8,
        s=90,
        label="Reduce active sleeve",
        zorder=5,
    )
    price_ax.set_title(f"{ticker} MA{short_window}/MA{long_window} with MACD Confirmation")
    price_ax.set_ylabel("Adjusted close price")
    price_ax.grid(True, alpha=0.25)
    price_ax.legend()

    macd_ax.plot(completed.index, completed["macd"], label="MACD", color="#2563eb", linewidth=1)
    macd_ax.plot(
        completed.index,
        completed["macd_signal"],
        label="MACD signal",
        color="#dc2626",
        linewidth=1,
    )
    macd_ax.axhline(0, color="#6b7280", linewidth=0.8)
    macd_ax.set_xlabel("Date")
    macd_ax.set_ylabel("MACD")
    macd_ax.grid(True, alpha=0.25)
    macd_ax.legend()

    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def run_ticker(
    ticker: str,
    prices: pd.DataFrame,
    args: argparse.Namespace,
    results_output: str,
    chart_output: str,
) -> dict[str, float | int | str]:
    results = add_ma_macd_strategy(
        prices,
        short_window=args.short_window,
        long_window=args.long_window,
        macd_fast=args.macd_fast,
        macd_slow=args.macd_slow,
        macd_signal=args.macd_signal,
        buy_hold_weight=args.buy_hold_weight,
    )
    summary = summarize_strategy(results)
    summary["ticker"] = ticker
    summary["results_output"] = results_output
    summary["chart_output"] = chart_output

    results.to_csv(results_output)
    plot_price_signals(
        results,
        ticker=ticker,
        output=chart_output,
        short_window=args.short_window,
        long_window=args.long_window,
    )

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a 50/50 buy-and-hold plus MA/MACD active trading strategy."
    )
    parser.add_argument("--ticker", default="AAPL", help="Ticker symbol to download.")
    parser.add_argument(
        "--tickers",
        nargs="+",
        help="One or more ticker symbols to run in one command. Overrides --ticker.",
    )
    parser.add_argument("--start", default="2020-01-01", help="Start date, YYYY-MM-DD.")
    parser.add_argument("--end", default=None, help="End date, YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--short-window", type=int, default=20, help="Short moving average window.")
    parser.add_argument("--long-window", type=int, default=60, help="Long moving average window.")
    parser.add_argument("--macd-fast", type=int, default=12, help="MACD fast EMA span.")
    parser.add_argument("--macd-slow", type=int, default=26, help="MACD slow EMA span.")
    parser.add_argument("--macd-signal", type=int, default=9, help="MACD signal EMA span.")
    parser.add_argument(
        "--buy-hold-weight",
        type=float,
        default=0.50,
        help="Portfolio weight permanently assigned to buy-and-hold.",
    )
    parser.add_argument(
        "--output",
        default="ma_macd_results.csv",
        help="CSV file for results when running one ticker.",
    )
    parser.add_argument(
        "--chart-output",
        default="ma_macd_signals.png",
        help="PNG file for the price chart when running one ticker.",
    )
    parser.add_argument(
        "--comparison-output",
        default="ma_macd_strategy_comparison.csv",
        help="CSV file for the multi-ticker comparison summary.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tickers = [ticker.upper() for ticker in (args.tickers or [args.ticker])]
    prices_by_ticker = download_prices_for_tickers(tickers, args.start, args.end)

    output_paths = {}
    for ticker in tickers:
        if len(tickers) == 1:
            output_paths[ticker] = (args.output, args.chart_output)
        else:
            prefix = safe_output_prefix(ticker)
            output_paths[ticker] = (
                f"{prefix}_ma20_ma60_macd_results.csv",
                f"{prefix}_ma20_ma60_macd_signals.png",
            )

    summaries = [
        run_ticker(ticker, prices_by_ticker[ticker], args, *output_paths[ticker])
        for ticker in tickers
    ]

    comparison = pd.DataFrame(summaries)
    comparison = comparison[
        [
            "ticker",
            "start",
            "end",
            "buy_signals",
            "sell_signals",
            "final_active_signal",
            "active_days_pct",
            "buy_hold_return_pct",
            "active_sleeve_return_pct",
            "portfolio_return_pct",
            "portfolio_sharpe_ratio",
            "buy_hold_max_drawdown_pct",
            "active_sleeve_max_drawdown_pct",
            "portfolio_max_drawdown_pct",
            "results_output",
            "chart_output",
        ]
    ]
    comparison["portfolio_sharpe_ratio"] = pd.to_numeric(
        comparison["portfolio_sharpe_ratio"],
        errors="coerce",
    )
    comparison.to_csv(args.comparison_output, index=False)

    print("\nStrategy settings")
    print("-----------------")
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Portfolio split: {args.buy_hold_weight:.0%} buy-and-hold / {1 - args.buy_hold_weight:.0%} active")
    print(f"Moving averages: MA{args.short_window} / MA{args.long_window}")
    print(f"MACD: {args.macd_fast}, {args.macd_slow}, {args.macd_signal}")
    print("Active sleeve: invested when MA20 > MA60 and MACD > MACD signal; otherwise cash")
    print(f"Saved comparison to {args.comparison_output}")

    print("\nComparison")
    print("----------")
    display = comparison.copy()
    display["active_signal"] = display["final_active_signal"].map({1: "Long", 0: "Cash"})
    pct_columns = [
        "active_days_pct",
        "buy_hold_return_pct",
        "active_sleeve_return_pct",
        "portfolio_return_pct",
        "buy_hold_max_drawdown_pct",
        "active_sleeve_max_drawdown_pct",
        "portfolio_max_drawdown_pct",
    ]
    for column in pct_columns:
        display[column] = display[column].map("{:.2f}%".format)
    display["portfolio_sharpe_ratio"] = display["portfolio_sharpe_ratio"].map(
        lambda value: "N/A" if pd.isna(value) else f"{value:.2f}"
    )

    print(
        display[
            [
                "ticker",
                "start",
                "end",
                "buy_signals",
                "sell_signals",
                "active_signal",
                "active_days_pct",
                "buy_hold_return_pct",
                "active_sleeve_return_pct",
                "portfolio_return_pct",
                "portfolio_sharpe_ratio",
                "portfolio_max_drawdown_pct",
            ]
        ].to_string(index=False)
    )

    for summary in summaries:
        print(f"Saved {summary['ticker']} results to {summary['results_output']}")
        print(f"Saved {summary['ticker']} chart to {summary['chart_output']}")


if __name__ == "__main__":
    main()
