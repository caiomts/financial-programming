import pandas as pd
import itertools
import pandas_datareader.data as web
from pandas.tseries.offsets import BDay
from datetime import datetime
import random
import math
import collections

# Stocks data

tickers = ['FDX', 'GOOGL', 'XOM', 'KO', 'NOK', 'MS', 'IBM']
stocks_df = web.DataReader(tickers, 'yahoo', start=datetime(2010, 1, 1)).High


# Descriptors guarantee the type and behavior of variables


class Date:
    """General descriptor for date"""

    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if isinstance(value, datetime):
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError('value must be a datetime')


class OneOfStock:
    """General descriptor for stocks"""

    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if value in set(tickers):
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError("value must be on of 'FDX', 'GOOGL', 'XOM', 'KO', 'NOK', 'MS', 'IBM'")


class OneOfMode:
    """General descriptor for investor mode"""

    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if value in {defensive, aggressive, mixed}:
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError("value must be on of defensive, aggressive, mixed")


class Monetary:
    """General descriptor for monetary entries"""

    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if (value is None) or (value >= 0):
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError('value must be >= 0')


class Investment:
    """Investment is an abstract object. Bonds and Stocks inherit attributes and methods"""
    pv = Monetary('pv')
    start_date = Date('start_date')
    end_date = Date('end_date')

    def __init__(self, pv, start_date, end_date):
        self.pv = pv
        self.start_date = start_date
        self.end_date = end_date
        self.term = self.end_date - self.start_date
        self.cash_flow = None

    def return_on_investment(self):
        return round((self.cash_flow.iloc[-1, 0] / self.pv) - 1, 4)

    def total_return(self):
        return round(self.cash_flow.iloc[-1, 0] - self.pv, 2)

    def risk_on_investment(self):
        return round(self.cash_flow.pct_change().std(), 4)


class Bonds(Investment):
    """All Bonds"""

    def __init__(self, pv, rate: float, start_date, end_date):
        super(Bonds, self).__init__(pv, start_date, end_date)
        self.rate = rate
        self.rate_flow = pd.Series(itertools.repeat((1 + self.rate) ** (1 / 365) - 1, self.term.days))
        self.rate_flow.iloc[0] = 0
        cash_flow = pd.DataFrame({'Date': pd.date_range(self.start_date, end=self.end_date, freq="D", closed='left'),
                                  'Value': (1 + self.rate_flow).cumprod() * self.pv})
        self.cash_flow = cash_flow.set_index('Date')

    @classmethod  # Call a bond as a short one. Ensure rate, min price and min period
    def short(cls, start_date,  pv=250):
        if pv < 250:
            raise ValueError('pv must be >= 250')
        rate, end_date = 0.015, start_date + pd.DateOffset(years=2)
        bond = cls(pv, rate, start_date, end_date)
        return bond

    @classmethod  # Call a bond as a long one. Ensure rate, min price and min period
    def long(cls, start_date, pv=1000):
        if pv < 1000:
            raise ValueError('pv must be >= 1000')
        rate, end_date = 0.03, start_date + pd.DateOffset(years=5)
        bond = cls(pv, rate, start_date, end_date)
        return bond

    def compound_rate(self, end_date):
        """Returns compound rate for a given date"""
        total_days = (end_date - self.start_date).days
        return round((1 + self.rate_flow.loc[self.rate_flow.index <= total_days]).prod() - 1, 4)


class Stocks(Investment):
    """All stocks"""
    name = OneOfStock('name')

    def __init__(self, name, start_date, end_date, num_stocks: int = 1):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.num_stocks = num_stocks
        self.price = stocks_df.loc[(self.start_date - BDay(1)):self.end_date, self.name]
        self.pv = self.price.iloc[0] * self.num_stocks
        cash_flow = pd.DataFrame({}, index=pd.date_range(start=(self.start_date - BDay(1)),
                                                         end=self.end_date, freq="D", closed='left'))
        cash_flow = cash_flow.merge(pd.DataFrame({'Value': self.price * self.num_stocks}), how='outer',
                                    right_on='Date', left_index=True)
        self.cash_flow = cash_flow.set_index('Date').fillna(method='pad').loc[self.start_date:, ]

    def return_on_stock(self, end_date):
        """Returns return on stock in a given date"""
        return self.price[self.price.index <= end_date].iloc[-1] / self.price.iloc[0] - 1

    def get_price(self, end_date):
        """Returns the price in a given date"""
        return self.price[self.price.index <= end_date].iloc[-1]

