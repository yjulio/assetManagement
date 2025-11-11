"""
Test suite for depreciation calculation function
Tests both straight_line and declining_balance methods
"""
import sys
import os
from datetime import date, timedelta, datetime
from decimal import Decimal


# Inline copy of calculate_depreciation function for testing
def calculate_depreciation(purchase_price, purchase_date_str, salvage_value, useful_life_years, method='straight_line'):
    """Calculate current asset value based on depreciation"""
    try:
        # Handle both date objects and string dates
        if isinstance(purchase_date_str, str):
            purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
        else:
            purchase_date = purchase_date_str
        
        years_owned = (date.today() - purchase_date).days / 365.25
        
        # If asset is fully depreciated, return salvage value
        if years_owned >= useful_life_years:
            return salvage_value
        
        if method == 'straight_line':
            # Straight-line depreciation
            depreciable_amount = purchase_price - salvage_value
            annual_depreciation = depreciable_amount / useful_life_years
            accumulated_depreciation = annual_depreciation * years_owned
            current_value = purchase_price - accumulated_depreciation
        elif method == 'declining_balance':
            # Double declining balance method
            rate = 2.0 / useful_life_years
            current_value = purchase_price * ((1 - rate) ** years_owned)
        else:
            current_value = purchase_price
        
        # Ensure we don't go below salvage value
        return max(current_value, salvage_value)
    except Exception as e:
        # If calculation fails, return purchase price
        return purchase_price


