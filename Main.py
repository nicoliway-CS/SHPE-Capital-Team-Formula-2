import yfinance as yf
import pandas as pd

meta = yf.Ticker("META")

print("Trailing PE:", meta.info.get("trailingPE", "N/A"))

# ----- Income Statement -----
income = meta.income_stmt
quarterly_income = meta.quarterly_income_stmt

print("\nTotal Revenue (Annual):")
print(income.loc["Total Revenue"])

# ----- Revenue Growth -----
revenue = income.loc["Total Revenue"]
revenue_growth_yoy = revenue.pct_change(periods=-1) * 100
print("\nRevenue Growth YoY (%):")
print(revenue_growth_yoy)

revenue_q = quarterly_income.loc["Total Revenue"]
revenue_growth_qoq = revenue_q.pct_change(periods=-1) * 100
print("\nRevenue Growth QoQ (%):")
print(revenue_growth_qoq)

# ----- EPS Growth -----
net_income = income.loc["Net Income"]
shares_outstanding = meta.info.get("sharesOutstanding")

if shares_outstanding and not net_income.empty:
    eps = net_income / shares_outstanding
    eps_growth = eps.pct_change(periods=-1) * 100
    print("\nEPS Growth (%):")
    print(eps_growth)
else:
    print("\nEPS Growth: Data not available.")

# ----- Margins -----
gross_profit = income.loc["Gross Profit"]
operating_income = income.loc["Operating Income"]
revenue = income.loc["Total Revenue"]

gross_margin = (gross_profit / revenue) * 100
operating_margin = (operating_income / revenue) * 100
net_margin = (net_income / revenue) * 100

print("\nGross Margin (%):\n", gross_margin)
print("Operating Margin (%):\n", operating_margin)
print("Net Margin (%):\n", net_margin)

# ----- Balance Sheet -----
balance = meta.balance_sheet
print("\nBalance Sheet Rows:", balance.index.tolist())

# Find equity
possible_equity_keys = [
    "Total Stockholder Equity",
    "Stockholders Equity",
    "Total Equity Gross Minority Interest"
]
equity = None
for key in possible_equity_keys:
    if key in balance.index:
        equity = balance.loc[key]
        break

if equity is None:
    print("\nEquity not found in balance sheet.")
else:
    roe = (net_income / equity) * 100
    print("\nReturn on Equity (%):\n", roe)

# ----- Return on Invested Capital (ROIC) -----
ebit = None
for key in ["Operating Income", "EBIT", "Earnings Before Interest and Taxes"]:
    if key in income.index:
        ebit = income.loc[key]
        break

possible_tax_keys = ["Income Tax Expense", "Tax Provision", "Provision for Income Taxes"]
possible_ebt_keys = ["Earnings Before Tax", "Pretax Income", "Income Before Tax"]

tax_expense = None
for key in possible_tax_keys:
    if key in income.index:
        tax_expense = income.loc[key]
        break

ebt = None
for key in possible_ebt_keys:
    if key in income.index:
        ebt = income.loc[key]
        break

if ebt is not None and tax_expense is not None and ebit is not None and equity is not None:
    tax_rate = tax_expense / ebt
    debt = balance.loc["Total Debt"] if "Total Debt" in balance.index else 0
    cash = balance.loc["Cash"] if "Cash" in balance.index else 0
    roic = (ebit * (1 - tax_rate)) / (debt + equity - cash) * 100
    print("\nReturn on Invested Capital (%):\n", roic)
else:
    print("\nROIC: Could not find all required fields (EBIT, tax, or pretax income).")

# ----- Debt-to-Equity Ratio -----
if equity is not None:
    if "Total Debt" in balance.index:
        debt = balance.loc["Total Debt"]
        de_ratio = debt / equity
        print("\nDebt to Equity Ratio:\n", de_ratio)
    else:
        print("\nDebt-to-Equity Ratio: 'Total Debt' not available.")

# ----- Free Cash Flow -----
cashflow = meta.cashflow
if "Total Cash From Operating Activities" in cashflow.index and "Capital Expenditures" in cashflow.index:
    fcf = cashflow.loc["Total Cash From Operating Activities"] - cashflow.loc["Capital Expenditures"]
    market_cap = meta.info.get("marketCap", None)
    if market_cap:
        fcf_yield = (fcf / market_cap) * 100
        print("\nFree Cash Flow:\n", fcf)
        print("Free Cash Flow Yield (%):\n", fcf_yield)
    else:
        print("\nFree Cash Flow Yield: Market cap not available.")
else:
    print("\nFree Cash Flow data not available.")