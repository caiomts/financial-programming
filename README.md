# Investors Simulation

Programming exercise. Modelling three types of investors with two types of investments.

* Aggressive only invests in stocks;
* Defensive only in bonds;
* Mixed combines both.

## Description

The project contains one main script (investor_simulator.py) with objects and functions.
The functional objects are: Bonds, Stocks, Investor, Portfolio.
All objects have attributes and methods. Attributes that are inputted have defined class to ensure variables behavior.

Bonds and Stocks are subclass of Investment, some attributes and methods are inherited. 

"Investor" is a namedtuple with mode (aggressive, defensive, mixed) and budget.
Modes are functions called by Portfolio to build the investment portfolio following
investor characteristics and a given period.

## Assumptions

Stocks: ['FDX', 'GOOGL', 'XOM', 'KO', 'NOK', 'MS', 'IBM']
Bonds: Short (2yo 1.5% p.a. min price:250); Long (5yo 3.0% p.a. min price:1000)

####Portfolio allocation: 
**Defensive**: Picks randomly a long or short bond, as long as it has > 1000 and then
allocate the rest in short.  
**Aggressive**: Picks randomly a stock and an amount [0, N] where N <= Budget. 
Repeat it until budget < 100.  
**Mixed**: Picks randomly, according to weights, Stock or Bond and for each try, follows the same
attempt, follows the same rules as above.

## Getting Started

Save the main script (investor_simulator.py) into the working directory and import as a package or try some simulations
[here!](https://share.streamlit.io/caiomts/financial-programming/sim_streamlit.py)


### Examples and Simulations

- p1_short_long_bonds.py - Bonds manipulations
- p2_stocks.py - Stocks manipulations
- p3_portfolios.py - Investor and Portfolio manipulations
- Simulations.py - Portfolio simulations
- Simulation_bonus.py - Other simulations

## Author

Caio Mescouto Terra de Souza

>caio.mescouto@gmail.com

## Version History

* 0.1
    * Initial Release - March 12, 2021.
  
* 1.0
  * Web app Release - April 05, 2021.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

* README template: [@DomPizzie](https://gist.github.com/DomPizzie/7a5ff55ffa9081f2de27c315f5018afc)
