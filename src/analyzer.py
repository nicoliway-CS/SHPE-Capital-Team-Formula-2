import yfinance as yf
import pandas as pd

def analyze_ticker(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)

    # Check if the ticker is valid
    if not stock.history(period="1d").empty:
        print(f"Analyzing {ticker_symbol}...")
    else:
        print(f"Ticker '{ticker_symbol}' not found or no data available.")
        return

    print("Trailing PE:", stock.info.get("trailingPE", "N/A"))

    # ----- Income Statement -----
    income = stock.income_stmt
    quarterly_income = stock.quarterly_income_stmt

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
    shares_outstanding = stock.info.get("sharesOutstanding")

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
    balance = stock.balance_sheet
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
    cashflow = stock.cashflow
    if "Total Cash From Operating Activities" in cashflow.index and "Capital Expenditures" in cashflow.index:
        fcf = cashflow.loc["Total Cash From Operating Activities"] - cashflow.loc["Capital Expenditures"]
        market_cap = stock.info.get("marketCap", None)
        if market_cap:
            fcf_yield = (fcf / market_cap) * 100
            print("\nFree Cash Flow:\n", fcf)
            print("Free Cash Flow Yield (%):\n", fcf_yield)
        else:
            print("\nFree Cash Flow Yield: Market cap not available.")
    else:
        print("\nFree Cash Flow data not available.")


    results = {
        # --- Identification ---
        "ticker": ticker_symbol,

        # --- Valuation ---
        "market_cap": stock.info.get("marketCap"),
        "trailing_pe": stock.info.get("trailingPE"),
        "forward_pe": stock.info.get("forwardPE"),
        "peg_ratio": stock.info.get("pegRatio"),
        "price_to_book": stock.info.get("priceToBook"),
        "enterprise_value": stock.info.get("enterpriseValue"),

        # --- Growth ---
        "revenue_growth_yoy": revenue_growth_yoy.mean() if 'revenue_growth_yoy' in locals() else None,
        "revenue_growth_qoq": revenue_growth_qoq.mean() if 'revenue_growth_qoq' in locals() else None,
        "eps_growth": eps_growth.mean() if 'eps_growth' in locals() else None,

        # --- Profitability ---
        "gross_margin": gross_margin.mean() if 'gross_margin' in locals() else None,
        "operating_margin": operating_margin.mean() if 'operating_margin' in locals() else None,
        "net_margin": net_margin.mean() if 'net_margin' in locals() else None,
        "roe": roe.mean() if 'roe' in locals() else None,
        "roic": roic.mean() if 'roic' in locals() else None,

        # --- Financial Health ---
        "total_debt": float(balance.loc["Total Debt"].iloc[0]) if "Total Debt" in balance.index else None,
        "de_ratio": de_ratio.mean() if 'de_ratio' in locals() else None,
        "current_ratio": stock.info.get("currentRatio"),
        "quick_ratio": stock.info.get("quickRatio"),

        # --- Cash Flow ---
        "operating_cashflow": float(cashflow.loc["Total Cash From Operating Activities"].iloc[0]) if "Total Cash From Operating Activities" in cashflow.index else None,
        "capital_expenditures": float(cashflow.loc["Capital Expenditures"].iloc[0]) if "Capital Expenditures" in cashflow.index else None,
        "free_cash_flow": fcf.mean() if 'fcf' in locals() else None,
        "fcf_yield": fcf_yield.mean() if 'fcf_yield' in locals() else None,

        # --- Dividend & Return ---
        "dividend_yield": stock.info.get("dividendYield"),
        "payout_ratio": stock.info.get("payoutRatio"),

        # --- Sentiment / Misc. ---
        "beta": stock.info.get("beta"),
        "52_week_high": stock.info.get("fiftyTwoWeekHigh"),
        "52_week_low": stock.info.get("fiftyTwoWeekLow"),
        "target_mean_price": stock.info.get("targetMeanPrice"),
        "recommendation": stock.info.get("recommendationKey"),
    }

    return results


if __name__ == "__main__":
    ticker_to_analyze = input("Enter the stock ticker to analyze: ")
    analyze_ticker(ticker_to_analyze)