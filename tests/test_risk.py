"""
Tests for risk analysis functionality
"""
import pytest
import numpy as np
from src.analysis.risk import calc_risk, calc_portfolio_risk, calc_correlation_matrix


class TestCalcRisk:
    """Test cases for calc_risk function"""
    
    def test_calc_risk_normal_case(self):
        """Test risk calculation with normal price series"""
        prices = [100.0, 101.0, 99.0, 102.0, 98.0, 105.0]
        result = calc_risk(prices)
        
        assert "VaR99" in result
        assert "Sharpe" in result
        assert "Alpha" in result
        assert isinstance(result["VaR99"], float)
        assert isinstance(result["Sharpe"], float)
        assert isinstance(result["Alpha"], float)
    
    def test_calc_risk_empty_list(self):
        """Test risk calculation with empty price list"""
        prices = []
        result = calc_risk(prices)
        
        assert result == {"VaR99": 0.0, "Sharpe": 0.0, "Alpha": 0.0}
    
    def test_calc_risk_single_price(self):
        """Test risk calculation with single price"""
        prices = [100.0]
        result = calc_risk(prices)
        
        assert result == {"VaR99": 0.0, "Sharpe": 0.0, "Alpha": 0.0}
    
    def test_calc_risk_two_prices(self):
        """Test risk calculation with two prices"""
        prices = [100.0, 105.0]
        result = calc_risk(prices)
        
        assert "VaR99" in result
        assert "Sharpe" in result
        assert "Alpha" in result
        # With only one return, std will be 0, so Sharpe should be 0
        assert result["Sharpe"] == 0.0
    
    @pytest.mark.parametrize("prices,expected_keys", [
        ([100.0, 102.0, 104.0], ["VaR99", "Sharpe", "Alpha"]),
        ([50.0, 55.0, 45.0, 60.0], ["VaR99", "Sharpe", "Alpha"]),
        ([1000.0, 990.0, 1010.0, 980.0, 1020.0], ["VaR99", "Sharpe", "Alpha"]),
    ])
    def test_calc_risk_parametrized(self, prices, expected_keys):
        """Parametrized test for different price series"""
        result = calc_risk(prices)
        
        for key in expected_keys:
            assert key in result
            assert isinstance(result[key], float)
    
    def test_calc_risk_constant_prices(self):
        """Test risk calculation with constant prices"""
        prices = [100.0, 100.0, 100.0, 100.0]
        result = calc_risk(prices)
        
        # All returns are 0, so all metrics should be 0
        assert result["VaR99"] == 0.0
        assert result["Sharpe"] == 0.0  # 0/0 handled as 0
        assert result["Alpha"] == 0.0
    
    def test_calc_risk_increasing_prices(self):
        """Test risk calculation with steadily increasing prices"""
        prices = [100.0, 101.0, 102.0, 103.0, 104.0]
        result = calc_risk(prices)
        
        # VaR should be positive (lowest return)
        assert isinstance(result["VaR99"], float)
        # Sharpe should be positive for consistently positive returns
        assert result["Sharpe"] > 0
        # Alpha (mean return) should be positive
        assert result["Alpha"] > 0
    
    def test_calc_risk_decreasing_prices(self):
        """Test risk calculation with steadily decreasing prices"""
        prices = [104.0, 103.0, 102.0, 101.0, 100.0]
        result = calc_risk(prices)
        
        # VaR should be negative (worst case loss)
        assert result["VaR99"] < 0
        # Sharpe should be negative for consistently negative returns
        assert result["Sharpe"] < 0
        # Alpha (mean return) should be negative
        assert result["Alpha"] < 0


class TestCalcPortfolioRisk:
    """Test cases for calc_portfolio_risk function"""
    
    def test_calc_portfolio_risk_normal_case(self):
        """Test portfolio risk calculation with normal inputs"""
        weights = [0.6, 0.4]
        returns_matrix = [[0.01, 0.02, -0.01], [0.015, -0.005, 0.02]]
        result = calc_portfolio_risk(weights, returns_matrix)
        
        assert "Portfolio_VaR99" in result
        assert "Portfolio_Volatility" in result
        assert isinstance(result["Portfolio_VaR99"], float)
        assert isinstance(result["Portfolio_Volatility"], float)
    
    def test_calc_portfolio_risk_empty_inputs(self):
        """Test portfolio risk calculation with empty inputs"""
        result1 = calc_portfolio_risk([], [])
        result2 = calc_portfolio_risk([0.5, 0.5], [])
        result3 = calc_portfolio_risk([], [[0.01, 0.02]])
        
        expected = {"Portfolio_VaR99": 0.0, "Portfolio_Volatility": 0.0}
        assert result1 == expected
        assert result2 == expected
        assert result3 == expected
    
    def test_calc_portfolio_risk_single_asset(self):
        """Test portfolio risk calculation with single asset"""
        weights = [1.0]
        returns_matrix = [[0.01, 0.02, -0.01, 0.005]]
        result = calc_portfolio_risk(weights, returns_matrix)
        
        assert "Portfolio_VaR99" in result
        assert "Portfolio_Volatility" in result
        assert isinstance(result["Portfolio_VaR99"], float)
        assert isinstance(result["Portfolio_Volatility"], float)


