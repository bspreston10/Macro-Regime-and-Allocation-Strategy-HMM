import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from pypfopt import EfficientFrontier, expected_returns, risk_models
from pypfopt.risk_models import CovarianceShrinkage
from scipy.optimize import minimize
import matplotlib.dates as mdates
from hmmlearn.hmm import GaussianHMM
from statsmodels.tsa.seasonal import seasonal_decompose
import yfinance as yf

class MacroRegimeAllocater:

    def __init__(self, start_date, end_date, assets=['SPY', 'TLT', 'GC=F'], frequency='1wk'):
        self.start_date = start_date
        self.end_date = end_date
        self.assets = assets
        self.frequency = frequency
        self.data = None
        self.features = None
        self.model = None
        self.regimes = None
        self.regime_weights = {
        'Divergent Macro (Risk-On)': {'SPY': 0.3963, 'Gold': 0.5442, 'TLT': 0.0595},
        'Flight to Safety (Risk-Off)': {'SPY': 0.4354, 'Gold': 0.2916, 'TLT': 0.273},
        'Transition Zone': {'SPY': 0.0668, 'Gold': 0.9332, 'TLT': 0.0}}
        self.regime_labels = None
    
    def fetch_data(self):
        data = {}

        for asset in self.assets:
            df = yf.download(asset, start=self.start_date, end=self.end_date, interval=self.frequency)
            df = df[['Close']]
            df.rename(columns={'Close': asset}, inplace=True)
            df = df.reset_index()
            data[asset] = df
        
        merged = data[self.assets[0]]
        for asset in self.assets[1:]:
            merged = pd.merge(merged, data[asset], on='Date', how='inner')
        
        merged.set_index('Date', inplace=True)
        merged = merged.droplevel(0, axis=1)
        self.data = merged
    
    def calculate_features(self):
        df = self.data.copy()
        rolling_corr = df['TLT'].rolling(window=4).corr(df['GC=F'])
        df['Rolling_Corr'] = rolling_corr
        df['Rolling_Corr'] = df['Rolling_Corr'].fillna(0)

        # Seasonal decomposition
        decomp = seasonal_decompose(df['Rolling_Corr'], model='additive', period=52)
        df['Corr_Trend'] = decomp.trend
        df = df.dropna(subset=['Corr_Trend'])

        # Derivatives
        df['Corr_Trend_Diff'] = df['Corr_Trend'].diff()
        df['Corr_Trend_Diff_Smoothed'] = df['Corr_Trend_Diff'].rolling(window=12).mean()
        df['Corr_Trend_Diff_Smoothed'] = df['Corr_Trend_Diff_Smoothed'].fillna(0)

        self.features = df[['Corr_Trend', 'Corr_Trend_Diff_Smoothed']].dropna()

    def train_hmm(self, n_regimes=3):
        X = self.features[['Corr_Trend', 'Corr_Trend_Diff_Smoothed']].values
        model = GaussianHMM(n_components=n_regimes, covariance_type='full', n_iter=1000, random_state=42)  
        model.fit(X)

        raw_states = model.predict(X)
        regimes = pd.Series(raw_states, index=self.features.index, name='Regime')

        # Smooth Regime
        regimes_smoothed = regimes.rolling(window=4, center=True).apply(lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[-1])
        regimes_smoothed = regimes_smoothed.ffill().bfill()  # fill edges

        self.model = model
        self.regimes = regimes_smoothed.astype(int)

        # Dynamically assign regime labels based on mean Corr_Trend
        temp = pd.DataFrame({'state': self.regimes, 'Corr_Trend': self.features['Corr_Trend']})
        means = temp.groupby('state').mean().sort_values(by='Corr_Trend')

        # Lowest correlation → likely Risk-Off (Flight to Safety)
        # Middle → Transition
        # Highest → Risk-On
        ordered_labels = ['Flight to Safety (Risk-Off)', 'Transition Zone', 'Divergent Macro (Risk-On)']
        self.regime_labels = {state: label for state, label in zip(means.index, ordered_labels)}

    def asset_allocv2(self, row, mean_deriv, std_deriv):
        base_alloc = self.regime_weights.get(row['regime_label'], {'SPY': 0.33, 'Gold': 0.33, 'TLT': 0.33})
        alloc = base_alloc.copy()

        deriv = row.get('Corr_Trend_derivative_smooth', 0)
        z = (deriv - mean_deriv) / std_deriv
        shift_strength = min(max(z / 2, -1), 1)

        alloc['SPY'] += 0.1 * shift_strength
        alloc['Gold'] -= 0.05 * shift_strength
        alloc['TLT'] -= 0.05 * shift_strength

        total = sum(alloc.values())
        for k in alloc:
            alloc[k] = max(0, alloc[k]) / total

        return (
            row['return_tlt'] * alloc['TLT'] +
            row['return_spy'] * alloc['SPY'] +
            row['return_gold'] * alloc['Gold']
        )

    def apply_allocations(self):
        # Merge features and regimes with price data
        df = self.data.copy()
        df = df.merge(self.features, left_index=True, right_index=True)
        df['Regime'] = self.regimes
        df['regime_label'] = df['Regime'].map(self.regime_labels)

        # Calculate weekly returns
        df['return_spy'] = df['SPY'].pct_change()
        df['return_tlt'] = df['TLT'].pct_change()
        df['return_gold'] = df['GC=F'].pct_change()

        # Compute z-score parameters (once!)
        mean_deriv = df['Corr_Trend_Diff_Smoothed'].mean()
        std_deriv = df['Corr_Trend_Diff_Smoothed'].std()

        df['Portfolio_Return'] = df.apply(
            lambda row: self.asset_allocv2(row, mean_deriv, std_deriv), axis=1
        )

        self.returns = df[['Portfolio_Return', 'return_spy']].dropna()

    def calculate_performance_metrics(self, risk_free_rate=0.01):
        df = self.returns.copy()
        df = df.dropna()

        # Sharpe Ratio
        excess_portfolio = df['Portfolio_Return'] - risk_free_rate / 52
        excess_spy = df['return_spy'] - risk_free_rate / 52

        sharpe_portfolio = np.sqrt(52) * (excess_portfolio.mean() / excess_portfolio.std())
        sharpe_spy = np.sqrt(52) * (excess_spy.mean() / excess_spy.std())

        # Cumulative returns
        cumulative_portfolio = (1 + df['Portfolio_Return']).cumprod()
        cumulative_spy = (1 + df['return_spy']).cumprod()

        # CAGR
        total_weeks = len(df)
        years = total_weeks / 52
        cagr_portfolio = cumulative_portfolio.iloc[-1]**(1/years) - 1
        cagr_spy = cumulative_spy.iloc[-1]**(1/years) - 1

        # Max Drawdown
        rolling_max_portfolio = cumulative_portfolio.cummax()
        drawdown_portfolio = (cumulative_portfolio - rolling_max_portfolio) / rolling_max_portfolio
        max_drawdown_portfolio = drawdown_portfolio.min()

        rolling_max_spy = cumulative_spy.cummax()
        drawdown_spy = (cumulative_spy - rolling_max_spy) / rolling_max_spy
        max_drawdown_spy = drawdown_spy.min()

        print("Performance Summary:")
        print(f"Sharpe Ratio (Portfolio): {sharpe_portfolio:.2f}")
        print(f"Sharpe Ratio (SPY): {sharpe_spy:.2f}")
        print(f"CAGR (Portfolio): {cagr_portfolio:.2%}")
        print(f"CAGR (SPY): {cagr_spy:.2%}")
        print(f"Max Drawdown (Portfolio): {max_drawdown_portfolio:.2%}")
        print(f"Max Drawdown (SPY): {max_drawdown_spy:.2%}")

        self.performance = {
            'Sharpe_Portfolio': sharpe_portfolio,
            'Sharpe_SPY': sharpe_spy,
            'CAGR_Portfolio': cagr_portfolio,
            'CAGR_SPY': cagr_spy,
            'Max_Drawdown_Portfolio': max_drawdown_portfolio,
            'Max_Drawdown_SPY': max_drawdown_spy
        }
    def plot_return(self):
        regime_colors = {
        'Divergent Macro (Risk-On)': '#2ECC71',
        'Transition Zone': '#F39C12',           
        'Flight to Safety (Risk-Off)': '#E74C3C' 
}

        df = self.returns.copy()
        df['Cumulative_Portfolio'] = (1 + df['Portfolio_Return']).cumprod()
        df['Cumulative_SPY'] = (1 + df['return_spy']).cumprod()

        # Merge with regime labels
        df['Regime'] = self.regimes
        df['regime_label'] = df['Regime'].map(self.regime_labels)

        fig, ax = plt.subplots(figsize=(14, 6))

        # Plot cumulative returns
        ax.plot(df.index, df['Cumulative_Portfolio'], label='Portfolio', color='black', linewidth=1.5)
        ax.plot(df.index, df['Cumulative_SPY'], label='SPY', color='green', linewidth=1.2)

        # Highlight regimes with background color
        prev_label = None
        start_date = None

        for date, row in df.iterrows():
            curr_label = row['regime_label']
            if curr_label != prev_label:
                if prev_label is not None:
                    ax.axvspan(start_date, date, color=regime_colors[prev_label], alpha=0.2)
                start_date = date
                prev_label = curr_label

        ax.axvspan(start_date, df.index[-1], color=regime_colors[prev_label], alpha=0.2)

        ax.set_title("Cumulative Returns with Macro Regime Overlays")
        ax.set_ylabel("Cumulative Return")
        ax.set_xlabel("Date")
        plt.xticks(rotation=45)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_drawdowns(self):
        """
        Plot drawdown of the portfolio and SPY with macro regime overlays.
        """
        regime_colors = {
            'Divergent Macro (Risk-On)': '#2ECC71',
            'Transition Zone': '#F39C12',
            'Flight to Safety (Risk-Off)': '#E74C3C'
        }

        df = self.returns.copy()
        df['Portfolio_Cum'] = (1 + df['Portfolio_Return']).cumprod()
        df['SPY_Cum'] = (1 + df['return_spy']).cumprod()

        # Calculate drawdown
        df['DD_Portfolio'] = df['Portfolio_Cum'] / df['Portfolio_Cum'].cummax() - 1
        df['DD_SPY'] = df['SPY_Cum'] / df['SPY_Cum'].cummax() - 1

        # Merge regime labels
        df['Regime'] = self.regimes
        df['regime_label'] = df['Regime'].map(self.regime_labels)

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(df.index, df['DD_Portfolio'], label='Portfolio Drawdown', color='black', linewidth=1.5)
        ax.plot(df.index, df['DD_SPY'], label='SPY Drawdown', color='green', linewidth=1.2)

        # Regime background shading
        prev_label = None
        start_date = None
        for date, row in df.iterrows():
            curr_label = row['regime_label']
            if curr_label != prev_label:
                if prev_label is not None:
                    ax.axvspan(start_date, date, color=regime_colors[prev_label], alpha=0.2)
                start_date = date
                prev_label = curr_label
        ax.axvspan(start_date, df.index[-1], color=regime_colors[prev_label], alpha=0.2)

        ax.set_title("Drawdowns with Macro Regime Overlays")
        ax.set_ylabel("Drawdown (%)")
        ax.set_xlabel("Date")
        plt.xticks(rotation=45)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        plt.show()

    def run(self):
        print("Fetching data...")
        self.fetch_data()
        print("Calculating features...")
        self.calculate_features()
        print("Training Hidden Markov Model...")
        self.train_hmm()
        print("Applying regime-based allocation...")
        self.apply_allocations()
        print("Calculating performance metrics...")
        self.calculate_performance_metrics()
        print("Plotting Returns...")
        self.plot_return()
        print("Plotting Drawdowns...")
        self.plot_drawdowns()
        print("Done.")        

