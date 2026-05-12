const strategies = {
  macd: {
    labelKey: "strategyMacd",
    descriptionKey: "strategyMacdDescription",
    comparisons: [
      "ma20_ma60_macd_strategy_comparison.csv",
      "korea_ma20_ma60_macd_strategy_comparison.csv",
      "ai_infrastructure_ma20_ma60_macd_strategy_comparison.csv",
      "growth_etf_ma20_ma60_macd_strategy_comparison.csv",
    ],
    equity: [
      { key: "portfolio_equity", labelKey: "portfolio", color: "#5de4e4" },
      { key: "market_equity", labelKey: "buyHold", color: "#58a6ff" },
      { key: "active_equity", labelKey: "activeSleeve", color: "#f4b860" },
    ],
    returnKey: "portfolio_return",
    signalKey: "active_position",
    metrics(row) {
    return [
      [tr("portfolioReturn"), pct(row.portfolio_return_pct), diff(row.portfolio_return_pct, row.buy_hold_return_pct)],
      [tr("buyHoldReturn"), pct(row.buy_hold_return_pct), tr("marketBaseline")],
      [tr("activeSleeveReturn"), pct(row.active_sleeve_return_pct), tr("activeDays", { value: num(row.active_days_pct, 1) })],
      [tr("sharpeRatio"), ratio(row.portfolio_sharpe_ratio), tr("annualizedDaily")],
      ...sentimentMetrics(row),
      [tr("portfolioMaxDrawdown"), pct(row.portfolio_max_drawdown_pct), tr("blendedDrawdown")],
      [tr("buySignals"), int(row.buy_signals), tr("sellSignalsNote", { value: int(row.sell_signals) })],
      [tr("finalSignal"), row.final_active_signal === "1" ? tr("active") : tr("flat"), tr("positionAtEnd")],
        [tr("activeMaxDrawdown"), pct(row.active_sleeve_max_drawdown_pct), tr("activeSleeveRisk")],
        [tr("buyHoldMaxDrawdown"), pct(row.buy_hold_max_drawdown_pct), tr("marketBaselineRisk")],
      ];
    },
  },
  improved: {
    labelKey: "strategyImproved",
    descriptionKey: "strategyImprovedDescription",
    comparisons: ["improved_strategy_comparison.csv", "korea_improved_strategy_comparison.csv"],
    equity: [
      { key: "strategy_equity", labelKey: "strategy", color: "#5de4e4" },
      { key: "market_equity", labelKey: "market", color: "#58a6ff" },
    ],
    returnKey: "strategy_return",
    signalKey: "signal",
    metrics(row) {
      return [
        [tr("strategyReturn"), pct(row.strategy_return_pct), diff(row.strategy_return_pct, row.market_return_pct)],
        [tr("marketReturn"), pct(row.market_return_pct), tr("buyHoldBaseline")],
        [tr("maxDrawdown"), pct(row.max_drawdown_pct), tr("strategyDrawdown")],
        [tr("buySignals"), int(row.buy_signals), tr("sellSignalsNote", { value: int(row.sell_signals) })],
        [tr("rsiExits"), int(row.rsi_exits), tr("momentumRiskExits")],
        [tr("stopLossExits"), int(row.stop_loss_exits), tr("protectiveExits")],
        [tr("smaExits"), int(row.sma_exits), tr("trendExits")],
        [tr("finalSignal"), row.final_signal === "1" ? tr("active") : tr("flat"), tr("positionAtEnd")],
      ];
    },
  },
};

const tickerLabels = {
  en: {
    AAPL: "AAPL",
    NVDA: "NVDA",
    "005930.KS": "Samsung",
    "000660.KS": "SK Hynix",
    "^KS11": "KOSPI",
    VST: "VST",
    CEG: "CEG",
    EQIX: "EQIX",
    AMAT: "AMAT",
    ASML: "ASML",
    LRCX: "LRCX",
    TSLA: "TSLA",
    AMD: "AMD",
    QQQ: "QQQ",
    SPY: "SPY",
  },
  zh: {
    AAPL: "蘋果",
    NVDA: "輝達",
    "005930.KS": "三星電子",
    "000660.KS": "SK 海力士",
    "^KS11": "KOSPI 韓國綜合股價指數",
    VST: "Vistra",
    CEG: "Constellation Energy",
    EQIX: "Equinix",
    AMAT: "應用材料",
    ASML: "艾司摩爾",
    LRCX: "科林研發",
    TSLA: "特斯拉",
    AMD: "超微半導體",
    QQQ: "納斯達克 100 ETF",
    SPY: "標普 500 ETF",
  },
};
const tickerOrder = ["AAPL", "NVDA", "TSLA", "AMD", "QQQ", "SPY", "VST", "CEG", "EQIX", "AMAT", "ASML", "LRCX", "005930.KS", "000660.KS", "^KS11"];

