"""
Fetch latest NewsAPI headlines, score simple news sentiment, and merge the
sentiment with MA20/MA60 + MACD backtest signals.

Set the API key in the environment instead of hardcoding it:
    $env:NEWSAPI_KEY="..."
    python news_sentiment.py
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
NEWSAPI_URL = "https://newsapi.org/v2/everything"
DEFAULT_TICKERS = ["AAPL", "NVDA", "LRCX", "AMAT", "AMD", "QQQ", "SPY", "005930.KS", "000660.KS"]
COMPARISON_FILES = [
    DATA_DIR / "ma20_ma60_macd_strategy_comparison.csv",
    DATA_DIR / "growth_etf_ma20_ma60_macd_strategy_comparison.csv",
    DATA_DIR / "ai_infrastructure_ma20_ma60_macd_strategy_comparison.csv",
    DATA_DIR / "korea_ma20_ma60_macd_strategy_comparison.csv",
]

QUERY_BY_TICKER = {
    "AAPL": '(Apple OR AAPL) AND (stock OR shares OR earnings OR iPhone OR AI)',
    "NVDA": '(Nvidia OR NVIDIA OR NVDA) AND (stock OR shares OR earnings OR AI OR chips)',
    "LRCX": '("Lam Research" OR LRCX) AND (stock OR chips OR semiconductor OR earnings)',
    "AMAT": '("Applied Materials" OR AMAT) AND (stock OR chips OR semiconductor OR earnings)',
    "AMD": '(AMD OR "Advanced Micro Devices") AND (stock OR shares OR earnings OR AI OR chips)',
    "QQQ": '("Invesco QQQ" OR QQQ OR Nasdaq) AND (ETF OR stocks OR technology)',
    "SPY": '("SPDR S&P 500 ETF" OR SPY OR "S&P 500") AND (ETF OR stocks OR market)',
    "005930.KS": '("Samsung Electronics" OR Samsung) AND (stock OR chips OR semiconductor OR earnings)',
    "000660.KS": '("SK Hynix" OR "SK hynix") AND (stock OR memory OR semiconductor OR earnings)',
}

POSITIVE_WORDS = {
    "accelerate": 1.0,
    "beat": 1.2,
    "beats": 1.2,
    "boom": 1.0,
    "bullish": 1.4,
    "buy": 1.0,
    "upgrade": 1.4,
    "upgraded": 1.4,
    "growth": 0.9,
    "gain": 0.8,
    "gains": 0.8,
    "higher": 0.7,
    "outperform": 1.3,
    "profit": 0.8,
    "profits": 0.8,
    "rally": 1.0,
    "record": 0.7,
    "strong": 0.8,
    "surge": 1.2,
    "surges": 1.2,
    "tops": 0.9,
    "win": 0.7,
    "wins": 0.7,
}

NEGATIVE_WORDS = {
    "bearish": -1.4,
    "cut": -0.9,
    "cuts": -0.9,
    "decline": -0.9,
    "declines": -0.9,
    "downgrade": -1.4,
    "downgraded": -1.4,
    "drop": -1.0,
    "drops": -1.0,
    "fall": -0.9,
    "falls": -0.9,
    "fear": -0.8,
    "loss": -1.0,
    "losses": -1.0,
    "miss": -1.2,
    "misses": -1.2,
    "pressure": -0.7,
    "risk": -0.7,
    "risks": -0.7,
    "sell": -1.0,
    "slump": -1.2,
    "weak": -0.8,
    "warning": -1.1,
}


@dataclass
class SentimentResult:
    ticker: str
    query: str
    sentiment_score: float
    sentiment_label: str
    article_count: int
    positive_articles: int
    negative_articles: int
    neutral_articles: int
    top_headline: str
    top_url: str


def article_score(text: str) -> float:
    words = [
        word.strip(".,:;!?()[]{}\"'").lower()
        for word in text.split()
    ]
    raw = 0.0
    matches = 0
    for word in words:
        if word in POSITIVE_WORDS:
            raw += POSITIVE_WORDS[word]
            matches += 1
        elif word in NEGATIVE_WORDS:
            raw += NEGATIVE_WORDS[word]
            matches += 1

    if matches == 0:
        return 0.0
    return math.tanh(raw / max(2, matches))


def sentiment_label(score: float) -> str:
    if score >= 0.15:
        return "Positive"
    if score <= -0.15:
        return "Negative"
    return "Neutral"


def recommendation(signal: str, sentiment_score: float) -> str:
    if signal == "Long" and sentiment_score >= 0.15:
        return "Buy"
    if signal == "Long" and sentiment_score >= -0.15:
        return "Hold"
    if signal == "Long":
        return "Reduce"
    if sentiment_score >= 0.25:
        return "Watchlist"
    if sentiment_score <= -0.15:
        return "Sell/Avoid"
    return "Hold Cash"


def fetch_articles(api_key: str, query: str, page_size: int) -> list[dict[str, object]]:
    params = urlencode(
        {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": api_key,
        }
    )
    request = Request(f"{NEWSAPI_URL}?{params}", headers={"User-Agent": "quant-news-sentiment/1.0"})
    with urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if payload.get("status") != "ok":
        raise RuntimeError(payload.get("message", "NewsAPI request failed"))

    return list(payload.get("articles", []))


def score_ticker(api_key: str, ticker: str, page_size: int) -> SentimentResult:
    query = QUERY_BY_TICKER[ticker]
    articles = fetch_articles(api_key, query, page_size)
    scores = []
    top_headline = ""
    top_url = ""

    for article in articles:
        title = str(article.get("title") or "")
        description = str(article.get("description") or "")
        score = article_score(f"{title} {description}")
        scores.append(score)
        if not top_headline and title and "[Removed]" not in title:
            top_headline = title
            top_url = str(article.get("url") or "")

    average = sum(scores) / len(scores) if scores else 0.0
    return SentimentResult(
        ticker=ticker,
        query=query,
        sentiment_score=average,
        sentiment_label=sentiment_label(average),
        article_count=len(scores),
        positive_articles=sum(1 for score in scores if score >= 0.15),
        negative_articles=sum(1 for score in scores if score <= -0.15),
        neutral_articles=sum(1 for score in scores if -0.15 < score < 0.15),
        top_headline=top_headline,
        top_url=top_url,
    )


def load_backtest_rows() -> pd.DataFrame:
    frames = []
    for path in COMPARISON_FILES:
        if path.exists():
            frames.append(pd.read_csv(path))
    if not frames:
        raise FileNotFoundError("No MA20/MA60 + MACD comparison CSV files found.")

    rows = pd.concat(frames, ignore_index=True)
    rows = rows.drop_duplicates(subset=["ticker"], keep="last")
    rows["portfolio_sharpe_ratio"] = rows.apply(backfill_sharpe, axis=1)
    rows["current_signal"] = rows["final_active_signal"].map({1: "Long", 0: "Cash", "1": "Long", "0": "Cash"})
    return rows


def backfill_sharpe(row: pd.Series) -> float:
    existing = pd.to_numeric(row.get("portfolio_sharpe_ratio"), errors="coerce")
    if pd.notna(existing):
        return float(existing)

    results_output = row.get("results_output")
    if not results_output:
        return float("nan")

    results_path = ROOT / str(results_output).lstrip("./")
    if not results_path.exists():
        return float("nan")

    results = pd.read_csv(results_path)
    returns = pd.to_numeric(results.get("portfolio_return"), errors="coerce").dropna()
    volatility = returns.std()
    if returns.empty or volatility == 0:
        return float("nan")
    return float((returns.mean() / volatility) * math.sqrt(252))


def merge_sentiment_into_comparisons(sentiment: pd.DataFrame) -> None:
    columns = [
        "ticker",
        "portfolio_sharpe_ratio",
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
    slim = sentiment[columns]

    for path in COMPARISON_FILES:
        if not path.exists():
            continue
        comparison = pd.read_csv(path)
        existing_sentiment_columns = [
            column for column in columns if column != "ticker" and column in comparison.columns
        ]
        if existing_sentiment_columns:
            comparison = comparison.merge(slim, on="ticker", how="left", suffixes=("", "_latest"))
            for column in existing_sentiment_columns:
                latest = f"{column}_latest"
                if latest in comparison.columns:
                    comparison[column] = comparison[latest].combine_first(comparison[column])
                    comparison = comparison.drop(columns=[latest])

            new_columns = [
                column for column in columns if column != "ticker" and column not in existing_sentiment_columns
            ]
            for column in new_columns:
                latest = f"{column}_latest"
                if latest in comparison.columns:
                    comparison[column] = comparison[latest]
                    comparison = comparison.drop(columns=[latest])
        else:
            comparison = comparison.merge(slim, on="ticker", how="left")
        comparison.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch latest NewsAPI sentiment and combine it with backtest signals.")
    parser.add_argument("--api-key", default=os.getenv("NEWSAPI_KEY"), help="NewsAPI key. Prefer NEWSAPI_KEY env var.")
    parser.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS, help="Tickers to score.")
    parser.add_argument("--page-size", type=int, default=20, help="NewsAPI articles per ticker.")
    parser.add_argument("--output", default="news_sentiment_scores.csv", help="Standalone sentiment CSV output.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Seconds to pause between API calls.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.api_key:
        raise SystemExit("Missing NewsAPI key. Set NEWSAPI_KEY or pass --api-key.")

    backtests = load_backtest_rows()
    results = []
    updated_at = pd.Timestamp.now(tz="Europe/London").isoformat()

    for ticker in args.tickers:
        ticker = ticker.upper()
        if ticker not in QUERY_BY_TICKER:
            raise ValueError(f"No NewsAPI query configured for {ticker}.")

        scored = score_ticker(args.api_key, ticker, args.page_size)
        row = backtests.loc[backtests["ticker"] == ticker]
        current_signal = row["current_signal"].iloc[0] if not row.empty else "Unknown"
        portfolio_sharpe = row["portfolio_sharpe_ratio"].iloc[0] if not row.empty else ""
        portfolio_drawdown = row["portfolio_max_drawdown_pct"].iloc[0] if not row.empty else ""

        results.append(
            {
                "ticker": ticker,
                "current_signal": current_signal,
                "portfolio_sharpe_ratio": portfolio_sharpe,
                "portfolio_max_drawdown_pct": portfolio_drawdown,
                "sentiment_score": scored.sentiment_score,
                "sentiment_label": scored.sentiment_label,
                "article_count": scored.article_count,
                "positive_articles": scored.positive_articles,
                "negative_articles": scored.negative_articles,
                "neutral_articles": scored.neutral_articles,
                "recommendation": recommendation(current_signal, scored.sentiment_score),
                "top_headline": scored.top_headline,
                "top_url": scored.top_url,
                "query": scored.query,
                "sentiment_updated_at": updated_at,
            }
        )
        time.sleep(args.sleep)

    sentiment = pd.DataFrame(results)
    DATA_DIR.mkdir(exist_ok=True)
    sentiment.to_csv(DATA_DIR / Path(args.output).name, index=False)
    merge_sentiment_into_comparisons(sentiment)

    display = sentiment[
        [
            "ticker",
            "current_signal",
            "sentiment_score",
            "sentiment_label",
            "article_count",
            "recommendation",
            "portfolio_sharpe_ratio",
            "portfolio_max_drawdown_pct",
        ]
    ].copy()
    display["sentiment_score"] = display["sentiment_score"].map("{:.2f}".format)
    print(display.to_string(index=False))
    print(f"Saved sentiment to {args.output}")
    print("Updated MA20/MA60 + MACD comparison CSVs for the dashboard.")


if __name__ == "__main__":
    main()
