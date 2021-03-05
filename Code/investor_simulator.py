import pandas as pd
import numpy as np
import itertools
import pandas_datareader.data as web
from datetime import datetime
import random
import math
import collections

# Stocks data
start = datetime(2014, 1, 4)
end = datetime(2021, 1, 1)

tickers = ['FDX', 'GOOGL', 'XOM', 'KO', 'NOK', 'MS', 'IBM']
stocks_df = web.DataReader(tickers, 'yahoo', datetime(2013, 1, 10)).High


# Descriptors guarantee the type and behavior of variables


class Date:
    """General descriptor for date"""

    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if isinstance(value, datetime) or (value is None):
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
    """General descriptor for stocks"""

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


class Period:
    """General descriptor for period"""

    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if isinstance(value, pd.DateOffset):
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError('value must be >= 1 and Type pd.DateOffset')


class Rates:
    """General descriptor for rates"""

    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if (value is None) or isinstance(value, (float, pd.Series)):
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError('value must be float or pandas.Series')


def stocks_date(date):
    """Returns closest date before the argument for which stock data are available"""
    if date in stocks_df.index:
        new_date = date
    else:
        while date not in stocks_df.index:
            try:
                date += - pd.Timedelta('1 day')
            except KeyError:
                pass
        new_date = date
    return new_date


class Investment:
    """Investment is an abstract object. Bonds and Stocks inherit attributes and methods"""
    period = Period('period')
    pv = Monetary('pv')
    rate = Rates('rate')
    start_date = Date('start_date')

    def __init__(self, period, pv, start_date):
        self.period = period
        self.pv = pv
        self.value = None
        self.rate = None
        self.start_date = start_date
        self.end_date = self.start_date + self.period

    def return_on_investment(self):
        return (self.value.iloc[-1, 0] / self.pv) - 1

    def total_return(self):
        return self.value.iloc[-1, 0] - self.pv

    def risk_on_investment(self):
        return np.std(self.value.pct_change())


class Bonds(Investment):
    """All Bonds"""
    min_price = Monetary('min_price')
    min_period = Period('min_period')

    def __init__(self, period, pv, rate, start_date=start, min_price=0.0, min_period=pd.DateOffset(years=1)):
        super(Bonds, self).__init__(period, pv, start_date)
        if self.pv < min_price:
            raise AttributeError('pv should be >= %s' % min_price)
        else:
            self._min_price = min_price
        if (start_date + self.period) < (start_date + min_period):
            raise AttributeError('period should be >= %s' % min_period)
        else:
            self._min_period = min_period
        self.days_year = int((self.end_date - self.start_date).days / 360)
        self.rate = rate
        # Transform interest rate into pd.Series and
        # ensure that pd.Series length is equal to the number of days in the period.
        if not isinstance(self.rate, pd.Series):
            total_days = (self.end_date - self.start_date).days
            self.rate = pd.Series(itertools.repeat((1 + self.rate) ** (1 / (total_days / self.days_year)) - 1,
                                                   total_days))
            self.rate.iloc[0] = 0
        # Set value as DataFrame with Date Index
        date = pd.date_range(self.start_date, end=self.end_date, freq="D", closed='left')
        value = pd.DataFrame({'value': (1 + self.rate).cumprod() * self.pv})
        self.value = value.set_index(date)

    @classmethod  # Call a bond as a short one. Ensure rate, min price and min period
    def short(cls, period=pd.DateOffset(years=2), pv=250, start_date=start):
        min_price, min_period, rate = 250, pd.DateOffset(years=2), 0.015
        bond = cls(period, pv, rate, start_date, min_price, min_period)
        return bond

    @classmethod  # Call a bond as a long one. Ensure rate, min price and min period
    def long(cls, period=pd.DateOffset(years=5), pv=1000, start_date=start):
        min_price, min_period, rate = 1000, pd.DateOffset(years=5), 0.03
        bond = cls(period, pv, rate, start_date, min_price, min_period)
        return bond

    def cash_flow(self, end_date=None):
        """Returns the bond cash flow for a given date or entire period"""
        if end_date is None:
            return self.value
        else:
            return self.value[self.value.index <= end_date]

    def compound_rate(self, end_date=None):
        """Returns compound rate for a given date or entire period"""
        if end_date is None:
            return (1 + self.rate).prod() - 1
        else:
            total_days = (end_date - self.start_date).days
            subset_rate = self.rate.iloc[:total_days + 1]
            return (1 + subset_rate).prod() - 1


class Stocks(Investment):
    """All stocks"""
    name = OneOfStock('name')

    def __init__(self, period, name, num_stocks: int = 1, start_date=start):
        self.period = period
        self.start_date = start_date
        self.end_date = self.start_date + self.period
        self.name = name
        self.num_stocks = num_stocks
        self.price = stocks_df.loc[stocks_date(self.start_date):stocks_date(self.end_date), self.name]
        self.pv = self.price.iloc[0] * self.num_stocks
        value = pd.DataFrame({}, index=pd.date_range(start=self.start_date, end=self.end_date, freq="D", closed='left'))
        value = value.merge(pd.DataFrame({'value': self.price.loc[stocks_date(self.start_date):
                                                                  stocks_date(self.end_date)] * self.num_stocks})
                            , how='left', right_on='Date', left_index=True)
        self.value = value.set_index('Date').fillna(method='pad').fillna(method='bfill')

    def return_on_stock(self, end_date=None):
        """Returns return on stock in a given date or entire period"""
        if end_date is None:
            return (self.price.iloc[-1] / self.price.iloc[0]) - 1
        else:
            date = stocks_date(end_date)
            return self.price[self.price.index == date] / self.price.iloc[0] - 1

    def get_price(self, end_date=None):
        """Returns the price in a given date or entire period"""
        if end_date is None:
            return self.price.iloc[-1]
        else:
            date = stocks_date(end_date)
            return self.price[self.price.index == date]