const translations = {
  en: {
    documentTitle: "Quant Strategy Results",
    marketEyebrow: "US and Korean Markets",
    pageTitle: "Strategy Results",
    localDashboard: "Local backtest dashboard",
    refresh: "Refresh",
    refreshTitle: "Refresh prices",
    languageButton: "繁中",
    languageTitle: "Switch to Traditional Chinese",
    strategyLabel: "Strategy",
    tickerLabel: "Ticker",
    loading: "Loading",
    strategyDashboard: "Strategy Dashboard",
    dashboardControls: "Dashboard controls",
    equityCurve: "Equity Curve",
    exposure: "Exposure",
    activeSignal: "Active Signal",
    generatedOutput: "Generated Output",
    signalChart: "Signal Chart",
    signalChartAlt: "Strategy signal chart",
    monthlyReturns: "Monthly Returns",
    monthlyHeatmap: "Heatmap",
    portfolioAllocation: "Portfolio Allocation",
    growthModelAllocation: "£5,000 Growth Model",
    allocationHolding: "Holding",
    allocationWeight: "Weight",
    allocationAmount: "Amount",
    allocationSignal: "Signal",
    allocationRecommendation: "Recommendation",
    openPng: "Open PNG",
    portfolioVsMarket: "Portfolio vs Market",
    strategyVsMarket: "Strategy vs Market",
    dateRange: "{start} to {end}",
    strategyMacd: "20/60 MA + MACD",
    strategyMacdDescription: "Uses 20-day and 60-day moving averages with MACD confirmation.",
    strategyImproved: "50/200 SMA + RSI + Stop Loss",
    strategyImprovedDescription: "Uses 50/200 SMA with an RSI filter and a 10% stop loss.",
    unavailableTicker: "{ticker} is not available for {strategy}.",
    manualRefreshRunning: "Manual refresh running...",
    refreshingLatestPrices: "Refreshing latest prices...",
    updatedNextRefresh: "Updated {time}; next refresh in 5 min",
    refreshUnavailable: "Refresh unavailable: {error}",
    serverRequired: "Local CSV dashboard; auto-refresh requires dashboard_server.py",
    justNow: "just now",
    buys: "Buys",
    sells: "Sells",
    chart: "Chart",
    portfolio: "Portfolio",
    buyHold: "Buy Hold",
    activeSleeve: "Active Sleeve",
    strategy: "Strategy",
    market: "Market",
    portfolioReturn: "Portfolio Return",
    buyHoldReturn: "Buy Hold Return",
    activeSleeveReturn: "Active Sleeve Return",
    portfolioMaxDrawdown: "Portfolio Max Drawdown",
    buySignals: "Buy Signals",
    finalSignal: "Final Signal",
    activeMaxDrawdown: "Active Max Drawdown",
    buyHoldMaxDrawdown: "Buy Hold Max Drawdown",
    strategyReturn: "Strategy Return",
    marketReturn: "Market Return",
    maxDrawdown: "Max Drawdown",
    sharpeRatio: "Sharpe Ratio",
    newsSentiment: "News Sentiment",
    recommendation: "Recommendation",
    sentimentArticles: "{value} latest articles",
    signalPlusSentiment: "Backtest signal + latest news",
    buyRecommendation: "Buy",
    holdRecommendation: "Hold",
    watchRecommendation: "Watch",
    cashSignal: "Cash",
    allocationRoleQQQ: "US tech ETF growth core",
    allocationRoleSPY: "Broad US market risk stabilizer",
    allocationRoleSKHynix: "Korean AI memory growth",
    allocationRoleLRCX: "AI semiconductor equipment",
    allocationRoleAMD: "AI compute growth",
    allocationRoleSamsung: "Korean mega-cap semiconductor exposure",
    allocationRoleAAPL: "US quality tech anchor",
    allocationRoleNVDA: "AI leader capped for drawdown risk",
    allocationRoleAMAT: "Semiconductor equipment diversification",
    allocationRoleKOSPI: "Broad Korean market exposure",
    allocationRoleVST: "AI power watchlist exposure",
    allocationRoleASML: "Strategic lithography exposure",
    allocationRoleEQIX: "Data center exposure with lower drawdown",
    allocationRoleCEG: "Small AI power diversifier",
    sortinoRatio: "Sortino Ratio",
    winRate: "Win Rate",
    annualizedDaily: "Annualized from daily returns",
    downsideRiskAdjusted: "Downside-risk adjusted",
    positiveReturnDays: "Positive return days",
    rsiExits: "RSI Exits",
    stopLossExits: "Stop Loss Exits",
    smaExits: "SMA Exits",
    marketBaseline: "Full-period market baseline",
    buyHoldBaseline: "Buy and hold baseline",
    activeDays: "{value}% active days",
    blendedDrawdown: "Blended portfolio drawdown",
    sellSignalsNote: "{value} sell signals",
    positionAtEnd: "Position at period end",
    activeSleeveRisk: "Active sleeve risk",
    marketBaselineRisk: "Market baseline risk",
    strategyDrawdown: "Strategy drawdown",
    momentumRiskExits: "Momentum risk exits",
    protectiveExits: "Protective exits",
    trendExits: "Trend exits",
    active: "Active",
    flat: "Flat",
    vsBenchmark: "{sign}{value} pts vs benchmark",
    loadErrorTitle: "Unable to load dashboard data",
  },
  zh: {
    documentTitle: "量化策略結果",
    marketEyebrow: "美國與韓國市場",
    pageTitle: "策略結果",
    localDashboard: "本機回測儀表板",
    refresh: "重新整理",
    refreshTitle: "更新價格",
    languageButton: "EN",
    languageTitle: "切換至英文",
    strategyLabel: "策略",
    tickerLabel: "標的",
    loading: "載入中",
    strategyDashboard: "策略儀表板",
    dashboardControls: "儀表板控制項",
    equityCurve: "權益曲線",
    exposure: "曝險",
    activeSignal: "主動訊號",
    generatedOutput: "產生的輸出",
    signalChart: "訊號圖",
    signalChartAlt: "策略訊號圖",
    monthlyReturns: "月報酬",
    monthlyHeatmap: "熱力圖",
    portfolioAllocation: "投資組合配置",
    growthModelAllocation: "£5,000 成長模型",
    allocationHolding: "持倉",
    allocationWeight: "權重",
    allocationAmount: "金額",
    allocationSignal: "訊號",
    allocationRecommendation: "建議",
    openPng: "開啟 PNG",
    portfolioVsMarket: "投資組合 vs 市場",
    strategyVsMarket: "策略 vs 市場",
    dateRange: "{start} 至 {end}",
    strategyMacd: "20/60 均線 + MACD",
    strategyMacdDescription: "使用 20 日與 60 日移動平均線，並以 MACD 確認訊號。",
    strategyImproved: "50/200 SMA + RSI + 停損",
    strategyImprovedDescription: "使用 50/200 簡單移動平均線，搭配 RSI 篩選與 10% 停損。",
    unavailableTicker: "{ticker} 不適用於 {strategy}。",
    manualRefreshRunning: "正在手動更新...",
    refreshingLatestPrices: "正在更新最新價格...",
    updatedNextRefresh: "已於 {time} 更新；下次更新在 5 分鐘後",
    refreshUnavailable: "無法更新：{error}",
    serverRequired: "本機 CSV 儀表板；自動更新需要 dashboard_server.py",
    justNow: "剛剛",
    buys: "買入",
    sells: "賣出",
    chart: "圖表",
    portfolio: "投資組合",
    buyHold: "買入持有",
    activeSleeve: "主動部位",
    strategy: "策略",
    market: "市場",
    portfolioReturn: "投資組合報酬",
    buyHoldReturn: "買入持有報酬",
    activeSleeveReturn: "主動部位報酬",
    portfolioMaxDrawdown: "投資組合最大回撤",
    buySignals: "買入訊號",
    finalSignal: "期末訊號",
    activeMaxDrawdown: "主動部位最大回撤",
    buyHoldMaxDrawdown: "買入持有最大回撤",
    strategyReturn: "策略報酬",
    marketReturn: "市場報酬",
    maxDrawdown: "最大回撤",
    sharpeRatio: "夏普比率",
    newsSentiment: "新聞情緒",
    recommendation: "建議",
    sentimentArticles: "{value} 篇最新文章",
    signalPlusSentiment: "回測訊號 + 最新新聞",
    buyRecommendation: "買入",
    holdRecommendation: "持有",
    watchRecommendation: "觀察",
    cashSignal: "現金",
    allocationRoleQQQ: "美國科技 ETF 成長核心",
    allocationRoleSPY: "廣泛美股市場風險穩定器",
    allocationRoleSKHynix: "韓國 AI 記憶體成長",
    allocationRoleLRCX: "AI 半導體設備",
    allocationRoleAMD: "AI 運算成長",
    allocationRoleSamsung: "韓國大型半導體龍頭配置",
    allocationRoleAAPL: "美國優質科技核心",
    allocationRoleNVDA: "AI 龍頭，因回撤風險控制部位",
    allocationRoleAMAT: "半導體設備分散配置",
    allocationRoleKOSPI: "廣泛韓國市場配置",
    allocationRoleVST: "AI 電力觀察名單配置",
    allocationRoleASML: "關鍵微影設備配置",
    allocationRoleEQIX: "資料中心配置，回撤較低",
    allocationRoleCEG: "小型 AI 電力分散配置",
    sortinoRatio: "索提諾比率",
    winRate: "勝率",
    annualizedDaily: "由日報酬年化",
    downsideRiskAdjusted: "下方風險調整",
    positiveReturnDays: "正報酬交易日",
    rsiExits: "RSI 出場",
    stopLossExits: "停損出場",
    smaExits: "SMA 出場",
    marketBaseline: "全期間市場基準",
    buyHoldBaseline: "買入持有基準",
    activeDays: "{value}% 主動持倉日",
    blendedDrawdown: "混合投資組合回撤",
    sellSignalsNote: "{value} 個賣出訊號",
    positionAtEnd: "期末部位狀態",
    activeSleeveRisk: "主動部位風險",
    marketBaselineRisk: "市場基準風險",
    strategyDrawdown: "策略回撤",
    momentumRiskExits: "動能風險出場",
    protectiveExits: "保護性出場",
    trendExits: "趨勢出場",
    active: "持倉",
    flat: "空倉",
    vsBenchmark: "{sign}{value} 點 vs 基準",
    loadErrorTitle: "無法載入儀表板資料",
  },
};

