import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, t
from scipy.optimize import fsolve
from numpy.linalg import matrix_power
from datetime import datetime

# set the 1-year to 7-year time horizon
years = np.arange(1, 8)

# ========================================
# Model 1: The CreditMetrics Markov Chain
# ========================================
# Raw S&P 1-Year Matrix (exluding 'NR' column)
raw_matrix_1yr = np.array([
    [87.28, 8.91,  0.51,  0.03,  0.10,  0.03,  0.05,  0.00], # AAA
    [0.44,  87.81, 7.45,  0.43,  0.05,  0.06,  0.02,  0.02], # AA
    [0.02,  1.52,  89.57, 4.52,  0.22,  0.09,  0.01,  0.04], # A (TD Bank)
    [0.00,  0.07,  3.07,  87.38, 3.12,  0.38,  0.09,  0.13], # BBB
    [0.01,  0.02,  0.10,  4.37,  78.89, 6.13,  0.49,  0.55], # BB
    [0.00,  0.02,  0.05,  0.14,  4.43,  75.15, 4.76,  2.87], # B
    [0.00,  0.00,  0.07,  0.12,  0.38,  13.08, 45.00, 26.12]  # CCC/C
])

# normalize rows and append 'Default' absorbing state
row_sums = raw_matrix_1yr.sum(axis=1)
norm_matrix = raw_matrix_1yr / row_sums[:, np.newaxis]
D_row = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]])
M = np.vstack([norm_matrix, D_row])

# calculate the Markov cumulative probability of default for TD
cm_pd_curve = []
for yr in years:
    M_t = matrix_power(M, yr)
    cum_pd = M_t[2, 7] # row 2 ('A'), Col 7 ('D')
    cm_pd_curve.append(cum_pd * 100)

# ==========================================================
# Model 2: The Merton Term Structure (KMV) with Growing Debt
# ==========================================================
# hardcoded variables from Merton_KMV_model.py
V = 1691810824877.19
sigma_V = 0.0194
D = 1537415500000.00
r = 0.04
gamma = 0.04 # debt grows at 4% per year, neutralizies asset drift

# calculate default probability over time
merton_pd_curve = []
for yr in years:
    # effective drift is now (r - gamma) + 0.5 * sigma_V^2
    # b/c r == gamma, the positive drift canceling out prevents the PD from dropping
    d1 = (np.log(V / D) + (r - gamma + 0.5 * sigma_V**2) * yr) / (sigma_V * np.sqrt(yr))
    d2 = d1 - sigma_V * np.sqrt(yr)
    
    # calculate PD using the fat-tailed t-distribution
    pd = norm.cdf(-d2)
    merton_pd_curve.append(pd * 100)

# ==========================================
# Model 3: Empirical S&P Data (Raw Matrices)
# ==========================================
# the full empirical matrices (including NR column)
sp_matrix_3yr = np.array([
    [65.99, 21.83, 2.30,  0.31,  0.21,  0.08,  0.10,  0.13,  9.04],
    [1.02,  68.34, 17.55, 1.81,  0.30,  0.19,  0.02,  0.11,  10.66],
    [0.05,  3.45,  72.80, 10.39, 0.95,  0.33,  0.07,  0.19,  11.77], # A
    [0.01,  0.20,  7.52,  68.33, 6.15,  1.28,  0.22,  0.67,  15.61],
    [0.01,  0.04,  0.38,  10.02, 50.89, 10.57, 1.09,  3.11,  23.91],
    [0.00,  0.02,  0.13,  0.58,  8.76,  43.32, 5.35,  10.46, 31.38],
    [0.00,  0.00,  0.08,  0.39,  1.31,  16.33, 10.74, 41.46, 29.99]
])

sp_matrix_5yr = np.array([
    [50.06, 28.56, 4.75,  0.86,  0.23,  0.16,  0.08,  0.34,  14.97],
    [1.28,  53.81, 23.60, 3.17,  0.49,  0.32,  0.04,  0.28,  17.01],
    [0.06,  4.44,  60.52, 13.58, 1.56,  0.52,  0.11,  0.40,  18.82], # A
    [0.02,  0.32,  9.70,  55.69, 6.97,  1.74,  0.29,  1.38,  23.88],
    [0.01,  0.06,  0.76,  11.78, 35.65, 10.54, 1.09,  5.85,  34.28],
    [0.01,  0.02,  0.16,  1.10,  8.94,  26.39, 3.50,  15.92, 43.96],
    [0.00,  0.00,  0.07,  0.51,  2.28,  11.75, 2.70,  46.57, 36.11]
])

