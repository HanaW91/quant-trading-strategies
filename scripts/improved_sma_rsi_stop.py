from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from aapl_sma_crossover import CHARTS_DIR, DATA_DIR, download_prices_for_tickers, max_drawdown_pct, safe_output_prefix


def add_rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.rolling(period).mean()
    avg_loss = losses.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def add_strategy(
    data: pd.DataFrame,
    short_window: int,
    long_window: int,
    rsi_period: int,
    rsi_threshold: float,
    stop_loss_pct: float,
) -> pd.DataFrame:
    result = data.copy()
    result["short_sma"] = result["Close"].rolling(short_window).mean()
    result["long_sma"] = result["Close"].rolling(long_window).mean()
    result["rsi"] = add_rsi(result["Close"], rsi_period)
    result["entry_price"] = pd.NA
    result["stop_price"] = pd.NA
    result["exit_reason"] = pd.NA
    result["signal"] = 0

    in_position = False
    entry_price = 0.0
    stop_price = 0.0

    for index, row in result.iterrows():
        indicators_ready = pd.notna(row["short_sma"]) and pd.notna(row["long_sma"]) and pd.notna(row["rsi"])
        if not indicators_ready:
            continue

        trend_ok = row["short_sma"] > row["long_sma"]
        rsi_ok = row["rsi"] >= rsi_threshold

        if in_position:
            exit_reason = None
            if row["Low"] <= stop_price:
                exit_reason = "stop_loss"
            elif row["rsi"] < rsi_threshold:
                exit_reason = "rsi_exit"
            elif not trend_ok:
                exit_reason = "sma_exit"

            if exit_reason:
                in_position = False
                result.at[index, "exit_reason"] = exit_reason
                entry_price = 0.0
                stop_price = 0.0

        elif trend_ok and rsi_ok:
            in_position = True
            entry_price = float(row["Close"])
            stop_price = entry_price * (1 - stop_loss_pct)

        result.at[index, "signal"] = int(in_position)
        if in_position:
            result.at[index, "entry_price"] = entry_price
            result.at[index, "stop_price"] = stop_price

    result["position_change"] = result["signal"].diff().fillna(0)
    result["market_return"] = result["Close"].pct_change()
    result["strategy_return"] = result["signal"].shift(1) * result["market_return"]
    result["market_equity"] = (1 + result["market_return"].fillna(0)).cumprod()
    result["strategy_equity"] = (1 + result["strategy_return"].fillna(0)).cumprod()
    return result


def summarize(results: pd.DataFrame) -> dict[str, float | int | str]:
    completed = results.dropna(subset=["short_sma", "long_sma", "rsi"]).copy()
    if completed.empty:
        raise ValueError("Not enough data to calculate 50/200 SMA + RSI strategy.")

    return {
        "start": completed.index[0].strftime("%Y-%m-%d"),
        "end": completed.index[-1].strftime("%Y-%m-%d"),
        "buy_signals": int((completed["position_change"] == 1).sum()),
        "sell_signals": int((completed["position_change"] == -1).sum()),
        "stop_loss_exits": int((completed["exit_reason"] == "stop_loss").sum()),
        "rsi_exits": int((completed["exit_reason"] == "rsi_exit").sum()),
        "sma_exits": int((completed["exit_reason"] == "sma_exit").sum()),
        "final_signal": int(completed["signal"].iloc[-1]),
        "market_return_pct": (completed["market_equity"].iloc[-1] - 1) * 100,
        "strategy_return_pct": (completed["strategy_equity"].iloc[-1] - 1) * 100,
        "max_drawdown_pct": max_drawdown_pct(completed["strategy_equity"]),
    }