let state = { strategy: "macd", ticker: "AAPL", lang: "en" };
let summaries = {};
let activeSeries = [];
let allocationRows = [];
let cacheVersion = Date.now();
let refreshState = { type: "local", time: null, error: "" };
const refreshEveryMs = 5 * 60 * 1000;
const hasRefreshApi =
  (location.hostname === "127.0.0.1" || location.hostname === "localhost") && location.port === "8001";

const els = {
  controls: document.querySelector(".controls"),
  marketEyebrow: document.querySelector("#marketEyebrow"),
  pageTitle: document.querySelector("#pageTitle"),
  strategyTabs: document.querySelector("#strategyTabs"),
  strategyDescription: document.querySelector("#strategyDescription"),
  strategyLabel: document.querySelector("#strategyLabel"),
  tickerLabel: document.querySelector("#tickerLabel"),
  tickerTabs: document.querySelector("#tickerTabs"),
  dateRange: document.querySelector("#dateRange"),
  selectionTitle: document.querySelector("#selectionTitle"),
  quickStats: document.querySelector("#quickStats"),
  metricGrid: document.querySelector("#metricGrid"),
  equityTitle: document.querySelector("#equityTitle"),
  equityLegend: document.querySelector("#equityLegend"),
  equityChart: document.querySelector("#equityChart"),
  signalChart: document.querySelector("#signalChart"),
  signalImage: document.querySelector("#signalImage"),
  chartLink: document.querySelector("#chartLink"),
  allocationLabel: document.querySelector("#allocationLabel"),
  allocationTitle: document.querySelector("#allocationTitle"),
  allocationTable: document.querySelector("#allocationTable"),
  allocationHoldingHeader: document.querySelector("#allocationHoldingHeader"),
  allocationWeightHeader: document.querySelector("#allocationWeightHeader"),
  allocationAmountHeader: document.querySelector("#allocationAmountHeader"),
  allocationSignalHeader: document.querySelector("#allocationSignalHeader"),
  allocationRecommendationHeader: document.querySelector("#allocationRecommendationHeader"),
  equityCurveLabel: document.querySelector("#equityCurveLabel"),
  exposureLabel: document.querySelector("#exposureLabel"),
  activeSignalTitle: document.querySelector("#activeSignalTitle"),
  generatedOutputLabel: document.querySelector("#generatedOutputLabel"),
  signalChartTitle: document.querySelector("#signalChartTitle"),
  monthlyReturnsLabel: document.querySelector("#monthlyReturnsLabel"),
  monthlyHeatmapTitle: document.querySelector("#monthlyHeatmapTitle"),
  monthlyHeatmap: document.querySelector("#monthlyHeatmap"),
  refreshStatus: document.querySelector("#refreshStatus"),
  refreshButton: document.querySelector("#refreshButton"),
  languageButton: document.querySelector("#languageButton"),
};

