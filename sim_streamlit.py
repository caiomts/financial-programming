import Code.investor_simulator as invsim
from datetime import datetime
from datetime import date, timedelta
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


st.set_page_config(page_title='Portfolio Simulation', page_icon=None, layout='wide', initial_sidebar_state='auto')

st.markdown(
    """<a style='display: block; text-align: right;'>A Web App by </a>
    <a style='display: block; text-align: right;' 
    href="https://github.com/caiomts/financial-programming">Caio Mescouto</a>
    """,
    unsafe_allow_html=True,
)

st.title('Portfolio Simulation')

'''
Comparing portfolio allocation.
To know more about it [README](https://github.com/caiomts/financial-programming/blob/master/README.md)
'''

# set dates and budget
start_date_sb = st.sidebar.date_input('Start Date (> 2010/01/01)', value=date.today() - timedelta(days=1800))
end_date_sb = st.sidebar.date_input('End Date (< Last business day)', value=date.today() - timedelta(days=4))
budget = st.sidebar.slider('Define the budget', min_value=1000, max_value=100000, value=1000, step=100)
stock_weight = st.sidebar.slider('% of Stocks on Mixed Portfolio', min_value=0, max_value=100, value=50, step=10)
simulations = st.sidebar.slider('Simulations', min_value=50, max_value=500, value=50, step=50)

start_date = datetime.combine(start_date_sb, datetime.min.time())
end_date = datetime.combine(end_date_sb, datetime.min.time())

# Call Portfolios
defensive = invsim.Investor(invsim.defensive, budget)
defensive_group = [invsim.Portfolio(defensive, start_date=start_date, end_date=end_date) for _ in range(simulations)]

aggressive = invsim.Investor(invsim.aggressive, budget)
aggressive_group = [invsim.Portfolio(aggressive, start_date=start_date, end_date=end_date) for _ in range(simulations)]

mixed = invsim.Investor(invsim.mixed, budget)
mixed_group = [invsim.Portfolio(mixed, start_date=start_date, end_date=end_date,
                                investment_weights=(stock_weight, 100 - stock_weight))
               for _ in range(simulations)]

groups = [defensive_group, aggressive_group, mixed_group]
names = ['defensive', 'aggressive', 'mixed']

results = invsim.return_and_vol_on_portfolios(groups, names)

header = ['Index', 'Defensive', 'Aggressive', 'Mixed']

fig = go.Figure(data=[go.Table(
    header=dict(values=header,
                fill_color='#8da0cb', align='center', font=dict(color='white', size=23), height=50),
    cells=dict(values=[results.index, results.defensive, results.aggressive, results.mixed],
               fill_color=['#8da0cb', '#66c2a5', '#66c2a5', '#66c2a5'],
               align='center', font=dict(color='white',
                                         size=20), height=40)
)])
st.plotly_chart(fig, use_container_width=True)

# Line Plot
means = invsim.mean_monthly_value_on_portfolios(groups, names)

fig = px.line(means.reset_index(), x="Date", y="Value", color='Portfolio_group', title='Portfolio Value'
              , height=700, template='seaborn',
              color_discrete_map={'defensive': '#66c2a5', 'aggressive': '#fc8d62', 'mixed': '#8da0cb'})
fig.update_layout(legend=dict(title=None, orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"))
st.plotly_chart(fig, use_container_width=True)


results = invsim.mean_yearly_return_on_portfolios(groups, names).dropna()

results['Date'] = results.Date.map(lambda x: x.year)


fig = px.bar(results.reset_index(), x="Date", y="Value", color='Portfolio_group',
             barmode='group', height=700, template='plotly_white',
             color_discrete_map={'defensive': '#66c2a5', 'aggressive': '#fc8d62', 'mixed': '#8da0cb'})
fig.update_layout(legend=dict(title=None, orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"))
fig.update_xaxes(type='category')
st.plotly_chart(fig, use_container_width=True)
