import investor_simulator as investso
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime

# Handle date time conversions between pandas and matplotlib
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# Use white grid plot background from seaborn
sns.set(font_scale=1.5, style="whitegrid")

# Part 1

period = pd.DateOffset(years=50)

long = investso.Bonds.long(period, 1000, start_date=datetime(2000, 1, 1))
short = investso.Bonds.short(period, 250, start_date=datetime(2000, 1, 1))

long_reshape = long.cash_flow().resample('Y').asfreq()
shor_reshape = short.cash_flow().resample('Y').asfreq()

bonds = pd.concat([long_reshape, shor_reshape], keys=['long', 'short'],
                  names=['investment', 'date']).reset_index(level='investment')

fig, ax = plt.subplots(figsize=(15, 10))
g = sns.lineplot(data=bonds.reset_index(), x='date', y="value", hue="investment", linewidth=2.5)
g.set(xlabel='Years', ylabel='Price', title='Bonds Prices')
plt.savefig(os.path.abspath('../Results/bonds_plot.png'), dpi=800)


plt.clf()

# Part 2

start = datetime(2016, 1, 1)

tickers = ['FDX', 'GOOGL', 'XOM', 'KO', 'NOK', 'MS', 'IBM']

stocks = [investso.Stocks(pd.DateOffset(years=5), ticker, 1, start).price for ticker in tickers]

stocks = pd.concat(stocks, keys=[ticker for ticker in tickers],
                   names=['investment', 'date']).reset_index(level='investment')

fig, ax = plt.subplots(figsize=(15, 10))
g = sns.lineplot(data=stocks.reset_index(), x='date', y=0, hue="investment", linewidth=2.5)
g.set(xlabel='Years', ylabel='Price', title='Bonds Prices')
date_form = DateFormatter("%Y")
ax.xaxis.set_major_formatter(date_form)
plt.savefig(os.path.abspath('../Results/stocks_plot.png'), dpi=800)



