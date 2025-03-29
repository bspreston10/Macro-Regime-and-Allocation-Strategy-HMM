import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from auto_hmm import MacroRegimeAllocater

st.set_page_config(layout="wide")
st.title("Macro Regime Portfolio Dashboard")

@st.cache_data
def run_model():
    allocator = MacroRegimeAllocater(start_date='2003-01-01', end_date='2024-04-10')
    allocator.fetch_data()
    allocator.calculate_features()
    allocator.train_hmm()
    allocator.apply_allocations()

    # Add regime label to returns DataFrame
    returns = allocator.returns.copy()
    returns['Regime'] = allocator.regimes
    returns['regime_label'] = returns['Regime'].map(allocator.regime_labels)

    return returns

returns = run_model()

st.markdown("""
Welcome to the **Macro Regime Portfolio Dashboard**

This tool uses a **Hidden Markov Model (HMM)** to detect shifting macroeconomic regimes based on relationships between equities, bonds, and gold. Instead of relying on a static portfolio like Buy & Hold (e.g., SPY), this strategy adapts asset allocations depending on the current regime:

- 🟢 **Divergent Macro (Risk-On)**: Favor equities (SPY)
- 🔴 **Flight to Safety (Risk-Off)**: Shift toward bonds (TLT) and gold
- 🟠 **Transition Zone**: Allocate defensively across all assets

Use the **date slider in the sidebar** to explore different time periods and observe how performance metrics (Sharpe Ratio, CAGR, Drawdown) evolve over time. Background colors in the return chart indicate which macro regime was active.""")

# --- Sidebar Date Slider ---
st.sidebar.header("📅 Date Range")
date_range = st.sidebar.slider(
    "Select Time Range",
    min_value=pd.to_datetime(returns.index.min()).date(),
    max_value=pd.to_datetime(returns.index.max()).date(),
    value=(pd.to_datetime(returns.index.min()).date(), pd.to_datetime(returns.index.max()).date()),
    format="YYYY-MM-DD"
)

start, end = date_range
filtered = returns.loc[(returns.index >= pd.to_datetime(start)) & (returns.index <= pd.to_datetime(end))]


def calc_metrics(returns_series, rf=0.0):
    sharpe = np.sqrt(52) * ((returns_series.mean() - rf / 52) / returns_series.std())
    cagr = (1 + returns_series).prod()**(52 / len(returns_series)) - 1
    max_dd = (1 + returns_series).cumprod().div((1 + returns_series).cumprod().cummax()).min() - 1
    return sharpe, cagr, max_dd

# Portfolio KPIs
sharpe_p, cagr_p, dd_p = calc_metrics(filtered['Portfolio_Return'])

# SPY KPIs
sharpe_spy, cagr_spy, dd_spy = calc_metrics(filtered['return_spy'])

# Row 1: Sharpe + CAGR
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Sharpe Ratio **(Portfolio)**", f"{sharpe_p:.2f}")
kpi2.metric("Max Drawdown **(Portfolio)**", f"{dd_p:.2%}")
kpi3.metric("CAGR **(Portfolio)**", f"{cagr_p:.2%}")

# Row 2: CAGR + Drawdowns
kpi4, kpi5, kpi6 = st.columns(3)
kpi4.metric("Sharpe Ratio **(SPY)**", f"{sharpe_spy:.2f}")
kpi6.metric("CAGR **(SPY)**", f"{cagr_spy:.2%}")
kpi5.metric("Max Drawdown **(SPY)**", f"{dd_spy:.2%}")

# --- Cumulative Returns Plot ---
st.subheader("Cumulative Returns with Regime Overlays")
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(filtered.index, (1 + filtered['Portfolio_Return']).cumprod(), label='Portfolio', color='black')
ax.plot(filtered.index, (1 + filtered['return_spy']).cumprod(), label='SPY', color='green')

# Regime overlays
regime_colors = {
    'Divergent Macro (Risk-On)': '#2ECC71',
    'Transition Zone': '#F39C12',
    'Flight to Safety (Risk-Off)': '#E74C3C'
}
prev_label = None
start_date = None

for date, row in filtered.iterrows():
    curr_label = row['regime_label']
    if curr_label != prev_label:
        if prev_label is not None:
            ax.axvspan(start_date, date, color=regime_colors.get(prev_label, 'gray'), alpha=0.2)
        start_date = date
        prev_label = curr_label
# Final span
ax.axvspan(start_date, filtered.index[-1], color=regime_colors.get(prev_label, 'gray'), alpha=0.2)

ax.set_title("Portfolio vs SPY Cumulative Returns")
ax.set_xlabel("Date")
ax.set_ylabel("Cumulative Returns (%)")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# --- Drawdown Plot ---
st.subheader("Drawdown Over Time for Portfolio and SPY")
fig2, ax2 = plt.subplots(figsize=(12, 4))
cumulative = (1 + filtered['Portfolio_Return']).cumprod()
cumulative_spy = (1 + filtered['return_spy']).cumprod()
drawdown_series = cumulative / cumulative.cummax() - 1
drawdown_series_spy = cumulative_spy / cumulative_spy.cummax() - 1
ax2.plot(filtered.index, drawdown_series, label='Portfolio Drawdown', color='black')
ax2.plot(filtered.index, drawdown_series_spy, label='SPY Drawdown', color='green')

# Regime overlays
prev_label = None
start_date = None

for date, row in filtered.iterrows():
    curr_label = row['regime_label']
    if curr_label != prev_label:
        if prev_label is not None:
            ax.axvspan(start_date, date, color=regime_colors.get(prev_label, 'gray'), alpha=0.2)
        start_date = date
        prev_label = curr_label
# Final span
ax.axvspan(start_date, filtered.index[-1], color=regime_colors.get(prev_label, 'gray'), alpha=0.2)

ax2.set_title("Portfolio vs SPY Drawdown")
ax2.set_xlabel("Date")
ax2.set_ylabel("Drawdown (%)")
ax2.grid(True)
st.pyplot(fig2)