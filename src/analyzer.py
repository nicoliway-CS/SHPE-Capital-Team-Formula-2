import yfinance as yf
import json

def get_stock_data(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)

    if stock.history(period="1d").empty:
        return None

    income_stmt = stock.income_stmt
    balance_sheet = stock.balance_sheet
    cash_flow = stock.cashflow
    
    # Safely get values from financials, return 0 if the key doesn't exist.
    total_revenue = income_stmt.loc['Total Revenue'].iloc[0] if 'Total Revenue' in income_stmt.index else 0
    net_income = income_stmt.loc['Net Income'].iloc[0] if 'Net Income' in income_stmt.index else 0
    total_equity = balance_sheet.loc['Total Stockholder Equity'].iloc[0] if 'Total Stockholder Equity' in balance_sheet.index else 0

    data = {
        "ticker": ticker_symbol,
        "trailing_pe": stock.info.get("trailingPE"),
        "forward_pe": stock.info.get("forwardPE"),
        "price_to_book": stock.info.get("priceToBook"),
        "price_to_sales": stock.info.get("priceToSalesTrailing12Months"),
        "ev_to_ebitda": stock.info.get("enterpriseToEbitda"),
        "peg_ratio": stock.info.get("pegRatio"),
        "roe": net_income / total_equity if total_equity else 0,
        "revenue_growth": stock.info.get("revenueGrowth"),
        "debt_to_equity": stock.info.get("debtToEquity"),
        "free_cash_flow": cash_flow.loc['Free Cash Flow'].iloc[0] if 'Free Cash Flow' in cash_flow.index else 0,
    }
    return data

if __name__ == "__main__":
    ticker_to_analyze = input("Enter the stock ticker to analyze: ")
    stock_data = get_stock_data(ticker_to_analyze)
    if stock_data:
        print(json.dumps(stock_data, indent=4))
    else:
        print(f"Could not retrieve data for {ticker_to_analyze}")