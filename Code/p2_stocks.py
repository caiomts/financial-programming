import investor_simulator as invsim
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker

# Handle date time conversions between pandas and matplotlib
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# set date
start_date = datetime(2016, 9, 1)
end_date = datetime(2021, 1, 1)

tickers = ['FDX', 'GOOGL', 'XOM', 'KO', 'NOK', 'MS', 'IBM']

# call stocks
stocks = [invsim.Stocks(ticker, start_date=start_date, end_date=end_date).price for ticker in tickers]

stocks = pd.concat(stocks, keys=[ticker for ticker in tickers],
                   names=['investment', 'date']).reset_index(level='investment')


sns.set_theme()
sns.set_context("paper", font_scale=1.5)
fig, ax = plt.subplots(figsize=(15, 10))
g = sns.lineplot(data=stocks.reset_index(), x='date', y=0, hue="investment", linewidth=1.5)
g.set(xlabel='Years', ylabel='Price', title='Bonds Prices')
ax.yaxis.set_major_locator(ticker.MultipleLocator(200))
date_form = DateFormatter("%Y")
ax.xaxis.set_major_formatter(date_form)
plt.savefig(os.path.abspath('../Results/p2_stocks_plot.png'), dpi=800)