init().catch((error) => {
  document.body.innerHTML = `<main class="error"><h1>${tr("loadErrorTitle")}</h1><p>${error.message}</p></main>`;
});

async function init() {
  els.refreshButton.addEventListener("click", () => refreshLatestPrices({ manual: true }));
  els.languageButton.addEventListener("click", async () => {
    state.lang = state.lang === "en" ? "zh" : "en";
    renderStaticText();
    renderRefreshStatus();
    renderTabs();
    await render();
  });
  renderStaticText();
  renderRefreshStatus();
  if (hasRefreshApi) {
    await refreshLatestPrices({ silent: true });
  } else {
    refreshState = { type: "serverRequired", time: null, error: "" };
    renderRefreshStatus();
  }
  await loadSummaries();
  await loadAllocation();
  renderTabs();
  await render();
  window.addEventListener("resize", () => renderCharts());
  if (hasRefreshApi) {
    window.setInterval(() => refreshLatestPrices(), refreshEveryMs);
  }
}

function renderTabs() {
  const tickers = availableTickers();
  if (!tickers.includes(state.ticker)) {
    state.ticker = tickers[0];
  }

  els.strategyTabs.innerHTML = Object.entries(strategies)
    .map(([key, strategy]) =>
      tabButton(tr(strategy.labelKey), key, key === state.strategy, "strategy", false, tr(strategy.descriptionKey)),
    )
    .join("");
  els.strategyDescription.textContent = tr(strategies[state.strategy].descriptionKey);
  els.tickerTabs.innerHTML = tickerOrder
    .map((ticker) => {
      const enabled = tickers.includes(ticker);
      const title = enabled
        ? ticker
        : tr("unavailableTicker", {
            ticker: tickerLabel(ticker),
            strategy: tr(strategies[state.strategy].labelKey),
          });
      return tabButton(tickerLabel(ticker), ticker, ticker === state.ticker, "ticker", !enabled, title);
    })
    .join("");

  document.querySelectorAll("[data-tab]").forEach((button) => {
    button.addEventListener("click", async () => {
      state[button.dataset.type] = button.dataset.tab;
      renderTabs();
      await render();
    });
  });
}

