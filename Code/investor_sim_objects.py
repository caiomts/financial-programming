import pandas as pd
import itertools
import os
import pandas_datareader.data as web
from datetime import datetime

# Stocks data
start = datetime(2016, 9, 1)
end = datetime(2021, 1, 1)

tickers = ['FDX', 'GOOGL', 'XOM', 'KO', 'NOK', 'MS', 'IBM']
stocks_df = web.DataReader(tickers, 'yahoo', start, end).High


class Date:
    """General descriptor for date"""
    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if isinstance(value, datetime) or (value is None):
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError('value must be a datetime')


class OneOf:
    """General descriptor for stocks"""
    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if value in set(tickers):
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError("value must be on of 'FDX', 'GOOGL', 'XOM', 'KO', 'NOK', 'MS', 'IBM'")


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
            raise ValueError('value must be >= 1 and Type pd.Timedelta')


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
    """All Investments"""
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
        self.days_year = int((self.end_date - self.start_date).days / 360)

    def return_on_investment(self):
        return (self.value.iloc[-1, 0] / self.pv) - 1

    def total_return(self):
        return self.value.iloc[-1, 0] - self.pv


class Bonds(Investment):
    """All Bonds"""
    min_price = Monetary('min_price')
    min_period = Period('min_period')

    def __init__(self, period, pv, rate, start_date=start, min_price=0.0, min_period=pd.DateOffset(years=1)):
        super(Bonds, self).__init__(period, pv, start_date)
        if self.pv < min_price:  # Ensure that pv is always bigger than min_price
            raise AttributeError('pv should be >= %s' % min_price)
        else:
            self._min_price = min_price
        # Ensure that period is always bigger than min_period
        if (start_date + self.period) < (start_date + min_period):
            raise AttributeError('period should be >= %s' % min_period)
        else:
            self._min_period = min_period
        self.rate = rate
        # Transform interest rate into pd.Series and
        # ensure that pd.Series length is equal to the number of days in the period.
        if not isinstance(self.rate, pd.Series):
            total_days = (self.end_date - self.start_date).days
            self.rate = pd.Series(itertools.repeat((1 + self.rate) ** (1 / (total_days/self.days_year)) - 1,
                                                   total_days))

    @classmethod
    def short(cls, period, pv, start_date=start):
        min_price, min_period, rate = 250, pd.DateOffset(years=2), 0.015
        bond = cls(period, pv, rate, start_date, min_price, min_period)
        return bond

    @classmethod
    def long(cls, period, pv, start_date=start):
        min_price, min_period, rate = 1000, pd.DateOffset(years=5), 0.03
        bond = cls(period, pv, rate, start_date, min_price, min_period)
        return bond

    def cash_flow(self, end_date=None):
        """Calculates the value attribute and returns the bond cash flow for a given date or entire period"""
        cf = pd.DataFrame({'value': (1 + self.rate).cumprod() * self.pv})
        date = pd.date_range(self.start_date, end=self.end_date, freq="D", closed='left')
        cf = cf.set_index(date)
        self.value = cf
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
    name = OneOf('name')

    def __init__(self, period, name, num_stocks, start_date):
        self.period = period
        self.start_date = stocks_date(start_date)
        self.end_date = stocks_date(self.start_date + self.period)
        self.name = name
        self.num_stocks = num_stocks
        self.price = stocks_df.loc[self.start_date:self.end_date, self.name]
        self.pv = self.price.iloc[0] * self.num_stocks
        self.value = pd.DataFrame({'value': self.price * self.num_stocks})

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
