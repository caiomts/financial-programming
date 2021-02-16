import pandas as pd


class Monetary:
    """General descriptor for monetary entries"""
    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if value >= 0:
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError('value must be >= 0')


class TimeDelta:
    """General descriptor for period"""
    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if isinstance(value, pd.Timedelta) and value >= pd.Timedelta('1 day'):
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError('value must be >= 1 and Type pd.Timedelta')


class Rates:
    """General descriptor for rates"""
    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if isinstance(value, float or pd.Series):
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
        self.fv
        self.rate

    def return_on_investment(self):
        return (self.fv / self.pv) - 1

    def total_return(self):
        return self.fv - self.pv


class Bonds(Investment):
    """All Bonds"""
    min_price = Monetary('min_price')
    min_period = Monetary('min_period')

    def __init__(self, period, pv, rate, min_price=0.0, min_period=0.0):
        super(Bonds, self).__init__(period, pv)
        if self.pv < min_price:     # Ensure that pv is always bigger than min_price
            raise AttributeError('pv should be >= %s' % min_price)
        else:
            self._min_price = min_price
        if self.period < min_period:    # Ensure that period is always bigger than min_period
            raise AttributeError('period should be >= %s' % min_period)
        else:
            self._min_period = min_period

    @classmethod
    def short(cls, period, pv):
        min_price, min_period, rate = 250, 2, 0.015
        bond = cls(period, pv, min_price, min_period, rate)
        return bond

    @classmethod
    def long(cls, period, pv):
        min_price, min_period, rate = 1000, 5, 0.03
        bond = cls(period, pv, min_price, min_period, rate)
        return bond


def compounded_rate(rate):
    """Compound rate annually"""
    return (1 + rate).prod() - 1


x = Investment(pd.Timedelta('1 day'), 100.10)

print(x.period, x.pv, x.rate, x.fv)

print(compounded_rate(pd.Series([0.015, 0.015])))