function tabButton(label, key, active, type, disabled = false, title = "") {
  return `<button class="${active ? "active" : ""}" data-type="${type}" data-tab="${key}" type="button" title="${escapeHtml(
    title,
  )}" ${disabled ? "disabled" : ""}>${escapeHtml(label)}</button>`;
}

async function loadSummaries() {
  cacheVersion = Date.now();
  const entries = await Promise.all(
    Object.entries(strategies).map(async ([key, strategy]) => {
      const groups = await Promise.all(strategy.comparisons.map(async (path) => parseCsv(await fetchText(path))));
      const rows = groups.flat();
      return [key, Object.fromEntries(rows.map((row) => [row.ticker, row]))];
    }),
  );
  summaries = Object.fromEntries(entries);
}

async function loadAllocation() {
  try {
    allocationRows = parseCsv(await fetchText("portfolio_allocation_with_spy.csv"));
  } catch (error) {
    allocationRows = [];
  }
}

async function render() {
  const strategy = strategies[state.strategy];
  const row = summaries[state.strategy][state.ticker];
  activeSeries = parseCsv(await fetchText(row.results_output));

  els.dateRange.textContent = tr("dateRange", { start: row.start, end: row.end });
  els.selectionTitle.textContent = `${tickerLabel(state.ticker)} ${tr(strategy.labelKey)}`;
  els.equityTitle.textContent = state.strategy === "macd" ? tr("portfolioVsMarket") : tr("strategyVsMarket");
  els.chartLink.href = row.chart_output;
  els.signalImage.src = withCacheBust(row.chart_output);

  renderQuickStats(row);
  renderMetrics([...strategy.metrics(row), ...analyticsMetrics(activeSeries, strategy.returnKey)]);
  renderAllocation();
  renderMonthlyHeatmap(activeSeries, strategy.returnKey);
  renderCharts();
}

async function refreshLatestPrices(options = {}) {
  const { manual = false, silent = false } = options;
  if (!hasRefreshApi) {
    refreshState = { type: "serverRequired", time: null, error: "" };
    renderRefreshStatus();
    return;
  }
  if (!silent) setRefreshStatus(manual ? tr("manualRefreshRunning") : tr("refreshingLatestPrices"));
  els.refreshButton.disabled = true;

  try {
    const response = await fetch(withCacheBust("/api/refresh"));
    if (!response.ok) throw new Error(`Refresh failed with HTTP ${response.status}`);
    const payload = await response.json();
    if (!payload.ok) throw new Error(payload.error || "Refresh failed");

    await loadSummaries();
    await loadAllocation();
    renderTabs();
    await render();
    refreshState = { type: "updated", time: payload.refreshed_at, error: "" };
    renderRefreshStatus();
  } catch (error) {
    if (!silent) {
      refreshState = { type: "error", time: null, error: error.message };
      renderRefreshStatus();
    } else {
      refreshState = { type: "serverRequired", time: null, error: "" };
      renderRefreshStatus();
    }
  } finally {
    els.refreshButton.disabled = false;
  }
}

function setRefreshStatus(message) {
  els.refreshStatus.textContent = message;
}

function renderRefreshStatus() {
  if (refreshState.type === "updated") {
    setRefreshStatus(tr("updatedNextRefresh", { time: formatDateTime(refreshState.time) }));
  } else if (refreshState.type === "error") {
    setRefreshStatus(tr("refreshUnavailable", { error: refreshState.error }));
  } else if (refreshState.type === "serverRequired") {
    setRefreshStatus(tr("serverRequired"));
  } else {
    setRefreshStatus(tr("localDashboard"));
  }
}

function renderQuickStats(row) {
  const stats = [
    [tr("buys"), int(row.buy_signals)],
    [tr("sells"), int(row.sell_signals)],
    [tr("chart"), row.chart_output],
  ];
  els.quickStats.innerHTML = stats
    .map(([label, value]) => `<div class="pill"><span class="label">${label}</span><strong>${value}</strong></div>`)
    .join("");
}

function availableTickers() {
  return Object.keys(summaries[state.strategy] ?? {});
}

