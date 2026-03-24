import pandas as pd
import numpy as np
from scipy.optimize import fsolve
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

# =============================
# 1. Setput and Data ingestion
# =============================
# load TD bond data
df = pd.read_csv("Evidence_Screenshots/Market_Data/td_bond_data.csv")
df['Maturity Date'] = pd.to_datetime(df['Maturity Date'])
df = df.sort_values(by='Maturity Date')

# the obs date used for the Market-Implied PD model
current_date = pd.to_datetime('2026-03-23')
target_col = '2026-03-23'

# Bank of Canada Official Benchmark Yields for March 23, 2026
# mapped to the 1, 2, 3, and 5-year horizons (Python will interpolate year 4)
goc_ttms = np.array([1.0, 2.0, 3.0, 5.0])
goc_spots = np.array([0.0276, 0.0295, 0.0300, 0.0314])

# ==========================================
# 2. Bootstrapping the TD Corporate Spot Curve
# ==========================================
td_ttms = []
td_spots = []

for _, row in df.iterrows():
    # bond characteristics
    ttm = (row['Maturity Date'] - current_date).days / 365.25
    coupon = float(row['Coupon'].strip('%')) / 100
    
    # price formatting
    clean_price = float(row[target_col].strip('%'))
    if clean_price <= 2.0: clean_price = clean_price * 100 
    
    # calculate accrued interest (Assuming previous coupon was roughly 6 months prior)
    # using simplified ACT/365 approximation for the solver
    days_since = (current_date - (row['Maturity Date'] - pd.DateOffset(months=6))).days % 182.5
    if days_since < 0: days_since += 182.5
    accrued = (days_since / 365) * (coupon * 100)
    dirty_price = clean_price + accrued

    # generate future cash flow dates
    cash_flow_times = sorted([ttm - (k*0.5) for k in range(int(np.ceil(ttm*2))) if ttm - (k*0.5) > 0])

    # The Assignment 1 Bootstrapping Solver
    def solve_spot(r):
        total_pv = 0
        for t in cash_flow_times:
            payment = (coupon * 100 / 2) + (100 if t == cash_flow_times[-1] else 0)
            
            if t == ttm:
                rate = r
            else:
                if len(td_ttms) > 1:
                    interp_func = interp1d(td_ttms, td_spots, kind='linear', fill_value="extrapolate")
                    rate = float(interp_func(t))
                else:
                    rate = td_spots[0] if td_spots else r
            
            discount_factor = 1 / (1 + rate/2) ** (2*t)
            total_pv += payment * discount_factor
        
        return total_pv - dirty_price

    # solve and store
    guess = td_spots[-1] if td_spots else 0.03
    r_solution = fsolve(solve_spot, guess)[0]
    td_ttms.append(ttm)
    td_spots.append(r_solution)

# ==========================================
# 3. Plotting the Comparative Spread
# ==========================================
plt.figure(figsize=(10, 6))

# plot the curves
plt.plot(goc_ttms, [r * 100 for r in goc_spots], marker='o', color='forestgreen', linewidth=2, label='Government of Canada (Risk-Free Baseline)')
plt.plot(td_ttms, [r * 100 for r in td_spots], marker='s', color='darkred', linewidth=2, label='TD Bank (Senior Unsecured)')

# gill the credit spread gap visually
# interpolate the GoC curve to match the exact TD maturities for the fill
goc_interp = interp1d(goc_ttms, goc_spots, kind='linear', fill_value='extrapolate')
goc_matched_spots = goc_interp(td_ttms)
plt.fill_between(td_ttms, [r * 100 for r in goc_matched_spots], [r * 100 for r in td_spots], color='salmon', alpha=0.3, label='Implied Credit Spread')

# formatting
plt.title('TD Bank vs. Government of Canada: Yield Curve & Credit Spread', fontsize=14, fontweight='bold')
plt.xlabel('Time to Maturity (Years)', fontsize=12)
plt.ylabel('Spot Rate (%)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc='upper left', fontsize=11)
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(decimals=2))

plt.tight_layout()
plt.savefig('TD_vs_GoC_Credit_Spread.png', dpi=300, bbox_inches='tight')
plt.show()

# print spread output for verification
print("\n==== 1-Year Credit Spread Verification ====")
print(f"TD 1-Year Bootstrapped Spot: {td_spots[0]:.4%}")
print(f"GoC 1-Year Baseline Spot:    {goc_spots[0]:.4%}")
print(f"Calculated Spread:           {(td_spots[0] - goc_spots[0]) * 10000:.0f} bps")


