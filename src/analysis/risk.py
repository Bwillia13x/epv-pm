"""
Risk analysis calculations for financial portfolios
"""
import numpy as np
from scipy import stats
from typing import List, Dict


def calc_risk(prices: List[float]) -> Dict[str, float]:
    """
    Calculate risk metrics for a given price series.
    
    Args:
        prices: List of price values
        
    Returns:
        Dictionary containing VaR99, Sharpe ratio, and Alpha
    """
    if not prices or len(prices) < 2:
        return {"VaR99": 0.0, "Sharpe": 0.0, "Alpha": 0.0}
    
    # Convert to numpy array for calculations
    prices_array = np.array(prices)
    
    # Calculate returns
    returns = np.diff(prices_array) / prices_array[:-1]
    
    if len(returns) == 0:
        return {"VaR99": 0.0, "Sharpe": 0.0, "Alpha": 0.0}
    
    # Calculate Value at Risk (99th percentile)
    var99 = np.percentile(returns, 1)  # 1st percentile for 99% VaR
    
    # Calculate Sharpe ratio (assuming 0% risk-free rate)
    mean_return = np.mean(returns)
    std_return = np.std(returns, ddof=1) if len(returns) > 1 else 0.0
    sharpe = mean_return / std_return if std_return != 0 else 0.0
    
    # Calculate Alpha (excess return over market - simplified as mean return)
    # In a real implementation, this would be calculated against a benchmark
    alpha = mean_return
    
    return {
        "VaR99": float(var99),
        "Sharpe": float(sharpe),
        "Alpha": float(alpha)
    }


def calc_portfolio_risk(weights: List[float], returns_matrix: List[List[float]]) -> Dict[str, float]:
    """
    Calculate portfolio-level risk metrics.
    
    Args:
        weights: Portfolio weights for each asset
        returns_matrix: Matrix of returns for each asset (each row is an asset, each column is a time period)
        
    Returns:
        Dictionary containing portfolio risk metrics
    """
    if not weights or not returns_matrix:
        return {"Portfolio_VaR99": 0.0, "Portfolio_Volatility": 0.0}
    
    weights_array = np.array(weights)
    returns_array = np.array(returns_matrix)
    
    # Calculate portfolio returns (dot product of weights with each time period)
    # returns_array.T transposes so each column is an asset, each row is a time period
    portfolio_returns = np.dot(returns_array.T, weights_array)
    
    # Portfolio VaR
    portfolio_var99 = np.percentile(portfolio_returns, 1)
    
    # Portfolio volatility
    portfolio_volatility = np.std(portfolio_returns, ddof=1) if len(portfolio_returns) > 1 else 0.0
    
    return {
        "Portfolio_VaR99": float(portfolio_var99),
        "Portfolio_Volatility": float(portfolio_volatility)
    }


def calc_correlation_matrix(returns_matrix: List[List[float]]) -> List[List[float]]:
    """
    Calculate correlation matrix for multiple assets.
    
    Args:
        returns_matrix: Matrix of returns for each asset
        
    Returns:
        Correlation matrix as nested list
    """
    if not returns_matrix:
        return []
    
    returns_array = np.array(returns_matrix)
    
    # For single asset, return 1x1 matrix with correlation of 1.0
    if len(returns_matrix) == 1:
        return [[1.0]]
    
    # Calculate correlation matrix
    correlation_matrix = np.corrcoef(returns_array)
    
    # Handle NaN values
    correlation_matrix = np.nan_to_num(correlation_matrix, nan=0.0)
    
    return correlation_matrix.tolist()