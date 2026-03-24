# Use the Merton/KMV model to calculate the default probability of TD Bank over time (1 year)
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm 
from scipy.optimize import fsolve
from scipy.stats import t

# market data configuration and model constraints
ticker_symbol = 'TD.TO'
start_date = '2025-03-20'
end_date = '2026-03-20'
trading_days = 252
r = 0.04 # 4% risk-free rate
T = 1.0 # 1-year time horizion

# hardcoded balance sheet data from TD's 2025 form 40-F (in raw CAD)
short_term_debt = (43795 + 221150) * 1e6 # Repos + Securities sold short
long_term_debt = 10733 * 1e6 # subordinated notes
total_deposits = 1267104 * 1e6 # customer deposits

# fetch market equity data programmatically
td_stock = yf.Ticker(ticker_symbol)
historical_data = td_stock.history(start=start_date, end=end_date)

# calculate Market Equity (E) and annualized Volatility (Sigma_E)
shares_outstanding = td_stock.info.get('sharesOutstanding', 1_689_495_505)
current_price = historical_data['Close'].iloc[-1]
E = current_price * shares_outstanding

historical_data['Daily_Return'] = historical_data['Close'].pct_change()
simga_E = historical_data['Daily_Return'].std() * np.sqrt(trading_days)

# define customized Bank Debt barrier (D)
D = short_term_debt + (0.5 * long_term_debt) + total_deposits

# define the system of equations for the numerical solver
def merton_system(variables, E_market, sigma_E_market, D, r, T):
    V, sigma_V = variables

    # calculate d1 and d2
    d1 = (np.log(V/D) + (r + 0.5 * sigma_V**2) * T) / (sigma_V * np.sqrt(T))
    d2 = d1 - sigma_V * np.sqrt(T)

    # the two equations we want to force to zero
    eq1 = (V * norm.cdf(d1) - np.exp(-r * T) * D * norm.cdf(d2)) - E_market
    eq2 = ((V / E_market) * norm.cdf(d1) * sigma_V) - sigma_E_market

    return [eq1, eq2]

# run fsolve with inital guesses (V roughly equals E+D, sigma_V roughly sigma_E)
inital_guess = [E + D, simga_E]
V_solved, sigma_V_solved = fsolve(merton_system, inital_guess, args=(E, simga_E, D, r, T))

# calculate final distance to default (DD)
d1_solved = (np.log(V_solved / D) + (r + 0.5 * sigma_V_solved**2) * T) / (sigma_V_solved * np.sqrt(T))
DD = d1_solved

# output the core metrics
print("\n==== Core Model Outpus =====")
print(f"Market Value of Equity (E): ${E:,.2f}")
print(f"Custom Bank Debt Barrier (D): ${D:,.2f}")
print(f"Annualized Equity Volatility (sigma_E): {simga_E:.4f}")
print("-" * 30)
print(f"Solved Asset Value (V): ${V_solved:,.2f}")
print(f"Solved Asset Volatility (sigma_V): {sigma_V_solved:.4f}")
print(f"Distance to Default (DD): {DD:.4f}")

# calculate Theoretical Merton PD, uses standard normal distribution func
merton_pd = norm.cdf(-DD)

# calculate the Empirical KMV-style PD proxy
# uses t-distribution to account for real-world "fat-tails" in market defaults
df_fat_tails = 4 # degrees of freedom for distribution proxy
kmv_pd = t.cdf(-DD, df=df_fat_tails)

# output of final 1-year default probabilities
print("\n==== 1-Year Probability of Default (PD) ====")
print(f"Theoretical Merton PD: {merton_pd:.10%}")
print(f"Empirical KMV Proxy PD: {kmv_pd:.10%}")

# note how empirical proxy predicts significantly higher probability of default than
# the pure theoretical model, even for a safe bank