# Investor is a named tuple if mode and budget as attributes


Investor = collections.namedtuple('Investor', ['mode', 'budget'])


class Portfolio:
    """All portfolios. Links Investor with investments"""
    mode = OneOfMode('mode')
    budget = Monetary('budget')

    def __init__(self, investor: Investor, start_date, end_date, investment_weights: tuple = (75, 25)):
        self.investor = investor
        self.budget = self.investor[1]
        self.start_date = start_date
        self.end_date = end_date
        self.investment_weights = investment_weights
        self.term = self.end_date - self.start_date
        self.mode = self.investor[0]
        self.investments = self.mode(self)
        self.invest_list = [(k, i) for k, i in self.investments.items()]

    def portfolio_cash_flow(self):
        investment_values = [self.investments[investment[0]].cash_flow for investment in self.invest_list]
        investment_keys = [investment[0] for investment in self.invest_list]
        port_cf = pd.concat(investment_values, keys=investment_keys,
                            names=['Investment', 'Date']).reset_index(level='Investment').fillna(method='pad')
        return port_cf[port_cf.index < self.end_date]


# Mode functions. Defensive and Aggressive just fill the dict with bonds and stocks respectively,
# according with the type and values returned by accounting_investment().
def defensive(portfolio):
    """Builds a defensive portfolio"""
    new_list = []
    bonds = accounting_investment(portfolio)
    investments = {key: getattr(Bonds, key)(start_date=portfolio.start_date, pv=bonds[key]) for key in bonds}
    investments_list = [(k, i) for k, i in investments.items()]
    end_dates = [(investments[investment[0]].end_date,
                  investments[investment[0]].cash_flow.iloc[-1, 0]) for investment in investments_list]
    for end_date in end_dates:
        if end_date[0] < portfolio.end_date:
            # Deal with overdue bonds.  Starts a recursive function to build a new portfolio with same mode
            # and calculates the new budget as bond's final value + rest of old budget.
            investor = Investor(portfolio.investor[0], end_date[1] + portfolio.budget)
            new_port = Portfolio(investor, start_date=end_date[0],
                                 end_date=portfolio.end_date)
            new_list.extend([(k, i) for k, i in new_port.investments.items()])
            portfolio.budget += new_port.budget
    investments_2 = {k + '_' + str(math.trunc(random.random() * 100)): i for k, i in new_list}
    return {**investments, **investments_2}


def aggressive(portfolio):
    """Builds an aggressive portfolio"""
    stocks = accounting_investment(portfolio)
    return {key: Stocks(name=key, start_date=portfolio.start_date, end_date=portfolio.end_date,
                        num_stocks=stocks[key]) for key in stocks}


def mixed(portfolio):
    """builds a mixed portfolio"""
    investments = {}
    temp = []
    # while budget is enough to buy a short bond, randomly weighted choose bond or stock.
    while portfolio.budget >= Bonds.short(start_date=portfolio.start_date).pv:
        mode_function = random.choices([pick_stock(portfolio), pick_bond(portfolio)],
                                       weights=portfolio.investment_weights)
        try:  # if no bond or stock is bought just move on to the next
            portfolio.budget += - mode_function[0][1]  # subtract the acquisition price from the budget
            key = list(mode_function[0][0].keys())[0]
            if key in investments:
                investments[key] += mode_function[0][0][key]
            else:
                investments[key] = mode_function[0][0][key]
        except TypeError:   # Skips when "pick stocks" doesn't returns a dict.
            pass
    for key in investments:
        if key in {'short', 'long'}:
            investments[key] = getattr(Bonds, key)(pv=investments[key], start_date=portfolio.start_date)
            if investments[key].end_date <= portfolio.end_date:
                budget = investments[key].cash_flow.iloc[-1, 0] + portfolio.budget
                investor = Investor(portfolio.investor[0], budget)
                new_port = Portfolio(investor, start_date=investments[key].end_date,
                                     end_date=portfolio.end_date, investment_weights=portfolio.investment_weights)
                temp.extend([(k, i) for k, i in new_port.investments.items()])
                portfolio.budget += new_port.budget
        elif key in tickers:
            investments[key] = Stocks(key, start_date=portfolio.start_date, end_date=portfolio.end_date,
                                      num_stocks=investments[key])
        else:
            pass
    investments2 = {k + '_' + str(math.trunc(random.random() * 100)): i for k, i in temp}
    return {**investments, **investments2}


