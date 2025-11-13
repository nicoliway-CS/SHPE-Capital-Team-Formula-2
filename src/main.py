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
    
    # 1. Get tickers - user can choose between default or custom
    tickers = algo.get_user_tickers()
    print(f"\nUsing {len(tickers)} tickers")
    
    # 2. Use tickers directly (already quality-filtered)
    filtered_tickers = tickers

    # If not enough stocks meet the criteria, exit gracefully
    if len(filtered_tickers) < 10:
        print("\nCould not find enough stocks meeting the criteria to build a portfolio. Try expanding the test list.")
        return

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
