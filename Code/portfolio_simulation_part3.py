import investor_simulator as investso
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import os
from datetime import datetime

# Handle date time conversions between pandas and matplotlib
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# Use white grid plot background from seaborn
sns.set(font_scale=1.5, style="whitegrid")

period = pd.DateOffset(years=5)


defensive = investso.Investor(investso.defensive, 5000)
defensive_group = [investso.Portfolio(defensive, period, start_date=datetime(2016, 1, 1)) for _ in range(500)]

aggressive = investso.Investor(investso.aggressive, 5000)
aggressive_group = [investso.Portfolio(aggressive, period, start_date=datetime(2016, 1, 1)) for _ in range(500)]

mixed = investso.Investor(investso.mixed, 5000)
mixed_group = [investso.Portfolio(mixed, period, start_date=datetime(2016, 1, 1),
                                  recalculate=False) for _ in range(500)]

groups = [defensive_group, aggressive_group, mixed_group]
names = ['defensive', 'aggressive', 'mixed']


def return_on_portfolios(portfolio_lists: list, lists_names: list):
    """Computes mean return and the mean volatility for each portfolios group"""
    i = 0
    return_on_group = {}
    for group in portfolio_lists:
        return_on_portfolio = [p.portfolio_return() for p in group]
        vol_on_portfolio = [p.portfolio_vol() for p in group]
        mean_return_portfolio = sum(return_on_portfolio) / len(return_on_portfolio)
        mean_vol_portfolio = sum(vol_on_portfolio) / len(vol_on_portfolio)
        return_on_group[lists_names[i]] = (round(mean_return_portfolio, 4), round(mean_vol_portfolio, 4))
        i += 1
    return return_on_group


results = return_on_portfolios(groups, names)
results_df = pd.DataFrame(results, index=['Investment return', 'daily volatility'])

fig, ax = plt.subplots(figsize=(8, 2))
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)
ax.set_frame_on(False)
tabla = pd.plotting.table(ax, results_df, loc='upper right', colWidths=[0.2]*len(results_df.columns))
tabla.auto_set_font_size(False)
tabla.set_fontsize(13)
tabla.scale(1.2, 1.5)
plt.savefig('../Results/table_part3.png', transparent=True)

plt.clf()


def mean_portfolios(portfolio_lists: list, lists_names: list, resample='M'):
    """Calculates the mean monthly values for each portfolio group"""
    list_cash_flows = []
    for group in portfolio_lists:
        cash_flows = [p.portfolio_cash_flow().groupby(['date']).sum().resample(resample).asfreq() +
                      p.budget for p in group]
        keys = [p for p in group]
        group_cash_flow = pd.concat(cash_flows, keys=keys,
                                    names=['Portfolio', 'date']).reset_index(level='date') \
            .groupby(['date']).mean()
        list_cash_flows.append(group_cash_flow)
    return pd.concat(list_cash_flows, keys=lists_names,
                     names=['Portfolio_group', 'date']).reset_index(level='date')


means = mean_portfolios(groups, names)

fig, ax = plt.subplots(figsize=(15, 10))
g = sns.lineplot(data=means.reset_index(), x='date', y="value", hue="Portfolio_group", linewidth=2.5)
g.set(xlabel='Years', ylabel='Price', title='Portfolio Prices')
date_form = DateFormatter("%Y")
ax.xaxis.set_major_formatter(date_form)
plt.savefig(os.path.abspath('../Results/portfolios_plot.png'), dpi=800)



