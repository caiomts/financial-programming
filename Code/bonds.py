import pandas as pd
import itertools


class Monetary:
    """General descriptor for monetary entries"""

    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if (value is None) or (value >= 0):
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError('value must be >= 0')


class TimeDelta:
    """General descriptor for period"""

    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if isinstance(value, pd.Timedelta) and (value >= pd.Timedelta('1 day')):
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


class Investment:
    """All Investment"""
    period = TimeDelta('period')
    pv = Monetary('pv')
    fv = Monetary('fv')
    rate = Rates('rate')

    def __init__(self, period, pv):
        self.period = period
        self.pv = pv
        self.fv = None
        self.rate = None

    def return_on_investment(self):
        return (self.fv / self.pv) - 1

    def total_return(self):
        return self.fv - self.pv


class Bonds(Investment):
    """All Bonds"""
    min_price = Monetary('min_price')
    min_period = TimeDelta('min_period')

    def __init__(self, period, pv, rate, min_price=0.0, min_period=pd.Timedelta('1 day'), day_convention=360):
        super(Bonds, self).__init__(period, pv)
        if self.pv < min_price:  # Ensure that pv is always bigger than min_price
            raise AttributeError('pv should be >= %s' % min_price)
        else:
            self._min_price = min_price
        if self.period < min_period:  # Ensure that period is always bigger than min_period
            raise AttributeError('period should be >= %s' % min_period)
        else:
            self._min_period = min_period
        self.day_convention = day_convention
        self.rate = rate
        # Transform interest rate into pd.Series and
        # ensure that pd.Series length is equal to the number of days in the period.
        if not isinstance(self.rate, pd.Series) or len(self.rate) != self.period.days:
            self.rate = pd.Series(itertools.repeat((1 + self.rate) ** (1 / self.day_convention) - 1, self.period.days))
        self.fv = self.pv * (1 + compound_rate(self.rate))

    @classmethod
    def short(cls, period, pv):
        min_price, min_period, rate = 250, pd.Timedelta('720 days'), 0.015
        bond = cls(period, pv, rate, min_price, min_period)
        return bond

    @classmethod
    def long(cls, period, pv):
        min_price, min_period, rate = 1000, pd.Timedelta('1800 days'), 0.03
        bond = cls(period, pv, rate, min_price, min_period)
        return bond

    def bond_cash_flow(self, start_date='2000-01-01', end_date=None):
        """"""
        cash_flow = pd.DataFrame({'Date': pd.date_range(start_date, periods=self.period.days, freq="D"),
                                  'daily_rate': self.rate,
                                  'compound_rate': (1 + self.rate).cumprod() - 1,
                                  'daily_fv': (1 + self.rate).cumprod() * self.pv}).set_index('Date')
        if end_date is None:
            return cash_flow
        else:
            return cash_flow[cash_flow.index <= end_date]


# General functions. All this functions fits more than one type of Investment


def compound_rate(rate):
    """Compound rates"""
    return (1 + rate).prod() - 1


x = Bonds.long(pd.Timedelta('1800 days'), 2000)

y = x.bond_cash_flow().resample('Y').asfreq()

print(x.bond_cash_flow(end_date='2003-12-31').resample('Y').asfreq())
print(x.bond_cash_flow())
