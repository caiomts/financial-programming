import investor_simulator as invsim
import os
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime
from datetime import date
import streamlit as st
import plotly.graph_objects as go

# Handle date time conversions between pandas and matplotlib
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

st.set_page_config(page_title=None, page_icon=None, layout='centered', initial_sidebar_state='auto')

# set dates and budget
start_date_sb = st.sidebar.date_input('Start Date (> 2010/01/01)', value=date(2010, 1, 2))
end_date_sb = st.sidebar.date_input('End Date (< 2020/04/02)', value=date(2020, 4, 1))
budget = st.sidebar.slider('Define the budget', 1000, 100000, 1000)
simulations = st.sidebar.slider('Simulations', 10, 500, 10)

start_date = datetime.combine(start_date_sb, datetime.min.time())
end_date = datetime.combine(end_date_sb, datetime.min.time())

# Call Portfolios
defensive = invsim.Investor(invsim.defensive, budget)
defensive_group = [invsim.Portfolio(defensive, start_date=start_date, end_date=end_date) for _ in range(simulations)]

aggressive = invsim.Investor(invsim.aggressive, budget)
aggressive_group = [invsim.Portfolio(aggressive, start_date=start_date, end_date=end_date) for _ in range(simulations)]

mixed = invsim.Investor(invsim.mixed, budget)
mixed_group = [invsim.Portfolio(mixed, start_date=start_date, end_date=end_date,
                                investment_weights=(25, 75)) for _ in range(simulations)]

groups = [defensive_group, aggressive_group, mixed_group]
names = ['defensive', 'aggressive', 'mixed']

results = invsim.return_and_vol_on_portfolios(groups, names)

header = ['Index', 'Defensive', 'Aggressive', 'Mixed']

fig = go.Figure(data=[go.Table(
    header=dict(values=header,
                fill_color='#4575b4', align='center', font=dict(color='white', size=23), height=50),
    cells=dict(values=[results.index, results.defensive, results.aggressive, results.mixed],
               fill_color='#e0f3f8', align='center', font=dict(color='#999999', size=20), height=40)
)])

st.plotly_chart(fig, use_container_width=True)

#fig, ax = plt.subplots(figsize=(8, 2))
#ax.xaxis.set_visible(False)
#ax.yaxis.set_visible(False)
#ax.set_frame_on(False)
#tabla = pd.plotting.table(ax, results, loc='upper right', colWidths=[0.2]*len(results.columns))
#tabla.auto_set_font_size(False)
#tabla.set_fontsize(13)
#tabla.scale(1.2, 1.5)
#st.pyplot(fig)


means = invsim.mean_monthly_value_on_portfolios(groups, names)


sns.set_theme()
sns.set_context("paper", font_scale=1.5)
fig, ax = plt.subplots(figsize=(15, 10))
g = sns.lineplot(data=means.reset_index(), x='Date', y="Value", hue="Portfolio_group", linewidth=2.5)
g.set(xlabel='Years', ylabel='Price', title='Portfolio Value')
date_form = DateFormatter("%m-%Y")
#ax.yaxis.set_major_locator(ticker.MultipleLocator(1000))
ax.xaxis.set_major_formatter(date_form)
st.pyplot(fig)


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
st.pyplot(fig)
