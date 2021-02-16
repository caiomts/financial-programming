# Investors Simulation

Three types of investors $\times$ two types of investments = five types of investment portfolio.

## Structure

* Investment
  * Bonds
  * Stocks
  * ...
* Investor
  * Defensive
  * Aggressive
  * Mixed ($X\times Defensive + (X-1)\times Aggressive\quad 0 < X < 1$)
* Investment Portfolio
    * Investor
    * n-Investments

## Investment

Investment is a high hierarchical object.

### Defining an Investment

Any investment is a relationship between Present and Future Values.
This relationship is a mathematical function with dependent variable (FV),
and independents variables (PV, Rate and Period). An investment is characterized
by its own mathematical function. 
    
$$f(PV, rate, period)\rightarrow FV$$

Sometimes the function is unknown, or the rate varies along the period.  

#### Investment Attributes

* PV (float > 0)
* Period (timedelta)
* FV (float >0)
* Rate = (float or pd.Series)

#### General Functions

All Investments have at least the following methods.
However, those methods are valid if and only if there is a function associated
with the investment. It's true only if subclasses of investment
  
* Return on Investment (ROI)
$$FV/PV - 1$$
  
* Total Return
$$FV - PV$$

### Bonds

Bonds are one type of investment and inherit attributes and Methods from it.

#### Bonds Attributes

* Min PV
* Min Period
* 



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

