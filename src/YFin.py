import yfinance as yf
import pandas as pd


def get_custom_tickers():
    """Allows user to input custom tickers."""
    while True:
        try:
            num_tickers = int(input("How many tickers would you like to analyze? "))
            if num_tickers <= 0:
                print("Please enter a positive number.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    print(f"\nEnter {num_tickers} ticker symbols (comma-separated or one per line):")
    print("Example: AAPL, MSFT, GOOGL")
    
    user_input = input().strip()
    
    # Try parsing as comma-separated first
    if ',' in user_input:
        tickers = [t.strip().upper() for t in user_input.split(',')]
    else:
        # Otherwise treat as single line with spaces or collect multiple lines
        tickers = [user_input.strip().upper()]
        
        if len(tickers) < num_tickers:
            print(f"You've entered {len(tickers)} ticker(s). Enter the remaining {num_tickers - len(tickers)}:")
            for i in range(num_tickers - len(tickers)):
                ticker = input(f"Ticker {len(tickers) + i + 1}: ").strip().upper()
                if ticker:
                    tickers.append(ticker)
    
    # Ensure we have the requested number
    tickers = tickers[:num_tickers]
    print(f"\nSelected tickers: {', '.join(tickers)}\n")
    return tickers


# Check if running as main script
if __name__ == "__main__":
    tickers = get_custom_tickers()
else:
    # Default tickers when imported by other modules
    tickers = ["AAPL", "MSFT", "AMZN", "GOOGL", "META",
               "TSLA", "NVDA", "JPM", "V", "MA",
               "NFLX", "ADBE", "INTC", "AMD", "CRM",
               "KO", "PEP", "DIS", "NKE", "WMT"]

results = []

for ticker_symbol in tickers:
    stock = yf.Ticker(ticker_symbol)

    info = stock.info or {}  # avoid NoneType issues

    # Income statement
    income_stmt = stock.income_stmt
    cash_flow = stock.cash_flow
    balance_sheet = stock.balance_sheet

    # Safely extract values
    try:
        net_income = income_stmt.loc["Net Income"].iloc[0]
    except:
        net_income = None

    try:
        total_equity = balance_sheet.loc["Total Stockholder Equity"].iloc[0]
    except:
        total_equity = None

    try:
        free_cash_flow = cash_flow.loc["Free Cash Flow"].iloc[0]
    except:
        free_cash_flow = None

    # Build dictionary
    data = {
        "ticker": ticker_symbol,
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "price_to_book": info.get("priceToBook"),
        "price_to_sales": info.get("priceToSalesTrailing12Months"),
        "ev_to_ebitda": info.get("enterpriseToEbitda"),
        "peg_ratio": info.get("pegRatio"),
        "roe": (net_income / total_equity) if (total_equity not in [None, 0]) else None,
        "revenue_growth": info.get("revenueGrowth"),
        "debt_to_equity": info.get("debtToEquity"),
        "free_cash_flow": free_cash_flow,
    }

    results.append(data)

# Convert to a DataFrame for easy viewing
df = pd.DataFrame(results)
print(df)
