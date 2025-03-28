# Macro-Regime-and-Allocation-Strategy-HMM

# TOC

1. Executive Summary
- One-paragraph overview: what you did, why, and what the results were.
- Mention the use of HMM, macro regimes, and how your strategy compares to SPY.

# Introduction

In traditional investing, many portfolios rely on a static allocation strategy, such as buying and holding a broad market index like the S&P 500 (SPY). While this passive approach can deliver strong returns over the long run, it exposes investors to significant drawdowns during adverse market conditions. This project aims to outperform passive investing by dynamically adjusting portfolio allocations in response to changing macroeconomic regimes.

To accomplish this, we apply a Hidden Markov Model (HMM) to identify distinct economic regimes that are not directly observable in the market data but leave underlying statistical patterns. By aligning asset allocation strategies with these regimes, the portfolio can adapt more intelligently to market conditions and better manage risk.

Regime-switching matters in asset allocation because financial markets are not always governed by the same dynamics. For example, strategies that work during a booming economy may fail during a downturn. Incorporating regime awareness allows the portfolio to reduce exposure to risky assets during high-volatility periods and lean into growth opportunities when conditions are favorable. This adaptive approach seeks to improve risk-adjusted returns and deliver smoother performance across economic cycles.

# Data & Assets

To capture a broad range of market conditions, including multiple recessions and recoveries, the dataset spans from October 13, 2003 to April 10, 2024. This long-term horizon ensures the model is exposed to various macroeconomic environments, such as the 2008 financial crisis, the COVID-19 shock, and the post-pandemic recovery.

- **Frequency:** Weekly returns (52 observations per year) were used to smooth out short-term noise while preserving regime dynamics
- **Data Source:** All asset price data was collected using the yfinance Python API

**Asset Universe:**

- **SPY:** S&P 500 ETF, representing U.S. equity exposure
- **TLT:** iShares 20+ Year Treasury Bond ETF, representing long-term government bonds
- **GC=F:** COMEX Gold Futures, providing a hedge against inflation and macro uncertainty

These assets were selected to create a macro-sensitive portfolio, with each asset responding differently across regimes (e.g., equities in growth, bonds in recessions, and gold during inflation or crisis periods). This diversity enables more effective risk balancing based on detected regime conditions.

# Methodology

## Hidden Markov Model (HMM)

To detect shifts in market conditions, we employed a Hidden Markov Model (HMM)—a statistical framework that assumes financial markets move through a sequence of hidden states or “regimes” (e.g., bull or bear markets), which can be inferred from observable data like returns and volatility.

**An HMM is well-suited for this task because:**

- It models the market as a probabilistic process, where each hidden state generates returns with its own statistical characteristics
- It captures time-dependent dynamics, learning how likely the market is to transition from one regime to another over time

**Model Configuration:**
  
The Hidden Markov Model was trained to identify three distinct macroeconomic regimes based on the relationship between equities, bonds and gold:

**Divergent Macro (Risk-On):**
- A regime where correlations break down—typically characterized by equities diverging from traditional safe havens. This reflects risk appetite, growth narratives, and investor confidence.

**Flight to Safety (Risk-Off):**
- A regime where equities begin moving in sync with bonds or gold, signaling market stress and a shift toward capital preservation. Correlation patterns tighten as investors flee riskier assets.

**Transition Zone:**
- A regime in between Risk-On and Risk-Off. Often marked by unstable or shifting correlations, this phase represents uncertainty or the beginning of a macro inflection point.

**Average Returns of Assets in Regimes:**

|                            | TLT Weekly Return | GC=F Weekly Return | SPY Weekly Return |
| -------------------------- | ----------------- | ------------------ | ----------------- |
| Divergent Macro (Risk-On)  | 0.11%             | 0.22%              | 0.23%             |
| Flight to Safety (Risk-Off)| 0.05%             | 0.19%              | 0.13%             |
| Transition Zone            | 0.69%             | -0.36%             | 1.74%             |


**Features Used for Modeling:**