Investor = collections.namedtuple('Investor', ['mode', 'budget'])


class Portfolio:
    """All portfolios"""
    mode = OneOfMode('mode')
    budget = Monetary('budget')
    period = Period('period')

    def __init__(self, investor, period, start_date=start, recalculate: bool = False, weights=[75, 25]):
        self.investor = investor
        self.mode = investor[0]
        self.budget = investor[1]
        self.period = period
        self.start_date = start_date
        self.recalculate = recalculate
        self.weights = weights
        self.investments = self.mode(self)  # Automatically call the mode function and build the portfolio
        self.invest_list = [(k, i) for k, i in self.investments.items()]

    def invest_weights(self):
        weights = np.array(self.budget)
        for invest in self.invest_list:
            key = invest[0]
            weight = self.investments[key].pv / self.investor[1]
            weights = np.append(weights, weight)
        return weights

    def portfolio_return(self):
        if self.recalculate is True:
            raise ValueError('This Methods works only for recalculate == False')
        else:
            return_on_investment = np.array([self.investments[investment[0]].return_on_investment() for investment
                                             in self.invest_list]).reshape(len(self.investments), )
            return_on_investment = np.insert(return_on_investment, 0, np.array(0))
            return self.invest_weights().T @ return_on_investment

    def portfolio_vol(self):
        if self.recalculate is True:
            raise ValueError('This Methods works only for recalculate == False')
        else:
            weights = self.invest_weights()
            length = len(self.invest_list[0][1].value)
            vol_on_investment = np.array([self.investments[investment[0]].value.pct_change() for investment in
                                          self.invest_list]).reshape(len(self.investments), length)
            vol_on_investment = np.insert(vol_on_investment, 0, 0, axis=0)
            return (weights.T @ np.cov(vol_on_investment[:, 1:]) @ weights) ** 0.5

    def portfolio_cash_flow(self):
        investment_values = [self.investments[investment[0]].value for investment in self.invest_list]
        investment_keys = [investment[0] for investment in self.invest_list]
        port_cf = pd.concat(investment_values, keys=investment_keys,
                            names=['investment', 'date']).reset_index(level='investment').fillna(method='pad')
        port_cf.value += self.budget
        end_date = self.start_date + self.period
        return port_cf[port_cf.index < end_date]


# Mode functions. Defensive and Aggressive just fill the dict with bonds and stocks respectively,
# according with the type and values returned by accounting_investment().
def defensive(portfolio):
    """Builds a defensive portfolio"""
    bonds = accounting_investment(portfolio)
    return {key: getattr(Bonds, key)(pv=bonds[key], period=portfolio.period,
                                     start_date=portfolio.start_date) for key in bonds}


def aggressive(portfolio):
    """Builds an aggressive portfolio"""
    stocks = accounting_investment(portfolio)
    return {key: Stocks(portfolio.period, key, stocks[key], start_date=portfolio.start_date) for key in stocks}


def mixed(portfolio):
    """builds a mixed portfolio"""
    investments = {}
    investments2 = {}
    # while budget is enough to buy a short bond, randomly weighted choose bond or stock.
    while portfolio.budget >= Bonds.short().pv:
        mode_function = random.choices([pick_stock(portfolio), pick_bond(portfolio)],
                                       weights=portfolio.weights)
        try:  # if no bond or stock is bought just move on to the next
            portfolio.budget += - mode_function[0][1]  # subtract the acquisition price from the budget
            key = list(mode_function[0][0].keys())[0]
            if key in investments:
                num = investments[key]
                investments[key] = num + mode_function[0][0][key]
            else:
                investments[key] = mode_function[0][0][key]
        except TypeError:
            pass
    for key in investments:  # loop dict filling it with bonds or stocks
        if (key in {'short', 'long'}) and (portfolio.recalculate is False):
            investments[key] = getattr(Bonds, key)(pv=investments[key], period=portfolio.period,
                                                   start_date=portfolio.start_date)
        elif key in {'short', 'long'}:  # in case of bond overdue
            pass
        elif key in tickers:
            investments[key] = Stocks(portfolio.period, key, investments[key], start_date=portfolio.start_date)
        else:
            pass
    return {**investments, **investments2}


# Functions for mode
def pick_bond(portfolio):
    """Randomly picks a bond"""
    # budget is enough to buy a long bond, randomly choose one.
    if portfolio.budget >= Bonds.long().pv:
        bond_type = random.choice(['long', 'short'])
        value = getattr(Bonds, bond_type)().pv
        return {bond_type: value}, value
    # budget is enough to buy a short bond, buy all budget.
    elif portfolio.budget >= Bonds.short().pv:
        bond_type = 'short'
        value = portfolio.budget
        return {bond_type: value}, value
    else:
        pass


def pick_stock(portfolio):
    """Randomly picks a stock"""
    stock = random.choice(tickers)
    price = Stocks(pd.DateOffset(days=5), stock, start_date=portfolio.start_date).pv
    max_num_stocks = int(portfolio.budget / price)
    if max_num_stocks < 1:
        pass
    else:
        amount = random.randint(1, max_num_stocks)
        return {stock: amount}, amount * price


def accounting_investment(portfolio):
    """Accounts bonds or stocks"""
    investments = {}
    if portfolio.mode is defensive:
        min_budget = Bonds.short().pv
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
                num = investments[key]
                investments[key] = num + invest[0][key]
            else:
                investments[key] = invest[0][key]
        except TypeError:
            pass
    return investments
