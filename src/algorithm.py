import pandas as pd
import numpy as np
import yfinance as yf
from scipy.optimize import minimize
import analyzer # Import the analyzer module

def get_sp500_tickers():
    """Fetches the list of S&P 500 tickers from Wikipedia."""
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    table = pd.read_html(url, header=0)[0]
    return table['Symbol'].tolist()

def filter_stocks(tickers):
    """Filters stocks based on fundamental criteria using the analyzer."""
    print(f"Fetching data and filtering from {len(tickers)} stocks... This may take a while.")
    
    filtered_tickers = []
    for i, ticker in enumerate(tickers):
        # Provide progress feedback to the user
        print(f"Analyzing {ticker} ({i+1}/{len(tickers)})...", end='\r')
        
        try:
            data = analyzer.get_stock_data(ticker)
            
            # Ensure data is valid and meets our criteria
            if data and \
               data.get('trailing_pe') is not None and data['trailing_pe'] > 0 and \
               data.get('price_to_book') is not None and data['price_to_book'] < 5 and \
               data.get('roe') is not None and data['roe'] > 0.10:
                filtered_tickers.append(ticker)
        except Exception as e:
            # Silently ignore stocks that cause errors (e.g., data not available)
            continue
            
    print(f"\nFinished filtering. Found {len(filtered_tickers)} stocks meeting the criteria.")
    return filtered_tickers

def get_historical_data(tickers, period="5y"):
    """Downloads historical daily returns for a list of tickers."""
    data = yf.download(tickers, period=period)['Adj Close']
    returns = data.pct_change().dropna()
    return returns

def portfolio_performance(weights, mean_returns, cov_matrix):
    """Calculates the expected performance of a portfolio."""
    returns = np.sum(mean_returns * weights) * 252
    std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    return returns, std_dev

def negative_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate=0.02):
    """Calculates the negative Sharpe ratio for optimization."""
    p_returns, p_std_dev = portfolio_performance(weights, mean_returns, cov_matrix)
    return -(p_returns - risk_free_rate) / p_std_dev

def minimize_volatility(weights, mean_returns, cov_matrix):
    """Function to minimize portfolio volatility."""
    _, p_std_dev = portfolio_performance(weights, mean_returns, cov_matrix)
    return p_std_dev

def find_optimal_portfolio(mean_returns, cov_matrix):
    """Finds the portfolios with minimum volatility and maximum Sharpe ratio."""
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)
    
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0.0, 1.0) for asset in range(num_assets))
    
    # Find Max Sharpe Ratio Portfolio
    max_sharpe_result = minimize(negative_sharpe_ratio, num_assets*[1./num_assets,], args=args,
                                 method='SLSQP', bounds=bounds, constraints=constraints)
    max_sharpe_weights = max_sharpe_result.x
    
    # Find Minimum Volatility Portfolio
    min_vol_result = minimize(minimize_volatility, num_assets*[1./num_assets,], args=args,
                              method='SLSQP', bounds=bounds, constraints=constraints)
    min_vol_weights = min_vol_result.x
    
    return max_sharpe_weights, min_vol_weights

def optimize_portfolio(returns, risk_tolerance):
    """
    Optimizes a portfolio based on Modern Portfolio Theory and user's risk tolerance.
    """
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    
    max_sharpe_w, min_vol_w = find_optimal_portfolio(mean_returns, cov_matrix)
    
    # Blend portfolios based on risk tolerance (1=min_vol, 5=max_sharpe)
    blend_factor = (risk_tolerance - 1) / 4.0
    blended_weights = (1 - blend_factor) * min_vol_w + blend_factor * max_sharpe_w
    
    # Create a Series for easy sorting and selection
    weights_series = pd.Series(blended_weights, index=returns.columns)
    
    # Select top 10 stocks and normalize weights
    top_10_series = weights_series.nlargest(10)
    final_weights = top_10_series / top_10_series.sum()
    
    return final_weights.index.tolist(), final_weights.values

def display_portfolio_stats(tickers, weights, returns):
    """Calculates and displays statistics for the optimized portfolio."""
    # Subset the returns data to only include the tickers in our final portfolio
    portfolio_returns_subset = returns[tickers]
    
    # Calculate annualized portfolio return
    mean_returns = portfolio_returns_subset.mean()
    portfolio_return = np.sum(mean_returns * weights) * 252
    
    # Calculate portfolio volatility (annualized standard deviation)
    cov_matrix = portfolio_returns_subset.cov()
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
    
    # Calculate Sharpe Ratio
    risk_free_rate = 0.02
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
    
    # Project 10-year growth of a hypothetical $10,000 investment
    initial_investment = 10000
    future_value = initial_investment * ((1 + portfolio_return) ** 10)
    
    print("\n--- Optimized Portfolio ---")
    print("Top 10 Holdings & Optimal Weights:")
    for ticker, weight in zip(tickers, weights):
        print(f"- {ticker}: {weight:.2%}")
        
    print("\n--- Portfolio Statistics ---")
    print(f"Expected Annual Return: {portfolio_return:.2%}")
    print(f"Annual Volatility (Risk): {portfolio_volatility:.2%}")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    
    print("\n--- 10-Year Growth Projection ---")
    print(f"A ${initial_investment:,.2f} investment could grow to an estimated ${future_value:,.2f}.")