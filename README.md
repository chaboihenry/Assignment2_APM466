# Corporate Credit Risk Term Structure Analysis 📈
**The Toronto-Dominion Bank (TD): A Multi-Model Perspective (2026-2033)**

---

## 📄 Executive Summary (APM466 Assignment 2)
This study evaluates the creditworthiness of TD Bank across a 7-year horizon by juxtaposing three distinct quantitative frameworks. While the **CreditMetrics (Markov)** model provides a stable, ratings-based historical baseline (PD < 0.7%), the **Structural Merton/KMV** model reveals a theoretical "Leverage Trap," projecting an inflated risk profile (PD ~3.75%) due to the bank's high leverage ratio and the square-root-of-time scaling of uncertainty. 

The **Market-Implied (Reduced-Form)** model serves as the real-time "truth," pricing a 1-year PD of **1.48%**. This suggests that while structural models are mathematically sound, they often fail to account for the "Too Big to Fail" regulatory backstops and proactive capital management inherent in Systemically Important Financial Institutions (SIFIs).

---

## 🧠 Models Implemented

### 1. The CreditMetrics Model (Markov Chain)
* **Mechanism:** Utilizes a first-order Markov process applied to S&P Global's historical 1-year transition matrices.
* **Engineering:** Includes algorithmic normalization of "Not Rated" (NR) categories and the implementation of a continuous "Default" absorbing state to calculate cumulative transition probabilities ($M^t$).
* **Data Evidence:** [See Ratings_Data/](Evidence_Screenshots/Ratings_Data/)

### 2. The Merton/KMV Model (Structural)
* **Mechanism:** Treats corporate equity as a European call option on the firm's assets using the Black-Scholes-Merton framework.
* **Engineering:** Solves a non-linear system of equations to back-out latent Asset Value ($V$) and Volatility ($\sigma_V$). Implements a dynamic debt barrier ($\gamma$) to neutralize unrealistic asset drift over long horizons.
* **Insight:** Exposes the **"Bank Leverage Trap."** In structural models, uncertainty scales by $\sqrt{T}$. For highly levered banks (~90% debt), this math forces the asset value to eventually "wander" into the debt barrier over long horizons, even if the bank is currently healthy.
* **Data Evidence:** [See Balance_Sheet/](Evidence_Screenshots/Balance_Sheet/)

### 3. Market-Implied Yield Spread (Reduced-Form)
* **Mechanism:** Extracts the real-time default probability priced in by live fixed-income traders.
* **Engineering:** Uses numerical root-finding (`scipy.optimize.fsolve`) to calculate the exact continuous Yield to Maturity (YTM) of a CAD-denominated TD corporate bond, accounting for exact day-count conventions and accrued interest.
* **Data Evidence:** [See Market_Data/](Evidence_Screenshots/Market_Data/)

---

## 📊 Results & Visualization
The term structure below illustrates the divergence between historical rating stability and theoretical structural risk.

![Cumulative PD Term Structure](Results/TD_Bank_PD_Term_Structure.png)

## 🛠️ Tech Stack
* **Python 3.x:** `NumPy`, `SciPy`, `Matplotlib`, `yfinance`.
* **Methodology:** Numerical optimization, Matrix exponentiation, and Continuous discounting.

---

## 👨‍💻 Author
**Henry Vianna**
* BSc Honours (Mathematical Applications in Economics and Finance) | University of Toronto
