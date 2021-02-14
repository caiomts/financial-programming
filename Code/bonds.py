class Quantity:
    """General Descriptor"""
    def __init__(self, storage_name):
        self.storage_name = storage_name

    def __set__(self, instance, value):
        if value >= 0:
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError('value must be >= 0')


class Investment(object):
    """All Investment"""
    term = Quantity('term')
    amount = Quantity('amount')

    def __init__(self, term, amount):
        self.term = term
        self.amount = amount


class Bonds(Investment):
    """All Bonds"""
    min_price = Quantity('min_price')
    min_term = Quantity('min_term')

    def __init__(self, term, amount, min_price=0.0, min_term=0.0, yearly_i=0.0):
        super(Bonds, self).__init__(term, amount)
        self.min_price = min_price
        self.min_term = min_term
        self.yearly_i = yearly_i

    @classmethod
    def short(cls, term, amount):
        min_price, min_term, yearly_i = 250, 2, 0.015
        bond = cls(term, amount, min_price, min_term, yearly_i)
        return bond

    @classmethod
    def long(cls, term, amount):
        min_price, min_term, yearly_i = 1000, 5, 0.03
        bond = cls(term, amount, min_price, min_term, yearly_i)
        return bond



x = Bonds.long(3, 800)


print(x.term, x.amount, x.min_term, x.min_price, x.yearly_i)
