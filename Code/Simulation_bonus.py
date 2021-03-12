import investor_simulator as invsim
import os
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime

# Handle date time conversions between pandas and matplotlib
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# set dates and budget
start_date = datetime(2016, 9, 1)
end_date = datetime(2021, 1, 1)


# Call Portfolios
defensive_group = [invsim.Portfolio(invsim.Investor(invsim.defensive, max(random.gauss(20000, 5000), 0)),
                                    start_date=start_date, end_date=end_date) for _ in range(500)]

aggressive_group = [invsim.Portfolio(invsim.Investor(invsim.aggressive, max(random.gauss(20000, 5000), 0)),
                                     start_date=start_date, end_date=end_date) for _ in range(500)]

mixed_group = [invsim.Portfolio(invsim.Investor(invsim.mixed, max(random.gauss(20000, 5000), 0)),
                                start_date=start_date, end_date=end_date) for _ in range(500)]

groups = [defensive_group, aggressive_group, mixed_group]
names = ['defensive', 'aggressive', 'mixed']

results = invsim.return_and_vol_on_portfolios(groups, names)

fig, ax = plt.subplots(figsize=(8, 2))
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)
ax.set_frame_on(False)
tabla = pd.plotting.table(ax, results, loc='upper right', colWidths=[0.2]*len(results.columns))
tabla.auto_set_font_size(False)
tabla.set_fontsize(13)
tabla.scale(1.2, 1.5)
plt.savefig('../Results/pb_portfolios_returns_and_vol.png', transparent=True)


means = invsim.mean_monthly_value_on_portfolios(groups, names)

sns.set_theme()
sns.set_context("paper", font_scale=1.5)
fig, ax = plt.subplots(figsize=(15, 10))
g = sns.lineplot(data=means.reset_index(), x='Date', y="Value", hue="Portfolio_group", linewidth=2.5)
g.set(xlabel='Years', ylabel='Price', title='Portfolio Value')
date_form = DateFormatter("%m-%Y")
ax.yaxis.set_major_locator(ticker.MultipleLocator(500))
ax.xaxis.set_major_formatter(date_form)
plt.savefig(os.path.abspath('../Results/pb_portfolios_monthly_price_plot.png'), dpi=800)


results = invsim.mean_yearly_return_on_portfolios(groups, names)


sns.set_theme()
sns.set_context("paper", font_scale=1.5)
fig, ax = plt.subplots(figsize=(15, 10))
g = sns.barplot(data=results[results.Date >= '2017'].reset_index(), x='Date', y="Value",
                hue="Portfolio_group", linewidth=2.5)
g.set(xlabel='Years', ylabel='Annual return', title='Portfolio Returns')
labels = [2017, 2018, 2019, 2020]
x = np.arange(len(labels))
ax.set_xticks(x)
ax.set_xticklabels(labels)
plt.savefig(os.path.abspath('../Results/pb_portfolios_annual_return_plot.png'), dpi=800)

# What is the best stock.

return_on_stocks = pd.DataFrame([invsim.Stocks(x, start_date=datetime(2016, 12, 31),
                                end_date=datetime(2017, 12, 31)).return_on_stock(datetime(2017, 12, 31))
                                for x in invsim.tickers], index=invsim.tickers,
                                columns=['Return']).sort_values('Return', ascending=False)


sns.set_theme()
sns.set_context("paper", font_scale=1.5)
fig, ax = plt.subplots(figsize=(15, 10))
g = sns.barplot(data=return_on_stocks.reset_index(), x='Return', y="index",
                linewidth=2.5)
g.set(xlabel='Returns', ylabel='Stocks', title='Return on Stocks - 2017')
sns.despine(left=True, bottom=True)
plt.savefig(os.path.abspath('../Results/pb_2017_stocks_returns.png'), dpi=800)

