# Investors Simulation

Programming exercise. Modelling three types of investors with two types of investments.

* Aggressive only invests in stocks;
* Defensive only in bonds;
* Mixed combines both.

## Description

The project contains one main script (investor_simulator.py) with objects and functions.
The functional objects are: Bonds, Stocks, Investor, Portfolio.
All objects have attributes and methods. Attributes that are inputted have defined class to ensure variables behavior.

"Bonds" has as main Attributes: 
  - period(pandas.DataOffset)
  - pv(>= 0)
  - rate(float, pd.Series)
  - start_date(datetime)
  - end_date(datetime)
  - min_price(>= 0)
  - min_period(pandas.DataOffset)
  - value
and main Methods:
  - short, long - works as shortcut to create bonds with specifics characteristics.
  - return_on_investment
  - total_return
  - cash_flow
  - compound_rate

"Stocks" has as main Attributes:
  - start_date 
  - end_date
  - name ('FDX', 'GOOGL', 'XOM', 'KO', 'NOK', 'MS', 'IBM')
  - num_stocks (int)
  - price
  - pv
  - value
and main Methods:
  - return_on_investment
  - total_return
  - return_on_stock
  - get_price

Bonds and Stocks are subclass of Investment, some attributes and methods are inherited. 

"Investor" is a namedtuple with mode (aggressive, defensive, mixed) and budget.
Modes are functions called by Portfolio to build the investment portfolio following
investor characteristics and a given period.

"Portfolio" has as main attributes:
  - mode (comes from the Investor)
  - budget (comes from the Investor)
  - period
  - start_date
  - recalculate (bool)
  - weights [stocks, bonds]
-  investments

## Getting Started

Save the main script (investor_simulator.py) into the working directory and import as a package.


### Dependencies

#### Packages:
- pandas
- itertools
- pandas_datareader.data
- datetime
- random
- math
- collections

## Author

Caio Mescouto Terra de Souza

* caio.mescouto-terra-de-souza@tsm-education.fr

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

* README template: [@DomPizzie](https://gist.github.com/DomPizzie/7a5ff55ffa9081f2de27c315f5018afc)
