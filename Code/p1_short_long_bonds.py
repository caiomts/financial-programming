import investor_simulator as invsim
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.ticker as ticker

# Handle date time conversions between pandas and matplotlib
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# set date
start_date = datetime(2000, 1, 1)
end_date = datetime(2050, 1, 1)

# call bonds
long = invsim.Bonds(1000, 0.03, start_date=start_date, end_date=end_date)
short = invsim.Bonds(250, 0.015, start_date=start_date, end_date=end_date)


bonds = pd.concat([long.cash_flow, short.cash_flow], keys=['long', 'short'],
                  names=['investment', 'Date']).reset_index(level='investment')

sns.set_theme()
sns.set_context("paper", font_scale=1.5)
fig, ax = plt.subplots(figsize=(15, 10))
ax.yaxis.set_major_locator(ticker.MultipleLocator(500))
g = sns.lineplot(data=bonds.reset_index(), x='Date', y="Value", hue="investment", linewidth=2.5)
g.set(xlabel='Years', ylabel='Price', title='Bonds Prices')
plt.savefig(os.path.abspath('../Results/p1_bonds_plot.png'), dpi=800)
