# Investors Simulation

Three types of investors $\times$ two types of investments = five types of investment portfolio.

## Structure

* Investment Portfolio as an object that has one investor, term and X.
* Methods 
    * Return

    
* Bonds
    * Term; Amount; min_price; min_term; i
    * **Function** for compounded interest in a cert time 
    * Plot of minimum investment
    

* Investor is a namedtuple with Mode, Budget (namedtuple)
    * Modes are functions
        * Defensive invests only in bonds (50-50) as long as he has enough money to invest in short.
        * Aggressive invests only in stocks. Randomly chosen until less than 100$ available
        * Mixed X% Defensive + (X-1)% Aggressive each try. Try only if budget > Short term Bond.
    
* Stocks
    * Term
    * Amount
    * Stock name
    * start date
    * end date
    * plot