sp_matrix_7yr = np.array([
    [38.53, 32.59, 6.80,  1.51,  0.23,  0.18,  0.10,  0.49,  19.56],
    [1.35,  42.94, 27.04, 4.21,  0.64,  0.32,  0.03,  0.46,  23.02],
    [0.06,  4.82,  51.38, 15.29, 1.99,  0.62,  0.11,  0.69,  25.05], # A
    [0.03,  0.42,  10.79, 46.84, 6.92,  1.91,  0.29,  2.10,  30.71],
    [0.00,  0.06,  1.02,  12.12, 26.65, 9.45,  0.88,  8.28,  41.54],
    [0.00,  0.01,  0.21,  1.48,  7.93,  17.45, 2.00,  19.95, 50.97],
    [0.00,  0.00,  0.18,  0.77,  3.07,  6.84,  2.11,  49.23, 37.79]
])
# extract PDs dynamically from the matrices
sp_years = [1, 3, 5, 7]
sp_empirical_pds = [
    raw_matrix_1yr[2, 7], # 1-Year 'A' row, 'D' col
    sp_matrix_3yr[2, 7],  # 3-Year 'A' row, 'D' col
    sp_matrix_5yr[2, 7],  # 5-Year 'A' row, 'D' col
    sp_matrix_7yr[2, 7]   # 7-Year 'A' row, 'D' col
]

# ==========================================
# Plotting the Presentation Graph
# ==========================================
# generate matplotlib fgiure
plt.figure(figsize=(10, 6))

# plot continuous curves
plt.plot(years, cm_pd_curve, marker='o', color='darkorange', linewidth=2, label='CreditMetrics (Markov Chain)')
plt.plot(years, merton_pd_curve, marker='s', color='deeppink', linewidth=2, label='Merton Model (KMV)')

# plot the empirical stars
plt.scatter(sp_years, sp_empirical_pds, marker='*', s=250, color='gold', edgecolor='black', zorder=5, label='S&P Empirical Data (Table 21)')

# formatting
plt.title('TD Bank: Cumulative Probability of Default Term Structure', fontsize=14, fontweight='bold')
plt.xlabel('Years into the Future', fontsize=12)
plt.ylabel('Cumulative Probability of Default (%)', fontsize=12)
plt.ylim(bottom=0) 
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc='upper left', fontsize=11)
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(decimals=3))
plt.tight_layout()
plt.savefig('TD_Bank_PD_Term_Structure.png', dpi=300, bbox_inches='tight')
plt.show()

# ======================================
# Exact YTM Calculation (TD CAD Bond)
# ======================================
clean_price = 101.10
face_value = 100
annual_coupon = 4.21
coupon_payment = annual_coupon / 2 

settlement_date = datetime(2026, 3, 23)
last_coupon_date = datetime(2025, 12, 1)
next_coupon_date = datetime(2026, 6, 1)

# Calculate exact Accrued Interest
days_since_last_coupon = (settlement_date - last_coupon_date).days 
days_in_period = (next_coupon_date - last_coupon_date).days
accrued_interest = coupon_payment * (days_since_last_coupon / days_in_period)
dirty_price = clean_price + accrued_interest

# Calculate exact time in years (t) until each future cash flow
# Note: Separating the final coupon (May 31) from Principal (June 1)
dates_of_cash_flows = [
    datetime(2026, 6, 1),
    datetime(2026, 12, 1),
    datetime(2027, 6, 1)   
]

t_flows = np.array([(date - settlement_date).days / 365.25 for date in dates_of_cash_flows])
cash_flows = np.array([coupon_payment, coupon_payment, face_value + coupon_payment])

# Define the equation to drive to zero
def ytm_equation(y, t_array, cf_array, target_price):
    present_value = np.sum(cf_array * np.exp(-y * t_array))
    return present_value - target_price

# Run the numerical solver
exact_ytm = fsolve(ytm_equation, 0.03, args=(t_flows, cash_flows, dirty_price))[0]

# ======================================
# Market-Implied Probability of Default
# ======================================
# Define the baseline assumptions
goc_1yr_yield = 0.0276  # 2.76% from Bank of Canada
recovery_rate = 0.45    # 45% Standard Senior Unsecured Assumption

# Calculate the Credit Spread and the PD
credit_spread = exact_ytm - goc_1yr_yield
market_implied_pd = credit_spread / (1 - recovery_rate)

# Output the rigorous pricing breakdown and final PD
print("\n==== Exact Continuous YTM Calculation ====")
print(f"Clean Price:       ${clean_price:.2f}")
print(f"Accrued Interest:  ${accrued_interest:.4f}")
print(f"Dirty Price:       ${dirty_price:.4f}")
print(f"Exact Continuous YTM: {exact_ytm:.4%}")

print("\n==== Market-Implied Yield Spread Model ====")
print(f"1-Year GoC Risk-Free Rate: {goc_1yr_yield:.2%}")
print(f"Exact Continuous TD Yield: {exact_ytm:.2%}")
print(f"Calculated Credit Spread:  {credit_spread * 10000:.0f} bps ({credit_spread:.2%})")
print(f"Assumed Recovery Rate:     {recovery_rate:.0%}")
print("-" * 43)
print(f"Market-Implied 1-Year PD:  {market_implied_pd:.2%}")