function renderStaticText() {
  document.documentElement.lang = state.lang === "zh" ? "zh-Hant" : "en";
  document.title = tr("documentTitle");
  els.controls.setAttribute("aria-label", tr("dashboardControls"));
  els.marketEyebrow.textContent = tr("marketEyebrow");
  els.pageTitle.textContent = tr("pageTitle");
  els.strategyLabel.textContent = tr("strategyLabel");
  els.tickerLabel.textContent = tr("tickerLabel");
  els.allocationLabel.textContent = tr("portfolioAllocation");
  els.allocationTitle.textContent = tr("growthModelAllocation");
  els.allocationHoldingHeader.textContent = tr("allocationHolding");
  els.allocationWeightHeader.textContent = tr("allocationWeight");
  els.allocationAmountHeader.textContent = tr("allocationAmount");
  els.allocationSignalHeader.textContent = tr("allocationSignal");
  els.allocationRecommendationHeader.textContent = tr("allocationRecommendation");
  els.equityCurveLabel.textContent = tr("equityCurve");
  els.exposureLabel.textContent = tr("exposure");
  els.activeSignalTitle.textContent = tr("activeSignal");
  els.generatedOutputLabel.textContent = tr("generatedOutput");
  els.signalChartTitle.textContent = tr("signalChart");
  els.signalImage.alt = tr("signalChartAlt");
  els.monthlyReturnsLabel.textContent = tr("monthlyReturns");
  els.monthlyHeatmapTitle.textContent = tr("monthlyHeatmap");
  els.chartLink.textContent = tr("openPng");
  els.refreshButton.textContent = tr("refresh");
  els.refreshButton.title = tr("refreshTitle");
  els.languageButton.textContent = tr("languageButton");
  els.languageButton.title = tr("languageTitle");
  if (!els.selectionTitle.textContent || els.selectionTitle.textContent === "Strategy Dashboard") {
    els.selectionTitle.textContent = tr("strategyDashboard");
  }
  if (els.dateRange.textContent === "Loading") {
    els.dateRange.textContent = tr("loading");
  }
}

function tickerLabel(ticker) {
  return tickerLabels[state.lang][ticker] ?? tickerLabels.en[ticker] ?? ticker;
}

