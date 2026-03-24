# Corporate Credit Risk Term Structure Analysis 📈

An end-to-end quantitative evaluation of the 1-to-7-year Probability of Default (PD) for The Toronto-Dominion Bank (TD). This project was developed to juxtapose theoretical structural models against empirical ratings data and live market-implied bond yields.

## 🎯 Executive Summary
This repository contains the mathematical engines and visualization scripts required to project corporate default risk across multiple time horizons. By comparing three distinct quantitative frameworks, this project highlights the divergence between balance-sheet-derived structural risk and the reality of market/regulatory interventions in the Canadian banking sector.

## 🧠 Models Implemented

### 1. The CreditMetrics Model (Markov Chain)
* **Mechanism:** Utilizes a first-order Markov process applied to S&P Global's historical 1-year transition matrices.
* **Engineering:** Includes algorithmic normalization of "Not Rated" (NR) categories and the implementation of a continuous "Default" absorbing state to calculate cumulative transition probabilities ($M^t$).
* **Insight:** Demonstrates the theoretical baseline while acknowledging the empirical reality of "Ratings Momentum" observed in multi-year S&P data.

### 2. The Merton/KMV Model (Structural / First Passage Time)
* **Mechanism:** Treats corporate equity as a barrier option on the firm's assets using Black-Cox First Passage Time mathematics.
* **Engineering:** Implements a dynamic debt barrier ($\gamma$) to neutralize unrealistic asset drift over long horizons. Substitutes the standard normal distribution with a Student's t-distribution (df=4) to accurately proxy the empirical "fat tails" observed in the KMV framework.
* **Insight:** Exposes the "Bank Leverage Trap"—illustrating how standard structural diffusion models artificially inflate long-term default risk for highly levered, systemically important financial institutions (SIFIs).

### 3. Market-Implied Yield Spread (Reduced-Form)
* **Mechanism:** Extracts the real-time default probability priced in by live fixed-income traders.
* **Engineering:** Uses numerical root-finding (`scipy.optimize.fsolve`) to calculate the exact continuous Yield to Maturity (YTM) of a CAD-denominated TD corporate bond, accounting for exact day-count conventions and accrued interest, benchmarked against the Bank of Canada risk-free rate.

## 📊 Visualizations
*(Upload your `TD_Bank_PD_Term_Structure.png` to the repo and link it here)*
![Cumulative PD Term Structure](link_to_your_image_here.png)

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Libraries:** `NumPy` (Matrix exponentiation, array operations), `SciPy` (Numerical optimization, statistical distributions), `Matplotlib` (Data visualization), `Datetime` (Day-count convention handling).

## 👨‍💻 Author
**Henry Vianna**
* BSc Honours (Mathematical Applications in Economics and Finance) | University of Toronto
* Based in Toronto, ON
* *Quantitative Finance | Algorithmic Trading | Data Science*