class TestDepreciationCalculation:
    """Test cases for calculate_depreciation function"""
    
    def test_straight_line_new_asset(self):
        """Test straight line depreciation for newly purchased asset"""
        purchase_price = 10000
        purchase_date = date.today()  # Today
        salvage_value = 1000
        useful_life_years = 5
        
        result = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'straight_line'
        )
        
        # New asset should have value close to purchase price
        assert result >= purchase_price * 0.99, f"Expected ~{purchase_price}, got {result}"
        assert result <= purchase_price, f"Value {result} exceeds purchase price {purchase_price}"
        print(f"✓ Straight line - New asset: ${purchase_price} → ${result:.2f}")
    
    def test_straight_line_mid_life(self):
        """Test straight line depreciation at mid-life"""
        purchase_price = 10000
        purchase_date = date.today() - timedelta(days=int(2.5 * 365.25))  # 2.5 years ago
        salvage_value = 1000
        useful_life_years = 5
        
        result = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'straight_line'
        )
        
        # After 2.5 years: depreciation = (10000 - 1000) / 5 * 2.5 = 4500
        # Expected value: 10000 - 4500 = 5500
        expected = 5500
        tolerance = 200
        assert abs(result - expected) < tolerance, f"Expected ~${expected}, got ${result:.2f}"
        print(f"✓ Straight line - Mid-life (2.5y): ${purchase_price} → ${result:.2f} (expected ~${expected})")
    
    def test_straight_line_nearly_depreciated(self):
        """Test straight line depreciation near end of useful life"""
        purchase_price = 10000
        purchase_date = date.today() - timedelta(days=int(4.9 * 365.25))  # 4.9 years ago
        salvage_value = 1000
        useful_life_years = 5
        
        result = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'straight_line'
        )
        
        # Should be close to salvage value
        expected = 1180  # (10000 - 1000) / 5 * 0.1 = 180 remaining + 1000 salvage
        tolerance = 200
        assert abs(result - expected) < tolerance, f"Expected ~${expected}, got ${result:.2f}"
        assert result >= salvage_value, f"Value ${result} below salvage ${salvage_value}"
        print(f"✓ Straight line - Nearly depreciated (4.9y): ${purchase_price} → ${result:.2f}")
    
    def test_straight_line_fully_depreciated(self):
        """Test straight line depreciation for fully depreciated asset"""
        purchase_price = 10000
        purchase_date = date.today() - timedelta(days=int(6 * 365.25))  # 6 years ago
        salvage_value = 1000
        useful_life_years = 5
        
        result = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'straight_line'
        )
        
        # Should return exactly salvage value
        assert result == salvage_value, f"Expected salvage ${salvage_value}, got ${result:.2f}"
        print(f"✓ Straight line - Fully depreciated (6y): ${purchase_price} → ${result:.2f}")
    
    def test_declining_balance_new_asset(self):
        """Test declining balance depreciation for new asset"""
        purchase_price = 10000
        purchase_date = date.today()
        salvage_value = 1000
        useful_life_years = 5
        
        result = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'declining_balance'
        )
        
        # New asset should have value close to purchase price
        assert result >= purchase_price * 0.99, f"Expected ~{purchase_price}, got {result}"
        assert result <= purchase_price, f"Value {result} exceeds purchase price {purchase_price}"
        print(f"✓ Declining balance - New asset: ${purchase_price} → ${result:.2f}")
    
    def test_declining_balance_mid_life(self):
        """Test declining balance depreciation at mid-life"""
        purchase_price = 10000
        purchase_date = date.today() - timedelta(days=int(2.5 * 365.25))  # 2.5 years ago
        salvage_value = 1000
        useful_life_years = 5
        
        result = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'declining_balance'
        )
        
        # Rate = 2.0 / 5 = 0.4 (double declining balance)
        # After 2.5 years: value = 10000 * (1 - 0.4)^2.5 = 10000 * 0.6^2.5 ≈ 2789
        # This is correct - declining balance depreciates faster initially
        expected = 2789
        tolerance = 300
        assert abs(result - expected) < tolerance, f"Expected ~${expected}, got ${result:.2f}"
        assert result >= salvage_value, f"Value ${result} below salvage ${salvage_value}"
        print(f"✓ Declining balance - Mid-life (2.5y): ${purchase_price} → ${result:.2f} (expected ~${expected})")
    
    def test_declining_balance_fully_depreciated(self):
        """Test declining balance for fully depreciated asset"""
        purchase_price = 10000
        purchase_date = date.today() - timedelta(days=int(10 * 365.25))  # 10 years ago
        salvage_value = 1000
        useful_life_years = 5
        
        result = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'declining_balance'
        )
        
        # Should return salvage value (protected by max())
        assert result == salvage_value, f"Expected salvage ${salvage_value}, got ${result:.2f}"
        print(f"✓ Declining balance - Fully depreciated (10y): ${purchase_price} → ${result:.2f}")
    
    def test_zero_salvage_value(self):
        """Test with zero salvage value"""
        purchase_price = 5000
        purchase_date = date.today() - timedelta(days=int(2 * 365.25))  # 2 years ago
        salvage_value = 0
        useful_life_years = 5
        
        result = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'straight_line'
        )
        
        # After 2 years: 5000 / 5 * 2 = 2000 depreciation
        # Expected: 5000 - 2000 = 3000
        expected = 3000
        tolerance = 150
        assert abs(result - expected) < tolerance, f"Expected ~${expected}, got ${result:.2f}"
        assert result >= 0, f"Value ${result} is negative"
        print(f"✓ Zero salvage value: ${purchase_price} → ${result:.2f} (expected ~${expected})")
    
    def test_string_date_format(self):
        """Test with date as string instead of date object"""
        purchase_price = 8000
        purchase_date_str = "2022-01-01"  # String format
        salvage_value = 800
        useful_life_years = 5
        
        result = calculate_depreciation(
            purchase_price, 
            purchase_date_str, 
            salvage_value, 
            useful_life_years, 
            'straight_line'
        )
        
        # Should handle string dates correctly
        assert result > salvage_value, f"Expected value > ${salvage_value}, got ${result:.2f}"
        assert result < purchase_price, f"Expected value < ${purchase_price}, got ${result:.2f}"
        print(f"✓ String date format: ${purchase_price} → ${result:.2f}")
    
    def test_high_salvage_value(self):
        """Test when salvage value is close to purchase price"""
        purchase_price = 10000
        purchase_date = date.today() - timedelta(days=int(3 * 365.25))  # 3 years ago
        salvage_value = 9000  # 90% of purchase price
        useful_life_years = 5
        
        result = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'straight_line'
        )
        
        # After 3 years: (10000 - 9000) / 5 * 3 = 600 depreciation
        # Expected: 10000 - 600 = 9400
        expected = 9400
        tolerance = 150
        assert abs(result - expected) < tolerance, f"Expected ~${expected}, got ${result:.2f}"
        print(f"✓ High salvage value: ${purchase_price} → ${result:.2f} (expected ~${expected})")
    
    def test_very_long_useful_life(self):
        """Test with very long useful life"""
        purchase_price = 100000
        purchase_date = date.today() - timedelta(days=int(5 * 365.25))  # 5 years ago
        salvage_value = 10000
        useful_life_years = 30  # 30 years
        
        result = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'straight_line'
        )
        
        # After 5 years: (100000 - 10000) / 30 * 5 = 15000 depreciation
        # Expected: 100000 - 15000 = 85000
        expected = 85000
        tolerance = 500
        assert abs(result - expected) < tolerance, f"Expected ~${expected}, got ${result:.2f}"
        print(f"✓ Long useful life (30y): ${purchase_price} → ${result:.2f} (expected ~${expected})")
    
    def test_short_useful_life(self):
        """Test with short useful life"""
        purchase_price = 3000
        purchase_date = date.today() - timedelta(days=int(1.5 * 365.25))  # 1.5 years ago
        salvage_value = 300
        useful_life_years = 2  # 2 years
        
        result = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'straight_line'
        )
        
        # After 1.5 years: (3000 - 300) / 2 * 1.5 = 2025 depreciation
        # Expected: 3000 - 2025 = 975
        expected = 975
        tolerance = 100
        assert abs(result - expected) < tolerance, f"Expected ~${expected}, got ${result:.2f}"
        print(f"✓ Short useful life (2y): ${purchase_price} → ${result:.2f} (expected ~${expected})")
    
    def test_error_handling_none_date(self):
        """Test error handling when date is None"""
        purchase_price = 5000
        purchase_date = None
        salvage_value = 500
        useful_life_years = 5
        
        result = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'straight_line'
        )
        
        # Should return purchase price on error
        assert result == purchase_price, f"Expected ${purchase_price} on error, got ${result:.2f}"
        print(f"✓ Error handling - None date: Returns purchase price ${result:.2f}")
    
    def test_comparison_methods(self):
        """Compare straight_line vs declining_balance for same asset"""
        purchase_price = 20000
        purchase_date = date.today() - timedelta(days=int(3 * 365.25))  # 3 years ago
        salvage_value = 2000
        useful_life_years = 5
        
        straight_line_value = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'straight_line'
        )
        
        declining_balance_value = calculate_depreciation(
            purchase_price, 
            purchase_date, 
            salvage_value, 
            useful_life_years, 
            'declining_balance'
        )
        
        print(f"✓ Method comparison (3y):")
        print(f"  Straight line: ${purchase_price} → ${straight_line_value:.2f}")
        print(f"  Declining balance: ${purchase_price} → ${declining_balance_value:.2f}")
        print(f"  Difference: ${abs(straight_line_value - declining_balance_value):.2f}")
        
        # Both should be valid depreciation
        assert straight_line_value >= salvage_value
        assert declining_balance_value >= salvage_value
        assert straight_line_value <= purchase_price
        assert declining_balance_value <= purchase_price


def run_all_tests():
    """Run all depreciation tests"""
    test_suite = TestDepreciationCalculation()
    
    print("\n" + "="*70)
    print("DEPRECIATION FUNCTION TEST SUITE")
    print("="*70 + "\n")
    
    # Get all test methods
    test_methods = [method for method in dir(test_suite) if method.startswith('test_')]
    
    passed = 0
    failed = 0
    errors = []
    
    for test_name in test_methods:
        try:
            test_method = getattr(test_suite, test_name)
            test_method()
            passed += 1
        except AssertionError as e:
            failed += 1
            errors.append(f"❌ {test_name}: {str(e)}")
            print(f"❌ {test_name}: {str(e)}")
        except Exception as e:
            failed += 1
            errors.append(f"❌ {test_name}: ERROR - {str(e)}")
            print(f"❌ {test_name}: ERROR - {str(e)}")
    
    print("\n" + "="*70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed out of {passed + failed} total")
    print("="*70 + "\n")
    
    if errors:
        print("Failed tests:")
        for error in errors:
            print(f"  {error}")
    
    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()
    sys.exit(0 if failed == 0 else 1)