class TestCalcCorrelationMatrix:
    """Test cases for calc_correlation_matrix function"""
    
    def test_calc_correlation_matrix_normal_case(self):
        """Test correlation matrix calculation with normal inputs"""
        returns_matrix = [
            [0.01, 0.02, -0.01, 0.005],
            [0.015, -0.005, 0.02, -0.01]
        ]
        result = calc_correlation_matrix(returns_matrix)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert len(result[0]) == 2
        assert len(result[1]) == 2
        
        # Diagonal should be 1.0 (perfect self-correlation)
        assert abs(result[0][0] - 1.0) < 1e-10
        assert abs(result[1][1] - 1.0) < 1e-10
    
    def test_calc_correlation_matrix_empty_input(self):
        """Test correlation matrix calculation with empty input"""
        result = calc_correlation_matrix([])
        assert result == []
    
    def test_calc_correlation_matrix_single_asset(self):
        """Test correlation matrix calculation with single asset"""
        returns_matrix = [[0.01, 0.02, -0.01, 0.005]]
        result = calc_correlation_matrix(returns_matrix)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert len(result[0]) == 1
        assert abs(result[0][0] - 1.0) < 1e-10
    
    def test_calc_correlation_matrix_identical_series(self):
        """Test correlation matrix with identical return series"""
        returns_matrix = [
            [0.01, 0.02, -0.01],
            [0.01, 0.02, -0.01]
        ]
        result = calc_correlation_matrix(returns_matrix)
        
        # Correlation between identical series should be 1.0
        assert abs(result[0][1] - 1.0) < 1e-10
        assert abs(result[1][0] - 1.0) < 1e-10
    
    @pytest.mark.parametrize("returns_matrix,expected_shape", [
        ([[0.01, 0.02], [0.01, -0.02]], (2, 2)),
        ([[0.01, 0.02, 0.03], [0.01, -0.02, 0.005], [0.02, 0.01, -0.01]], (3, 3)),
    ])
    def test_calc_correlation_matrix_parametrized(self, returns_matrix, expected_shape):
        """Parametrized test for correlation matrix shapes"""
        result = calc_correlation_matrix(returns_matrix)
        
        assert len(result) == expected_shape[0]
        assert len(result[0]) == expected_shape[1]
        
        # Check diagonal elements are 1.0
        for i in range(expected_shape[0]):
            assert abs(result[i][i] - 1.0) < 1e-10


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_calc_risk_with_zeros(self):
        """Test calc_risk with zero prices"""
        prices = [0.0, 1.0, 2.0]
        result = calc_risk(prices)
        
        # Should handle zero prices gracefully
        assert "VaR99" in result
        assert "Sharpe" in result
        assert "Alpha" in result
    
    def test_calc_risk_with_negative_prices(self):
        """Test calc_risk with negative prices"""
        prices = [-1.0, -2.0, -3.0]
        result = calc_risk(prices)
        
        # Should handle negative prices (though unrealistic)
        assert "VaR99" in result
        assert "Sharpe" in result
        assert "Alpha" in result
    
    def test_calc_risk_large_numbers(self):
        """Test calc_risk with very large numbers"""
        prices = [1e6, 1.1e6, 0.9e6, 1.2e6]
        result = calc_risk(prices)
        
        assert "VaR99" in result
        assert "Sharpe" in result
        assert "Alpha" in result
        assert all(np.isfinite(v) for v in result.values())
    
    def test_calc_risk_small_numbers(self):
        """Test calc_risk with very small numbers"""
        prices = [1e-6, 1.1e-6, 0.9e-6, 1.2e-6]
        result = calc_risk(prices)
        
        assert "VaR99" in result
        assert "Sharpe" in result
        assert "Alpha" in result
        assert all(np.isfinite(v) for v in result.values())