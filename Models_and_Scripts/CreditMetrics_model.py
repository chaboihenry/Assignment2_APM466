# Use a CreditMetrics-type model to calculate the default probability of TD Bank over time.
import numpy as np
import pandas as pd

# define the rating states (columns & rows)
ratings = ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC/C', 'D', 'NR']

# hardcode the verified S&P 1-year transition matrix (values in &)
# data source: S&P Global Corporate Average Transition Rates (1981-2025)
transition_data = [
    [87.28, 8.91,  0.51,  0.03,  0.10,  0.03,  0.05,  0.00,  3.09],  # AAA
    [0.44,  87.81, 7.45,  0.43,  0.05,  0.06,  0.02,  0.02,  3.73],  # AA
    [0.02,  1.52,  89.57, 4.52,  0.22,  0.09,  0.01,  0.04,  3.99],  # A
    [0.00,  0.07,  3.07,  87.38, 3.12,  0.38,  0.09,  0.13,  5.75],  # BBB
    [0.01,  0.02,  0.10,  4.37,  78.89, 6.13,  0.49,  0.55,  9.44],  # BB
    [0.00,  0.02,  0.05,  0.14,  4.43,  75.15, 4.76,  2.87,  12.59], # B
    [0.00,  0.00,  0.07,  0.12,  0.38,  13.08, 45.00, 26.12, 15.23]  # CCC/C
]

# exclude 'D' & 'NR' from the index b/c companies currently in Default or Not Rated
# don't have standard forward transition probabilities here.
tm_df = pd.DataFrame(transition_data, index=ratings[:-2], columns=ratings)

# define TD Bank's current mapping
td_actual_rating = 'A+'
td_mapped_bucket = 'A' 

# extract the Probability of Default (PD), locate the row for 'A' and col for 'D'
td_pd_percent = tm_df.loc[td_mapped_bucket, 'D']

# output the findings for the 1-page presentation
print("==== CreditMetrics 1-Year Probability of Default =====")
print(f"Target Company: TD Bank")
print(f"Official S&P Senior Debt Rating: {td_actual_rating}")
print(f"Matrix Mapped Bucket: {td_mapped_bucket}")
print("-" * 45)
print(f"1-year Probability of Default (PD): {td_pd_percent}%")

# compare this PD to theoretical Merton PD and empirical KMV proxy PD