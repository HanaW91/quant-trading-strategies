from __future__ import annotations

import argparse
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse

import pandas as pd

from aapl_sma_crossover import download_prices_for_tickers, run_ticker, safe_output_prefix
from improved_sma_rsi_stop import run_ticker as run_improved_ticker


ROOT = Path(__file__).resolve().parent
US_TICKERS = ["AAPL", "NVDA"]
KOREA_TICKERS = ["005930.KS", "000660.KS", "^KS11"]
AI_INFRA_TICKERS = ["VST", "CEG", "EQIX", "AMAT", "ASML", "LRCX"]
GROWTH_ETF_TICKERS = ["TSLA", "AMD", "QQQ", "SPY"]
REFRESH_LOCK = threading.Lock()
LAST_REFRESH: dict[str, object] = {}


def strategy_args(start: str, end: str | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        start=start,
        end=end,
        short_window=20,
        long_window=60,
        macd_fast=12,
        macd_slow=26,
        macd_signal=9,
        buy_hold_weight=0.50,
    )


def improved_args(start: str, end: str | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        start=start,
        end=end,
        short_window=50,
        long_window=200,
        rsi_period=14,
        rsi_threshold=50,
        stop_loss_pct=0.10,
    )


def run_group(tickers: list[str], start: str, comparison_output: str) -> list[dict[str, object]]:
    args = strategy_args(start=start)
    prices_by_ticker = download_prices_for_tickers(tickers, args.start, args.end)
    summaries = []

    for ticker in tickers:
        prefix = safe_output_prefix(ticker)
        summaries.append(
            run_ticker(
                ticker=ticker,
                prices=prices_by_ticker[ticker],
                args=args,
                results_output=str(ROOT / f"{prefix}_ma20_ma60_macd_results.csv"),
                chart_output=str(ROOT / f"{prefix}_ma20_ma60_macd_signals.png"),
            )
        )

    comparison = pd.DataFrame(summaries)
    columns = [
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
    comparison = comparison[columns]
    comparison["results_output"] = comparison["results_output"].map(lambda path: Path(path).name)
    comparison["chart_output"] = comparison["chart_output"].map(lambda path: Path(path).name)
    comparison = preserve_sentiment_columns(comparison, ROOT / comparison_output)
    comparison.to_csv(ROOT / comparison_output, index=False)

    return comparison.to_dict(orient="records")


def preserve_sentiment_columns(comparison: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    if not output_path.exists():
        return comparison

    existing = pd.read_csv(output_path)
    sentiment_columns = [
        "sentiment_score",
        "sentiment_label",
        "article_count",
        "positive_articles",
        "negative_articles",
        "neutral_articles",
        "recommendation",
        "top_headline",
        "top_url",
        "sentiment_updated_at",
    ]
    available = [column for column in sentiment_columns if column in existing.columns]
    if not available:
        return comparison

    return comparison.merge(existing[["ticker", *available]], on="ticker", how="left")


def run_improved_group(tickers: list[str], start: str, comparison_output: str) -> list[dict[str, object]]:
    args = improved_args(start=start)
    prices_by_ticker = download_prices_for_tickers(tickers, args.start, args.end)
    summaries = []

    for ticker in tickers:
        summary = run_improved_ticker(ticker, prices_by_ticker[ticker], args)
        summaries.append(summary)

    comparison = pd.DataFrame(summaries)
    columns = [
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
    comparison = comparison[columns]
    comparison.to_csv(ROOT / comparison_output, index=False)
    return comparison.to_dict(orient="records")


def refresh_data() -> dict[str, object]:
    with REFRESH_LOCK:
        us_rows = run_group(US_TICKERS, "2020-01-01", "ma20_ma60_macd_strategy_comparison.csv")
        korea_rows = run_group(KOREA_TICKERS, "2024-01-01", "korea_ma20_ma60_macd_strategy_comparison.csv")
        ai_infra_rows = run_group(
            AI_INFRA_TICKERS,
            "2023-01-01",
            "ai_infrastructure_ma20_ma60_macd_strategy_comparison.csv",
        )
        growth_etf_rows = run_group(
            GROWTH_ETF_TICKERS,
            "2023-01-01",
            "growth_etf_ma20_ma60_macd_strategy_comparison.csv",
        )
        us_improved_rows = run_improved_group(US_TICKERS, "2020-01-01", "improved_strategy_comparison.csv")
        korea_improved_rows = run_improved_group(
            KOREA_TICKERS,
            "2024-01-01",
            "korea_improved_strategy_comparison.csv",
        )
        latest = {
            "ok": True,
            "groups": {
                "us": us_rows,
                "korea": korea_rows,
                "ai_infra": ai_infra_rows,
                "growth_etf": growth_etf_rows,
                "us_improved": us_improved_rows,
                "korea_improved": korea_improved_rows,
            },
            "tickers": US_TICKERS + KOREA_TICKERS + AI_INFRA_TICKERS + GROWTH_ETF_TICKERS,
            "refreshed_at": pd.Timestamp.now(tz="Europe/London").isoformat(),
        }
        LAST_REFRESH.clear()
        LAST_REFRESH.update(latest)
        return latest


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            self.send_json(LAST_REFRESH or {"ok": True, "refreshed_at": None})
            return
        if parsed.path == "/api/refresh":
            try:
                self.send_json(refresh_data())
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
            return
        super().do_GET()

    def send_json(self, payload: dict[str, object], status: int = 200) -> None:
        data = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the strategy dashboard with yfinance refresh API.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"Dashboard server running at http://{args.host}:{args.port}/")
    print("Refresh endpoint: /api/refresh")
    server.serve_forever()


if __name__ == "__main__":
    main()