# Functions for mode
def pick_bond(portfolio):
    """Randomly picks a bond"""
    # budget is enough to buy a long bond, randomly choose one.
    if portfolio.budget >= Bonds.long(start_date=portfolio.start_date).pv:
        bond_type = random.choice(['long', 'short'])
        value = getattr(Bonds, bond_type)(start_date=portfolio.start_date).pv
        return {bond_type: value}, value
    # budget is enough to buy a short bond, buy all budget.
    else:
        bond_type = 'short'
        value = portfolio.budget
        return {bond_type: value}, value


def pick_stock(portfolio):
    """Randomly picks a stock"""
    stock = random.choice(tickers)
    try:
        price = Stocks(name=stock, start_date=portfolio.start_date, end_date=portfolio.end_date).pv
        max_num_stocks = int(portfolio.budget / price)
        # Exception when the range date doesn't allow pick a stock. when Bonds due in the last few days of a portfolio.
    except KeyError:
        max_num_stocks = 0
    if max_num_stocks < 1:
        pass
    else:
        amount = random.randint(1, max_num_stocks)
        return {stock: amount}, amount * price


def accounting_investment(portfolio):
    """Accounts bonds or stocks"""
    investments = {}
    if portfolio.mode is defensive:
        min_budget = Bonds.short(start_date=portfolio.start_date).pv
        function = pick_bond
    else:
        min_budget = 100
        function = pick_stock
    while portfolio.budget >= min_budget:
        invest = function(portfolio)
        try:  # if no bond or stock is bought just move on to the next
            key = list(invest[0].keys())[0]
            portfolio.budget += - invest[1]
            if key in investments:
                investments[key] += invest[0][key]
            else:
                investments[key] = invest[0][key]
        except TypeError:   # Skips when "pick stocks" doesn't returns a dict.
            pass
    return investments


# Working on simulations
def return_and_vol_on_portfolios(portfolio_lists: list, lists_names: list):
    """Computes mean return and the mean volatility for each portfolios group"""
    i = 0
    return_on_group = {}
    for group in portfolio_lists:
        return_on_portfolio = [(p.portfolio_cash_flow().groupby('Date').sum().Value[-1] /
                               p.portfolio_cash_flow().groupby('Date').sum().Value[0]) - 1 for p in group]
        vol_on_portfolio = [p.portfolio_cash_flow().groupby('Date').sum().pct_change().std().Value for p in group]
        mean_return_portfolio = sum(return_on_portfolio) / len(return_on_portfolio)
        mean_vol_portfolio = sum(vol_on_portfolio) / len(vol_on_portfolio)
        return_on_group[lists_names[i]] = (round(mean_return_portfolio, 4), round(mean_vol_portfolio, 4))
        i += 1
    return pd.DataFrame(return_on_group, index=['Investment return', 'daily volatility'])


def mean_monthly_value_on_portfolios(portfolio_lists: list, lists_names: list):
    """Calculates the mean monthly values for each portfolio group"""
    list_cash_flows = []
    for group in portfolio_lists:
        cash_flows = [p.portfolio_cash_flow().groupby(['Date']).sum().resample('M').asfreq() for p in group]
        keys = [p for p in group]
        group_cash_flow = pd.concat(cash_flows, keys=keys,
                                    names=['Portfolio', 'Date']).reset_index(level='Date') \
            .groupby(['Date']).mean()
        list_cash_flows.append(group_cash_flow)
    return pd.concat(list_cash_flows, keys=lists_names,
                     names=['Portfolio_group', 'Date']).reset_index(level='Date')


def mean_yearly_return_on_portfolios(portfolio_lists: list, lists_names: list):
    """Calculates the mean yearly return for each portfolio group"""
    list_cash_flows = []
    for group in portfolio_lists:
        cash_flows = [p.portfolio_cash_flow().groupby(['Date']).sum().resample('Y')
                      .asfreq().pct_change() for p in group]
        keys = [p for p in group]
        group_cash_flow = pd.concat(cash_flows, keys=keys,
                                    names=['Portfolio', 'Date']).reset_index(level='Date') \
            .groupby(['Date']).mean()
        list_cash_flows.append(group_cash_flow)
    return pd.concat(list_cash_flows, keys=lists_names,
                     names=['Portfolio_group', 'Date']).reset_index(level='Date')
