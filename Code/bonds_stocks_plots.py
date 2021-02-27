import investor_sim_objects as investso
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

sns.set_theme(style="whitegrid")

# Part 1

period = pd.DateOffset(years=50)

long = investso.Bonds.long(period, 1000, start_date=datetime(2000, 1, 1))
short = investso.Bonds.short(period, 250, start_date=datetime(2000, 1, 1))

long_reshape = long.cash_flow().resample('Y').asfreq()
shor_reshape = short.cash_flow().resample('Y').asfreq()

bonds = pd.concat([long_reshape, shor_reshape], keys=['long', 'short'],
                  names=['investment', 'date']).reset_index(level='investment')

g = sns.relplot(data=bonds.reset_index(), x='date', y="value", hue="investment", linewidth=2.5)
g.set(xlabel='Years', ylabel='Price', title='Bonds Prices', ylim=(100, 5000))
plt.savefig(os.path.abspath('../Results/50y_plot.png'), dpi=800)

plt.clf()

# Part 2

start = datetime(2016, 9, 1)
end = datetime(2021, 1, 1)

tickers = ['FDX', 'GOOGL', 'XOM', 'KO', 'NOK', 'MS', 'IBM']

stocks = [investso.Stocks(pd.DateOffset(years=5), ticker, 1, start) for ticker in tickers]

for stock in stocks:
    f = sns.lineplot(data=stock.price)
    f.set(xlabel='Years', ylabel='Price', title='Stock Prices')

plt.savefig(os.path.abspath('../Results/stock_plot.png'), dpi=800)






