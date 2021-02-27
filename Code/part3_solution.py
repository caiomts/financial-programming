import investor_sim_objects as investso
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

period = pd.DateOffset(years=5)

defensive = [investso.Portfolio(investso.defensive, 5000, period)]
aggressive = [investso.Portfolio(investso.aggressive, 5000, period)]
mixes = [investso.Portfolio(investso.mixed, 5000, period, recalculate='y')]