- A rolling correlation of equity prices (SPY) with gold (GC=F) and long-term treasuries (TLT)
- The trend component from a seasonal decomposition of this rolling correlation
- The first derivative of that trend, capturing momentum in macro relationships rather than price alone

This feature engineering allows the HMM to focus not on raw price or volatility, but on shifts in inter-asset relationships, which are often early signals of changing macro regimes.

## Regime-Based Portfolio Allocation

Once the Hidden Markov Model classified the current market regime as Divergent Macro (Risk-On), Transition Zone, or Flight to Safety (Risk-Off), the portfolio dynamically adjusted its allocations using the principles of Modern Portfolio Theory (MPT).

### Modern Portfolio Theory (MPT)

For each detected regime, I applied mean-variance optimization to compute the optimal weights for the portfolio’s three assets: SPY, TLT, and gold (GC=F). This approach balances expected returns against covariances, seeking the highest Sharpe ratio for a given regime-specific risk profile.

- **Inputs:** Historical weekly returns and covariances of assets within each regime
- **Objective:** Maximize the Sharpe ratio by adjusting asset weights to improve risk-adjusted returns

**Regime-Based Rebalancing**

The portfolio rebalanced only when a new regime was detected by the HMM. This event-driven allocation minimizes transaction costs while still responding to meaningful shifts in macroeconomic conditions.

- **Risk-On (Divergent Macro):** Allocation favored SPY, with reduced exposure to TLT and gold.
- **Risk-Off (Flight to Safety):** Allocation tilted heavily toward TLT and gold, reducing equity exposure.
- **Transition Zone:** Weights were more evenly balanced, favoring diversification across all three assets.

**Handling Regime Transitions**

To prevent excessive turnover or reacting to short-term noise, a buffer period was used before committing to a full reallocation:

- Regime changes were only acted upon when the HMM assigned consistently high probability (e.g., >80%) to the new state for at least a few consecutive periods.
- This added stability ensured the model responded to structural shifts rather than whipsaws in short-term correlations.

This regime-sensitive allocation strategy enabled the portfolio to lean into favorable conditions and de-risk during periods of instability, enhancing long-term risk-adjusted returns.

# Performance Evaluation

## Finding Optimal Model
In the beginning I just used I used solely the seasonal decomposition trend and a simple allocation strategy as seen below:

|                            | Weight for SPY  | Weight for TLT  | Weight for Gold   |
| -------------------------- | --------------- | --------------- | ----------------  |
| Divergent Macro (Risk-On)  |      0.7        | 0.1             | 0.2               |
| Flight to Safety (Risk-Off)| 0.2             | 0.5             | 0.3               |
| Transition Zone            | 0               | 0.5             | 0.5               |

5.1 Cumulative Returns Plot
	•	Compare HMM + MPT portfolio vs. SPY (Buy & Hold)
	•	Annotate major financial crises and regime shifts

5.2 Sharpe Ratio
	•	Show annualized Sharpe for both strategies
	•	Explain risk-adjusted performance

5.3 Optional: Other Metrics
	•	Max drawdown
	•	Volatility
	•	CAGR (Compound Annual Growth Rate)

 6. Macro Regime Interpretation
	•	Describe what each regime typically represents (bull, bear, stagflation, etc.)
	•	Add visuals or shaded graphs to show when each regime occurred

7. Discussion & Insights
	•	Highlight when your strategy outperformed
	•	How regime shifts improved risk management or captured upside
	•	When and why the strategy lagged SPY, if applicable

8. Limitations
	•	HMM model assumptions (stationarity, Gaussianity)
	•	Lookahead bias risks
	•	Ignored transaction costs or taxes

9. Future Improvements
	•	Try more regimes or train on macroeconomic indicators
	•	Consider Bayesian HMMs or LSTM regime detection
	•	Introduce options for tail hedging

10. Conclusion
	•	Recap: Regime detection + macro-sensitive assets can enhance returns and reduce risk
	•	Stronger Sharpe ratio and smoother equity curve than passive SPY investing

