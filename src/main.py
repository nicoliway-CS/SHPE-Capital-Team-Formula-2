import algorithm as algo

def get_risk_tolerance():
    """Prompts the user to determine their risk tolerance."""
    while True:
        try:
            tolerance = int(input("On a scale of 1 (very conservative) to 5 (very aggressive), what is your risk tolerance? "))
            if 1 <= tolerance <= 5:
                return tolerance
            else:
                print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    """Main function to run the portfolio optimization."""
    risk_level = get_risk_tolerance()
    print(f"\nRisk level selected: {risk_level}")
    
    # 1. Get S&P 500 tickers
    sp500_tickers = algo.get_sp500_tickers()
    
    # 2. Filter stocks (optional, can be expanded)
    filtered_tickers = algo.filter_stocks(sp500_tickers)
    
    # 3. Get historical data for the filtered stocks
    print("Downloading historical data...")
    historical_returns = algo.get_historical_data(filtered_tickers)
    
    # 4. Optimize the portfolio
    print("Optimizing portfolio...")
    optimal_tickers, optimal_weights = algo.optimize_portfolio(historical_returns, risk_level)
    
    # 5. Display the results
    algo.display_portfolio_stats(optimal_tickers, optimal_weights, historical_returns)

if __name__ == "__main__":
    main()
