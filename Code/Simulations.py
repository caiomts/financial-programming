import investor_simulator as investsim
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

# Use white grid plot background from seaborn
sns.set(font_scale=1.5, style="whitegrid")

start_date = datetime(2015, 12, 31)
end_date = datetime(2021, 1, 1)
budget = 50000

# Portfolio

defensive = investsim.Investor(investsim.defensive, budget)
defensive_group = [investsim.Portfolio(defensive, start_date=start_date, end_date=end_date) for _ in range(500)]

aggressive = investsim.Investor(investsim.aggressive, budget)
aggressive_group = [investsim.Portfolio(aggressive, start_date=start_date, end_date=end_date) for _ in range(500)]

mixed = investsim.Investor(investsim.mixed, budget)
mixed_group = [investsim.Portfolio(mixed, start_date=start_date, end_date=end_date,
                                   investment_weights=(25, 75)) for _ in range(500)]

groups = [defensive_group, aggressive_group, mixed_group]
names = ['defensive', 'aggressive', 'mixed']

results = investsim.return_and_vol_on_portfolios(groups, names)

fig, ax = plt.subplots(figsize=(8, 2))
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)
ax.set_frame_on(False)
tabla = pd.plotting.table(ax, results, loc='upper right', colWidths=[0.2]*len(results.columns))
tabla.auto_set_font_size(False)
tabla.set_fontsize(13)
tabla.scale(1.2, 1.5)
plt.savefig('../Results/portfolios_returns_and_vol_Sim4_x10.png', transparent=True)
plt.show()

means = investsim.mean_monthly_value_on_portfolios(groups, names)

fig, ax = plt.subplots(figsize=(15, 10))
g = sns.lineplot(data=means.reset_index(), x='Date', y="Value", hue="Portfolio_group", linewidth=2.5)
g.set(xlabel='Years', ylabel='Price', title='Portfolio Prices')
date_form = DateFormatter("%Y")
ax.xaxis.set_major_formatter(date_form)
plt.savefig(os.path.abspath('../Results/portfolios_monthly_price_plot_Sim4_x10.png'), dpi=800)
plt.show()

results = investsim.mean_yearly_return_on_portfolios(groups, names)

fig, ax = plt.subplots(figsize=(15, 10))
g = sns.barplot(data=results[results.Date >= '2016'].reset_index(), x='Date', y="Value",
                hue="Portfolio_group", linewidth=2.5)
g.set(xlabel='Years', ylabel='Annual return', title='Portfolio Returns')
labels = [2016, 2017, 2018, 2019, 2020]
x = np.arange(len(labels))
ax.set_xticks(x)
ax.set_xticklabels(labels)
plt.savefig(os.path.abspath('../Results/portfolios_annual_return_plot_Sim4_x10.png'), dpi=800)
plt.show()
