# Macro-Regime-and-Allocation-Strategy-HMM

# Table of Contents
- [Executive Summary](#executive-summary)
- [Introduction](#introduction)
- [Data & Assets](#data--assets)
- [Methodology](#methodology)
- [Performance Evaluation](#performance-evaluation)
- [Discussion & Insights](#discussion--insights)
- [Limitations](#limitations)
- [Conclusion](#conclusion)


# Executive Summary

This project explores how incorporating macroeconomic regime detection into portfolio construction can enhance investment performance and reduce downside risk compared to passive strategies. Using a Hidden Markov Model (HMM) trained on the evolving relationship between equities (SPY), long-term bonds (TLT), and gold (GC=F), I classified the market into three regimes: Divergent Macro (Risk-On), Flight to Safety (Risk-Off), and Transition Zone.

I then applied Modern Portfolio Theory (MPT) within each regime to dynamically adjust asset weights based on regime-specific return and risk characteristics. The final model also incorporated the derivative of a decomposed correlation trend to improve regime detection responsiveness.

Backtests from 2003 to 2024—including during the 2008 Financial Crisis and COVID-19 crash—showed that this adaptive strategy significantly outperformed a SPY Buy & Hold approach, delivering:
- Higher Sharpe Ratios:
	- **Portfolio Sharpe Ratio:** 0.79
 	- **SPY Sharpe Ratio:** 0.53
- Lower drawdowns:
	- **Portfolio Max Drawdown:** -25.60%
 	- **SPY Max Drawdown:** -54.77%
- Higher weekly returns during crises:

|                       | Portfolio Return | SPY Return |
|-----------------------|------------------|------------|
| 2008 Financial Crisis | 0.19%            | -0.04%     |
| 2020 COVID-19 Pandemic| 0.37%            | 0.31%      |

These results demonstrate that macro-aware, regime-sensitive allocation frameworks—grounded in financial theory and enhanced by machine learning—can meaningfully improve risk-adjusted returns in real-world portfolios.

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

To detect shifts in market conditions, we employed a Hidden Markov Model (HMM)—a statistical framework that assumes financial markets move through a sequence of hidden states or “regimes” (e.g., bull or bear markets), which can be inferred from observable data like returns and volatility. An HMM is well-suited for this task because it models the market as a probabilistic process, where each hidden state generates returns with its own statistical characteristics, and it captures time-dependent dynamics, learning how likely the market is to transition from one regime to another over time/

### Model Configuration:
  
The Hidden Markov Model was trained to identify three distinct macroeconomic regimes based on the relationship between equities, bonds and gold:

- **Divergent Macro (Risk-On):**
	- A regime where correlations break down—typically characterized by equities diverging from traditional safe havens. This reflects risk appetite, growth narratives, and investor confidence.

- **Flight to Safety (Risk-Off):**
	- A regime where equities begin moving in sync with bonds or gold, signaling market stress and a shift toward capital preservation. Correlation patterns tighten as investors flee riskier assets.

- **Transition Zone:**
	- A regime in between Risk-On and Risk-Off. Often marked by unstable or shifting correlations, this phase represents uncertainty or the beginning of a macro inflection point.

## Features Used for Modeling:

- A rolling correlation of equity prices (SPY) with gold (GC=F) and long-term treasuries (TLT)
- The trend component from a seasonal decomposition of this rolling correlation
- The first derivative of that trend, capturing momentum in macro relationships rather than price alone

This feature engineering allows the HMM to focus not on raw price or volatility, but on shifts in inter-asset relationships, which are often early signals of changing macro regimes.

## Regime-Based Portfolio Allocation

Once the Hidden Markov Model classified the current market regime as Divergent Macro (Risk-On), Transition Zone, or Flight to Safety (Risk-Off), the portfolio dynamically adjusted its allocations using the principles of Modern Portfolio Theory (MPT).

### Modern Portfolio Theory (MPT)

For each detected regime, I applied mean-variance optimization to compute the optimal weights for the portfolio’s three assets: SPY, TLT, and gold (GC=F). This approach balances expected returns against covariances, seeking the highest Sharpe ratio for a given regime-specific risk profile.

### Regime-Based Rebalancing

The portfolio rebalanced only when a new regime was detected by the HMM. This event-driven allocation minimizes transaction costs while still responding to meaningful shifts in macroeconomic conditions.

- **Risk-On (Divergent Macro):** Allocation favored SPY, with reduced exposure to TLT and gold.
- **Risk-Off (Flight to Safety):** Allocation tilted heavily toward TLT and gold, reducing equity exposure.
- **Transition Zone:** Weights were more evenly balanced, favoring diversification across all three assets.

### Handling Regime Transitions

To prevent excessive turnover or reacting to short-term noise, a buffer period was used before committing to a full reallocation:

- Regime changes were only acted upon when the HMM assigned consistently high probability (e.g., >80%) to the new state for at least a few consecutive periods.
- This added stability ensured the model responded to structural shifts rather than whipsaws in short-term correlations.

This regime-sensitive allocation strategy enabled the portfolio to lean into favorable conditions and de-risk during periods of instability, enhancing long-term risk-adjusted returns.

## Returns of Assets in Regimes:

|                            | TLT Weekly Return | GC=F Weekly Return | SPY Weekly Return |
| -------------------------- | ----------------- | ------------------ | ----------------- |
| Divergent Macro (Risk-On)  | 0.11%             | 0.22%              | 0.23%             |
| Flight to Safety (Risk-Off)| 0.05%             | 0.19%              | 0.13%             |
| Transition Zone            | 0.69%             | -0.36%             | 1.74%             |

![Screenshot 2025-03-28 at 2 29 24 PM](https://github.com/user-attachments/assets/9a51dfc2-31e4-414f-92fe-9f131da2592f)

![Screenshot 2025-03-28 at 2 29 46 PM](https://github.com/user-attachments/assets/eb7061b8-e42c-4c7c-8d88-3d8c90b49941)

![Screenshot 2025-03-28 at 2 30 10 PM](https://github.com/user-attachments/assets/7cde2ef8-7ba4-4603-8749-ad843c7faec4)


## Finding Optimal Model

To arrive at the final regime-based strategy, I went through a series of model iterations—each introducing a key enhancement. The process allowed me to assess the value of each feature and refine the strategy using real-world performance metrics.

### Phase 1: Simple Allocation by Regime

In the first version, I applied a basic allocation strategy using fixed weights for each regime. Regimes were identified using the trend component from seasonal decomposition of rolling correlations between SPY and safe-haven assets (TLT and gold).

|                            | Weight for SPY  | Weight for TLT  | Weight for Gold   |
| -------------------------- | --------------- | --------------- | ----------------  |
| Divergent Macro (Risk-On)  |      0.7        | 0.1             | 0.2               |
| Flight to Safety (Risk-Off)| 0.2             | 0.5             | 0.3               |
| Transition Zone            | 0               | 0.5             | 0.5               |

This approach provided basic diversification, but lacked sensitivity to asset dynamics within each regime.

### Phase 2: Added Momentum Signal (Derivative of Trend)

To improve regime transitions and early detection, I incorporated the first derivative of the trend (i.e., the rate of change in correlation trend), allowing the HMM to detect shifts more responsively. This helped identify when a regime was strengthening or breaking down.

While this improved responsiveness, performance still plateaued due to the fixed allocation weights.

### Phase 3: Regime-Specific Modern Portfolio Theory (MPT)

In the final version, I applied mean-variance optimization within each regime. The model computed optimal asset weights based on regime-specific historical returns and covariances, maximizing the Sharpe ratio within each environment.

This version significantly boosted risk-adjusted performance, reduced drawdowns, and better handled macro inflection points.

# Performance Evaluation

## Cumulative Returns
To evaluate not only overall performance but also the portfolio’s resilience under market stress, I conducted focused analyses on two major crisis periods: the 2008 Global Financial Crisis (January 2007 to December 2009) and the COVID-19 pandemic (January 2020 to December 2020).

![Screenshot 2025-03-28 at 12 20 25 PM](https://github.com/user-attachments/assets/00886236-b724-4076-a185-cfb3d01937b9)

The cumulative returns plot above compares four variations of the regime-based strategy against the SPY Buy & Hold benchmark. Each model iteration builds on the last, illustrating the impact of MPT optimization and derivative-based regime detection.

- Green shaded areas represent Risk-On (Divergent Macro) regimes
- Red shaded areas represent Risk-Off (Flight to Safety) regimes
- Orange shaded areas indicate the Transition Zone where macro sentiment is uncertain

**Key Takeaways:**

- The purple line (Final Model: MPT + Derivative) consistently outperforms other strategies, particularly during and after high-volatility events like the 2008 Financial Crisis, COVID Crash in 2020, and the 2022 bear market.
- The red line (MPT without derivative) also performs well, but lags slightly due to delayed regime transitions.
- Strategies without MPT (blue and orange) show more volatility and underperformance in sideways markets and Risk-Off regimes.
- SPY (green line) shows strong growth in Risk-On periods but suffers significant drawdowns in red zones, particularly in 2008 and 2020.

This plot clearly demonstrates the value of combining MPT with timely regime detection. The use of the derivative (rate of change of trend) enabled earlier and more accurate transitions between macro states, allowing the final model to better navigate risk and capitalize on momentum.

### 2008 Financial Crisis Cumulative Returns

![Screenshot 2025-03-28 at 12 47 27 PM](https://github.com/user-attachments/assets/e6ea94a1-fc8d-4506-9a1f-f19ee0b6ab9d)

**Key Takeaways:** 

- The SPY Buy & Hold strategy (green line) experienced a steep drawdown, dropping well below 1.0 in cumulative returns during late 2008.
- In contrast, all regime-aware strategies preserved capital significantly better, especially during prolonged Risk-Off periods.
- The final model (MPT + Derivative, purple line) maintained the strongest cumulative return throughout the crisis and recovered faster.
- Models using MPT allocation (red & purple) outperformed their fixed-weight counterparts, highlighting the benefit of dynamically adjusting risk based on regime conditions.
- The use of the derivative of the correlation trend helped models respond earlier to macro stress, enabling more timely shifts into defensive assets like TLT and gold.

This stress test demonstrates the value of combining macro regime detection with adaptive portfolio construction. While SPY suffered significant losses, the regime-aware models provided both downside protection and faster recovery.

### 2020 COVID-19 Pandemic 

![Screenshot 2025-03-28 at 12 48 58 PM](https://github.com/user-attachments/assets/3e972c18-8612-4930-b7e6-632956b7352b)

 **Key Takeaways:**
 
- The SPY Buy & Hold strategy (green line) experienced a sharp drawdown in March 2020, falling below 3.1 before recovering by year-end.
- Regime-aware strategies demonstrated strong downside protection, with much smaller dips during the Risk-Off transition.
- The final model (MPT + Derivative, purple line) once again led performance, preserving capital during the crash and capturing upside during the recovery.
- Notably, the MPT-based strategies (red & purple) quickly adapted to changing conditions and outperformed fixed-weight models throughout the year.
- The inclusion of the derivative feature allowed earlier identification of the downturn, helping the model shift into safer allocations before the steepest part of the drop.

This case study highlights the strategy’s ability to respond swiftly to fast, high-impact shocks—a crucial feature for risk-managed portfolios in modern markets.

## Sharpe Ratio

### Overall

|             | Portfolio 1 (No MPT, No Deriv) | Portfolio 2 (No MPT, Deriv) | Portfolio 3 (MPT, No Deriv) | Portfolio 4 (MPT, Deriv)     | SPY  |
|-------------|--------------------------------|-----------------------------|-----------------------------|------------------------------|------|
|Sharpe Ratio | 0.66                           | 0.66                        | 0.78                        | **0.79**                     | 0.53 |

- Both MPT-enabled portfolios outperform SPY and fixed-weight strategies.
- Adding the derivative improves responsiveness and results in the highest overall Sharpe.

### 2008 Financial Crisis

|             | Portfolio 1 (No MPT, No Deriv) | Portfolio 2 (No MPT, Deriv) | Portfolio 3 (MPT, No Deriv)     | Portfolio 4 (MPT, Deriv) | SPY   |
|-------------|--------------------------------|-----------------------------|---------------------------------|--------------------------|-------|
|Sharpe Ratio | 0.41                           | 0.34                        | **0.63**                        | 0.58                     | -0.11 |

- All regime-based portfolios achieved positive Sharpe Ratios, in stark contrast to SPY’s negative ratio.
- Portfolio 3 (MPT, No Deriv) had the best Sharpe in this slower-burning crisis, suggesting MPT played a stronger role than the derivative here.

### 2020 COVID-19 Pandemic

|             | Portfolio 1 (No MPT, No Deriv) | Portfolio 2 (No MPT, Deriv) | Portfolio 3 (MPT, No Deriv) | Portfolio 4 (MPT, Deriv)    | SPY  |
|-------------|--------------------------------|-----------------------------|-----------------------------|-----------------------------|------|
|Sharpe Ratio | 0.54                           | 0.65                        | 1.09                        | **1.22**                    | 0.55 |

- During this fast, high-impact crisis, Portfolio 4 (MPT + Deriv) delivered the best risk-adjusted performance, nearly doubling SPY’s Sharpe.
- The derivative helped detect regime shifts earlier, while MPT adjusted weights in real time, offering both agility and precision.

### Conclusion
Across the full time horizon and during major crises like the 2008 financial meltdown and the COVID-19 crash, the final model (MPT + Derivative) delivered superior Sharpe Ratios and reduced drawdowns, highlighting its ability to preserve capital in stressed environments and capitalize on recovery trends. Each model iteration—from fixed weights to derivative-enhanced optimization—contributed to these improvements, reinforcing the value of an iterative, data-driven approach to portfolio construction.

Ultimately, this strategy showcases how machine learning, macro intuition, and classic finance theory can work together to build smarter, more adaptable portfolios in a complex market landscape.

## Drawdown

### Overall
![Screenshot 2025-03-28 at 1 45 16 PM](https://github.com/user-attachments/assets/31d040de-9c1b-4577-98d0-c34509422aed)

- SPY (green line) suffered the largest and deepest drawdowns, especially during 2008 and early 2020.
- All regime-based strategies consistently experienced shallower and shorter drawdowns.
- The final model (MPT + Derivative) displayed the most consistent capital protection, recovering quickly after downturns and avoiding deep underwater periods.

### 2008 Financial Crisis

![Screenshot 2025-03-28 at 1 47 06 PM](https://github.com/user-attachments/assets/469f2021-e24f-4642-9c0e-b1ac2f284790)

- SPY experienced a peak drawdown of over -50%, while regime-based portfolios stayed within the -20% to -30% range.
- MPT-based models (especially Portfolio 3) managed risk better than their fixed-weight counterparts.
- The drawdown reduction is especially significant during the prolonged Risk-Off period from late 2007 to early 2009, where SPY failed to recover for years.

### 2020 COVID-19 Pandemic

![Screenshot 2025-03-28 at 1 48 36 PM](https://github.com/user-attachments/assets/6564bc0e-b33e-457a-92b6-0114c523046c)

- During the sharp and sudden drop in March 2020, SPY fell over 30%, while the final model only drew down around 12%.
- Regime-aware portfolios reacted more quickly and began recovering weeks before SPY.
- The inclusion of the derivative allowed faster recognition of the macro shift, resulting in a faster pivot to defensive allocations and quicker recovery.

### Conlcusion
These drawdown plots visually reinforce the strategy’s ability to reduce losses during market stress, offering strong downside protection without sacrificing long-term growth. While SPY exhibits deeper, longer recoveries, regime-based models maintain smoother equity curves and more consistent risk exposure throughout various macro environments.

# Discussion & Insights

## When the Stratigies Outperformed the S&P

- During crises like 2008 and 2020, the final model (MPT + Derivative) significantly outperformed SPY by rotating into defensive assets (TLT and gold) well before SPY fully priced in the risk.
- In longer Risk-On regimes, it still maintained competitive growth while avoiding unnecessary risk during transitional or overheated markets.
- The combination of regime detection and allocation optimization allowed the strategy to preserve capital while still capturing upside momentum as conditions improved.

## When the Strategy Lagged the SPY

- In strong bull markets with extended Risk-On periods (e.g., 2016–2019), SPY outperformed the regime-based strategies on a pure CAGR basis.
- This is expected, as the regime model prioritizes risk-adjusted returns and not absolute returns at all times.
- Additionally, during choppy Transition Zones, returns were flatter—reflecting the model’s more cautious allocation behavior.

## Risk Management

- By actively shifting into TLT and gold during Risk-Off periods, the model reduced drawdowns by over 50% compared to SPY during the 2008 crisis.
- The derivative feature helped identify early signs of macro inflection points, especially during COVID, enabling faster responses.
- Rebalancing only during regime transitions, rather than at fixed intervals, helped reduce noise and avoid overfitting to market volatility.

## Conclusion

While the SPY Buy & Hold strategy can outperform in uninterrupted bull markets, it comes with severe drawdowns during macro stress. The regime-aware strategy, on the other hand, delivered superior Sharpe Ratios, smoother equity curves, and faster recoveries—especially during periods of economic uncertainty.

This adaptive framework proves that when models are guided by macro relationships and inter-asset signals, they can balance offense and defense far more effectively than static strategies.

# Limitations

## HMM Assumptions

The Hidden Markov Model assumes:
- Stationarity: that the statistical properties of the data (like mean and variance) remain constant within each regime.
- Gaussianity: that returns follow a normal distribution within each hidden state.

## Lookahead Bias Risk

Care was taken to structure the model without peeking into future data (e.g., by using rolling calculations and shifting outputs), but lookahead bias is always a concern in time-series models. If any feature or label unintentionally incorporates future information—such as using non-lagged signals or fitting over the entire dataset—it could inflate backtest results.

In reality, financial markets are often non-stationary and exhibit fat-tailed distributions, especially during times of stress. This means the HMM may sometimes misclassify regime shifts or underestimate risk during tail events.

## No Transaction Costs or Taxes

This analysis assumes frictionless trading:
- No transaction costs
- No bid/ask spreads
- No slippage
- No taxes

In practice, frequent regime-driven reallocations may trigger capital gains, incur fees, and reduce net performance—particularly for retail or tax-sensitive investors. Future versions of the model should incorporate cost-aware optimization to simulate more realistic outcomes.

# Future Improvements

While this regime-based framework already delivers strong results, there are several areas that could enhance both the sophistication and practicality of the strategy:

## More Regimes or Macro-Sensitive Training

- The current model uses three regimes, but expanding to four or five could allow for more nuanced states (e.g., “early recovery” vs. “late expansion”).
- Incorporating macroeconomic indicators (e.g., yield curve slopes, PMI, inflation surprises) as additional HMM inputs could improve regime identification and align the model more closely with real-world cycles.

## Advanced Regime Detection Models

- Consider using Bayesian Hidden Markov Models, which offer uncertainty quantification and smoother transitions between states.
- Alternatively, LSTM neural networks or hybrid models could detect non-linear, sequential macro patterns without relying on Gaussian assumptions.

## Real-Time Automation
- The current pipeline is backtested on historical data. Future work could focus on building a real-time engine that:
- Ingests weekly or daily market data (via APIs like yfinance, FRED, or Alpaca)
- Computes updated features (rolling correlations, decompositions, etc.)
- Detects regime changes using the trained HMM model
- Automatically rebalances the portfolio and logs trades or alerts
- Tools like Airflow, cron jobs, or serverless functions could be used to schedule updates.
- For deployment, platforms like Streamlit, Dash, or a private Telegram bot could act as interfaces to monitor the model and send live trade recommendations.

These enhancements would move the project from a research framework to a robust, deployable investment system, capable of reacting to macro shifts in near real-time while preserving its theoretical foundation.

# Conclusion

This project demonstrates how combining regime detection with macro-sensitive asset allocation can offer a powerful alternative to traditional passive investing. By leveraging a Hidden Markov Model trained on inter-asset relationships—specifically between equities, bonds, and gold—the strategy dynamically adjusts portfolio weights based on the underlying macroeconomic environment.

Through multiple iterations, including the integration of trend derivatives and Modern Portfolio Theory, the final model achieved a higher Sharpe ratio, shallower drawdowns, and a smoother equity curve than a SPY Buy & Hold approach. Most importantly, the strategy demonstrated resilience during periods of extreme stress, such as the 2008 financial crisis and the COVID-19 crash, while still participating in market rallies during Risk-On regimes.

Ultimately, this work shows that adaptive, data-driven portfolio construction rooted in macro context can outperform static strategies—not just by chasing returns, but by managing risk intelligently across economic cycles.


