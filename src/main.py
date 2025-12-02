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
    # 1. Ask the user for their risk tolerance
    risk_level = get_risk_tolerance()
    print(f"\nRisk level selected: {risk_level}")

    # 2. Ask the user which tickers to use (default 20 or custom)
    print("\nGetting tickers...")
    tickers = algo.get_user_tickers()  # from algorithm.py (uses YFin.py under the hood)
    print(f"\nYou selected {len(tickers)} tickers: {tickers}")

    # 3. Filter the tickers using fundamentals via analyzer.py
    print("\nFiltering stocks based on fundamental criteria (P/E > 0, P/B < 15)...")
    filtered_tickers = algo.filter_stocks(tickers)

    # If no stocks pass the filter, stop and tell the user
    if not filtered_tickers:
        print("\nNo stocks met the fundamental criteria.")
        print("Try again with more tickers or adjust the filter rules in algorithm.py.")
        return

    print(f"\nProceeding with {len(filtered_tickers)} filtered stocks:")
    print(filtered_tickers)

    # 4. Download historical price data for the filtered tickers
    print("\nDownloading historical price data...")
    historical_returns = algo.get_historical_data(filtered_tickers)

    # 5. Optimize the portfolio using Modern Portfolio Theory
    print("\nOptimizing portfolio...")
    optimal_tickers, optimal_weights = algo.optimize_portfolio(historical_returns, risk_level)

    # 6. Display the portfolio statistics and projections
    algo.display_portfolio_stats(optimal_tickers, optimal_weights, historical_returns)

if __name__ == "__main__":
    main()