function tr(key, replacements = {}) {
  const dictionary = translations[state.lang] ?? translations.en;
  let value = dictionary[key] ?? translations.en[key] ?? key;
  Object.entries(replacements).forEach(([name, replacement]) => {
    value = value.replaceAll(`{${name}}`, replacement);
  });
  return value;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function analyticsMetrics(rows, returnKey) {
  const returns = rows.map((row) => number(row[returnKey])).filter(Number.isFinite);
  const activeReturns = returns.filter((value) => value !== 0);
  const average = mean(returns);
  const volatility = standardDeviation(returns);
  const downside = standardDeviation(returns.filter((value) => value < 0));
  const sharpe = volatility > 0 ? (average / volatility) * Math.sqrt(252) : NaN;
  const sortino = downside > 0 ? (average / downside) * Math.sqrt(252) : NaN;
  const wins = activeReturns.filter((value) => value > 0).length;
  const winRate = activeReturns.length ? (wins / activeReturns.length) * 100 : NaN;

  return [
    [tr("sharpeRatio"), ratio(sharpe), tr("annualizedDaily")],
    [tr("sortinoRatio"), ratio(sortino), tr("downsideRiskAdjusted")],
    [tr("winRate"), pct(winRate), tr("positiveReturnDays")],
  ];
}

function sentimentMetrics(row) {
  if (!row.sentiment_score) return [];
  return [
    [tr("newsSentiment"), ratio(row.sentiment_score), tr("sentimentArticles", { value: int(row.article_count) })],
    [tr("recommendation"), recommendationLabel(row.recommendation), tr("signalPlusSentiment")],
  ];
}

function renderMonthlyHeatmap(rows, returnKey) {
  const monthly = monthlyReturns(rows, returnKey);
  const years = [...new Set(monthly.map((item) => item.year))].sort();
  const months = Array.from({ length: 12 }, (_, index) => index);

  els.monthlyHeatmap.innerHTML = [
    `<div class="heatmap-corner"></div>`,
    ...months.map((month) => `<div class="heatmap-month">${monthLabel(month)}</div>`),
    ...years.flatMap((year) => [
      `<div class="heatmap-year">${year}</div>`,
      ...months.map((month) => {
        const item = monthly.find((entry) => entry.year === year && entry.month === month);
        if (!item) return `<div class="heatmap-cell empty"></div>`;
        return `<div class="heatmap-cell ${item.value >= 0 ? "gain" : "loss"}" style="--intensity:${heatIntensity(
          item.value,
        )}" title="${year} ${monthLabel(month)}: ${pct(item.value)}">${pct(item.value)}</div>`;
      }),
    ]),
  ].join("");
}

function monthlyReturns(rows, returnKey) {
  const grouped = new Map();
  rows.forEach((row) => {
    const value = number(row[returnKey]);
    const date = new Date(row.Date);
    if (!Number.isFinite(value) || Number.isNaN(date.getTime())) return;
    const key = `${date.getFullYear()}-${date.getMonth()}`;
    if (!grouped.has(key)) {
      grouped.set(key, { year: date.getFullYear(), month: date.getMonth(), compounded: 1 });
    }
    grouped.get(key).compounded *= 1 + value;
  });
  return [...grouped.values()].map((item) => ({
    year: item.year,
    month: item.month,
    value: (item.compounded - 1) * 100,
  }));
}

function heatIntensity(value) {
  return Math.min(1, Math.max(0.18, Math.abs(value) / 12)).toFixed(2);
}

function monthLabel(month) {
  return new Intl.DateTimeFormat(state.lang === "zh" ? "zh-Hant" : undefined, { month: "short" }).format(
    new Date(2024, month, 1),
  );
}

function renderMetrics(metrics) {
  els.metricGrid.innerHTML = metrics
    .map(([label, value, note]) => {
      const cls = String(value).startsWith("-") ? "negative" : String(value).includes("%") ? "positive" : "neutral";
      return `<article class="metric-card"><span class="label">${label}</span><strong class="${cls}">${value}</strong><span>${note}</span></article>`;
    })
    .join("");
}

function renderAllocation() {
  if (!allocationRows.length) {
    els.allocationTable.innerHTML = `<tr><td colspan="5">N/A</td></tr>`;
    return;
  }

  els.allocationTable.innerHTML = allocationRows
    .map((row) => {
      const recommendation = recommendationLabel(row.recommendation || "Watch");
      const signalClass = row.signal === "Long" ? "positive" : "neutral";
      const holding = tickerLabel(row.ticker) || row.holding;
      return `<tr>
        <td><strong>${escapeHtml(holding)}</strong><span>${escapeHtml(allocationRoleLabel(row))}</span></td>
        <td>${escapeHtml(row.weight_pct)}%</td>
        <td>£${escapeHtml(Number(row.allocation_gbp).toLocaleString())}</td>
        <td class="${signalClass}">${escapeHtml(signalLabel(row.signal))}</td>
        <td>${escapeHtml(recommendation)}</td>
      </tr>`;
    })
    .join("");
}

function recommendationLabel(value) {
  if (value === "Buy") return tr("buyRecommendation");
  if (value === "Hold") return tr("holdRecommendation");
  if (value === "Watch") return tr("watchRecommendation");
  return value || "N/A";
}

function signalLabel(value) {
  if (value === "Long") return tr("active");
  if (value === "Cash") return tr("cashSignal");
  return value || "N/A";
}

function allocationRoleLabel(row) {
  const keys = {
    QQQ: "allocationRoleQQQ",
    SPY: "allocationRoleSPY",
    "000660.KS": "allocationRoleSKHynix",
    LRCX: "allocationRoleLRCX",
    AMD: "allocationRoleAMD",
    "005930.KS": "allocationRoleSamsung",
    AAPL: "allocationRoleAAPL",
    NVDA: "allocationRoleNVDA",
    AMAT: "allocationRoleAMAT",
    "^KS11": "allocationRoleKOSPI",
    VST: "allocationRoleVST",
    ASML: "allocationRoleASML",
    EQIX: "allocationRoleEQIX",
    CEG: "allocationRoleCEG",
  };
  const key = keys[row.ticker];
  return key ? tr(key) : row.role;
}

function renderCharts() {
  if (!activeSeries.length) return;
  const strategy = strategies[state.strategy];
  drawLineChart(els.equityChart, activeSeries, strategy.equity);
  drawStepChart(els.signalChart, activeSeries, strategy.signalKey);
  els.equityLegend.innerHTML = strategy.equity
    .map((item) => `<span><i style="background:${item.color}"></i>${tr(item.labelKey)}</span>`)
    .join("");
}

function drawLineChart(canvas, rows, lines) {
  const ctx = setupCanvas(canvas);
  const bounds = chartBounds(canvas);
  const values = lines.flatMap((line) => rows.map((row) => number(row[line.key])).filter(Number.isFinite));
  const min = Math.min(...values);
  const max = Math.max(...values);

  drawGrid(ctx, bounds, min, max, (value) => `${value.toFixed(1)}x`);

  lines.forEach((line) => {
    ctx.beginPath();
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = line.color;
    rows.forEach((row, index) => {
      const value = number(row[line.key]);
      const x = bounds.left + (index / (rows.length - 1)) * bounds.width;
      const y = scale(value, min, max, bounds.bottom, bounds.top);
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  });
}

function drawStepChart(canvas, rows, key) {
  const ctx = setupCanvas(canvas);
  const bounds = chartBounds(canvas);
  drawGrid(ctx, bounds, 0, 1, (value) => value.toFixed(0));

  ctx.beginPath();
  ctx.lineWidth = 2.5;
  ctx.strokeStyle = "#48d597";
  rows.forEach((row, index) => {
    const value = number(row[key]) > 0 ? 1 : 0;
    const x = bounds.left + (index / (rows.length - 1)) * bounds.width;
    const y = scale(value, 0, 1, bounds.bottom, bounds.top);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  ctx.fillStyle = "rgba(72, 213, 151, 0.12)";
  rows.forEach((row, index) => {
    if (number(row[key]) <= 0) return;
    const x = bounds.left + (index / rows.length) * bounds.width;
    ctx.fillRect(x, bounds.top, Math.max(1, bounds.width / rows.length), bounds.height);
  });

  drawDateAxis(ctx, bounds, rows);
}

function setupCanvas(canvas) {
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.max(1, Math.floor(rect.width * ratio));
  canvas.height = Math.max(1, Math.floor(rect.height * ratio));
  const ctx = canvas.getContext("2d");
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.clearRect(0, 0, rect.width, rect.height);
  return ctx;
}

function chartBounds(canvas) {
  const rect = canvas.getBoundingClientRect();
  return {
    left: 54,
    right: rect.width - 18,
    top: 18,
    bottom: rect.height - 34,
    width: rect.width - 72,
    height: rect.height - 52,
  };
}

function drawGrid(ctx, bounds, min, max, formatter) {
  ctx.strokeStyle = "rgba(147, 164, 184, 0.18)";
  ctx.fillStyle = "#93a4b8";
  ctx.font = "12px system-ui";
  ctx.lineWidth = 1;

  for (let i = 0; i <= 4; i += 1) {
    const value = min + ((max - min) * i) / 4;
    const y = scale(value, min, max, bounds.bottom, bounds.top);
    ctx.beginPath();
    ctx.moveTo(bounds.left, y);
    ctx.lineTo(bounds.right, y);
    ctx.stroke();
    ctx.fillText(formatter(value), 8, y + 4);
  }
}

function drawDateAxis(ctx, bounds, rows) {
  if (rows.length < 2) return;

  const tickCount = bounds.width < 380 ? 3 : 5;
  ctx.save();
  ctx.strokeStyle = "rgba(147, 164, 184, 0.28)";
  ctx.fillStyle = "#93a4b8";
  ctx.font = "12px system-ui";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";

  for (let i = 0; i < tickCount; i += 1) {
    const index = Math.round((i / (tickCount - 1)) * (rows.length - 1));
    const row = rows[index];
    const x = bounds.left + (index / (rows.length - 1)) * bounds.width;
    const date = formatAxisDate(row.Date);

    ctx.beginPath();
    ctx.moveTo(x, bounds.bottom);
    ctx.lineTo(x, bounds.bottom + 5);
    ctx.stroke();
    ctx.textAlign = i === 0 ? "left" : i === tickCount - 1 ? "right" : "center";
    ctx.fillText(date, x, bounds.bottom + 9);
  }

  ctx.restore();
}

function formatAxisDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value ?? "";
  return date.toLocaleDateString(state.lang === "zh" ? "zh-Hant" : undefined, {
    month: "short",
    year: "numeric",
  });
}

function scale(value, min, max, outMin, outMax) {
  if (max === min) return (outMin + outMax) / 2;
  return outMin + ((value - min) / (max - min)) * (outMax - outMin);
}

async function fetchText(path) {
  const response = await fetch(withCacheBust(path));
  if (!response.ok) throw new Error(`Could not load ${path}`);
  return response.text();
}

function withCacheBust(path) {
  const separator = path.includes("?") ? "&" : "?";
  return `${path}${separator}v=${cacheVersion}`;
}

function parseCsv(text) {
  const [headerLine, ...lines] = text.trim().split(/\r?\n/);
  const headers = splitCsvLine(headerLine);
  return lines.map((line) => {
    const cells = splitCsvLine(line);
    return Object.fromEntries(headers.map((header, index) => [header, cells[index] ?? ""]));
  });
}

function splitCsvLine(line) {
  const cells = [];
  let current = "";
  let quoted = false;
  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    if (char === '"') quoted = !quoted;
    else if (char === "," && !quoted) {
      cells.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  cells.push(current);
  return cells;
}

function number(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : NaN;
}

function pct(value) {
  return Number.isFinite(Number(value)) ? `${num(value, 1)}%` : "N/A";
}

function num(value, digits = 0) {
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

function ratio(value) {
  return Number.isFinite(value) ? value.toFixed(2) : "N/A";
}

function mean(values) {
  if (!values.length) return NaN;
  return values.reduce((total, value) => total + value, 0) / values.length;
}

function standardDeviation(values) {
  if (values.length < 2) return NaN;
  const average = mean(values);
  const variance = values.reduce((total, value) => total + (value - average) ** 2, 0) / (values.length - 1);
  return Math.sqrt(variance);
}

function int(value) {
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: 0 });
}

function diff(value, benchmark) {
  const delta = Number(value) - Number(benchmark);
  return tr("vsBenchmark", {
    sign: delta >= 0 ? "+" : "",
    value: delta.toFixed(1),
  });
}

function formatDateTime(value) {
  if (!value) return tr("justNow");
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return tr("justNow");
  return date.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}