def plot_signals(results: pd.DataFrame, ticker: str, output: str, short_window: int, long_window: int) -> None:
    completed = results.dropna(subset=["short_sma", "long_sma", "rsi"]).copy()
    buys = completed[completed["position_change"] == 1]
    sells = completed[completed["position_change"] == -1]

    fig, (price_ax, rsi_ax) = plt.subplots(
        2,
        1,
        figsize=(14, 9),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )
    price_ax.plot(completed.index, completed["Close"], label="Close", color="#1f2937", linewidth=1.4)
    price_ax.plot(completed.index, completed["short_sma"], label=f"SMA{short_window}", color="#2563eb", linewidth=1.1)
    price_ax.plot(completed.index, completed["long_sma"], label=f"SMA{long_window}", color="#d97706", linewidth=1.1)
    price_ax.scatter(buys.index, buys["Close"], marker="^", color="#16a34a", edgecolor="white", linewidth=0.8, s=90, label="Buy", zorder=5)
    price_ax.scatter(sells.index, sells["Close"], marker="v", color="#dc2626", edgecolor="white", linewidth=0.8, s=90, label="Sell", zorder=5)
    price_ax.set_title(f"{ticker} SMA{short_window}/SMA{long_window} with RSI Filter and Stop Loss")
    price_ax.set_ylabel("Adjusted close price")
    price_ax.grid(True, alpha=0.25)
    price_ax.legend()

    rsi_ax.plot(completed.index, completed["rsi"], label="RSI", color="#7c3aed", linewidth=1)
    rsi_ax.axhline(50, color="#6b7280", linewidth=0.8)
    rsi_ax.set_xlabel("Date")
    rsi_ax.set_ylabel("RSI")
    rsi_ax.grid(True, alpha=0.25)
    rsi_ax.legend()

    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def run_ticker(ticker: str, prices: pd.DataFrame, args: argparse.Namespace) -> dict[str, float | int | str]:
    prefix = safe_output_prefix(ticker)
    DATA_DIR.mkdir(exist_ok=True)
    CHARTS_DIR.mkdir(exist_ok=True)
    results_output = DATA_DIR / f"{prefix}_improved_sma_crossover_results.csv"
    chart_output = CHARTS_DIR / f"{prefix}_improved_sma_crossover_signals.png"
    results = add_strategy(
        prices,
        short_window=args.short_window,
        long_window=args.long_window,
        rsi_period=args.rsi_period,
        rsi_threshold=args.rsi_threshold,
        stop_loss_pct=args.stop_loss_pct,
    )
    summary = summarize(results)
    summary["ticker"] = ticker
    summary["results_output"] = f"../data/{results_output.name}"
    summary["chart_output"] = f"../charts/{chart_output.name}"

    results.to_csv(results_output)
    plot_signals(results, ticker, chart_output, args.short_window, args.long_window)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run 50/200 SMA + RSI + stop-loss strategy.")
    parser.add_argument("--tickers", nargs="+", default=["AAPL", "NVDA"])
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--short-window", type=int, default=50)
    parser.add_argument("--long-window", type=int, default=200)
    parser.add_argument("--rsi-period", type=int, default=14)
    parser.add_argument("--rsi-threshold", type=float, default=50)
    parser.add_argument("--stop-loss-pct", type=float, default=0.10)
    parser.add_argument("--comparison-output", default="improved_strategy_comparison.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tickers = [ticker.upper() for ticker in args.tickers]
    prices_by_ticker = download_prices_for_tickers(tickers, args.start, args.end)
    summaries = [run_ticker(ticker, prices_by_ticker[ticker], args) for ticker in tickers]

    comparison = pd.DataFrame(summaries)
    comparison = comparison[
        [
            "ticker",
            "start",
            "end",
            "buy_signals",
            "sell_signals",
            "stop_loss_exits",
            "rsi_exits",
            "sma_exits",
            "final_signal",
            "market_return_pct",
            "strategy_return_pct",
            "max_drawdown_pct",
            "results_output",
            "chart_output",
        ]
    ]
    DATA_DIR.mkdir(exist_ok=True)
    comparison.to_csv(DATA_DIR / Path(args.comparison_output).name, index=False)

    display = comparison.copy()
    for column in ["market_return_pct", "strategy_return_pct", "max_drawdown_pct"]:
        display[column] = display[column].map("{:.2f}%".format)
    print(display.to_string(index=False))
    print(f"Saved comparison to {Path(args.comparison_output).name}")


if __name__ == "__main__":
    main()
