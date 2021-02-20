import investor_simulation as invest_sim
import os
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt

sns.set_theme(style="whitegrid")

period = pd.Timedelta('365 days') * 51

long = invest_sim.Bonds.long(period, 1000)
short = invest_sim.Bonds.short(period, 250)

long_reshape = long.bond_cash_flow(start_date='2000-01-01', end_date='2049-12-31').resample('365D').asfreq()
shor_reshape = short.bond_cash_flow(start_date='2000-01-01', end_date='2049-12-31').resample('365D').asfreq()

bonds = pd.concat([long_reshape, shor_reshape], keys=['long', 'short'],
                  names=['investment', 'Date']).reset_index(level='investment')

g = sns.relplot(data=bonds.reset_index(), x='Date', y="daily_fv", hue="investment", linewidth=2.5)
g.set(xlabel='Years', ylabel='Price', title='Bonds Prices', ylim=(100, 5000))
plt.savefig(os.path.abspath('../Results/50y_plot.png'), dpi=600)
plt.show()
