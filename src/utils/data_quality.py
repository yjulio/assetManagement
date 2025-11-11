"""
Data Quality and Standardization Module
Cleans, enriches, and standardizes asset data for accurate dashboard reporting
"""

import re
from datetime import datetime, date
from typing import Dict, List, Any, Tuple
import unicodedata

class DataQualityCleaner:
    """
    Handles data cleaning, standardization, and enrichment for asset management
    """
    
    # Standard category mappings (singular form)
    CATEGORY_STANDARDS = {
        'laptop': 'Laptop',
        'laptops': 'Laptop',
        'notebook': 'Laptop',
        'notebooks': 'Laptop',
        'computer': 'Computer',
        'computers': 'Computer',
        'desktop': 'Computer',
        'desktops': 'Computer',
        'pc': 'Computer',
        'pcs': 'Computer',
        'monitor': 'Monitor',
        'monitors': 'Monitor',
        'display': 'Monitor',
        'displays': 'Monitor',
        'screen': 'Monitor',
        'screens': 'Monitor',
        'printer': 'Printer',
        'printers': 'Printer',
        'phone': 'Phone',
        'phones': 'Phone',
        'mobile': 'Phone',
        'mobiles': 'Phone',
        'smartphone': 'Phone',
        'smartphones': 'Phone',
        'tablet': 'Tablet',
        'tablets': 'Tablet',
        'ipad': 'Tablet',
        'ipads': 'Tablet',
        'chair': 'Chair',
        'chairs': 'Chair',
        'desk': 'Desk',
        'desks': 'Desk',
        'table': 'Table',
        'tables': 'Table',
        'vehicle': 'Vehicle',
        'vehicles': 'Vehicle',
        'car': 'Vehicle',
        'cars': 'Vehicle',
        'truck': 'Vehicle',
        'trucks': 'Vehicle',
        'van': 'Vehicle',
        'vans': 'Vehicle',
    }
    
    # Standard supplier name mappings
    SUPPLIER_STANDARDS = {
        'hp': 'HP',
        'hewlett packard': 'HP',
        'hewlett-packard': 'HP',
        'dell': 'Dell',
        'dell inc': 'Dell',
        'dell inc.': 'Dell',
        'lenovo': 'Lenovo',
        'microsoft': 'Microsoft',
        'ms': 'Microsoft',
        'apple': 'Apple',
        'apple inc': 'Apple',
        'apple inc.': 'Apple',
        'samsung': 'Samsung',
        'canon': 'Canon',
        'epson': 'Epson',
        'brother': 'Brother',
    }
    
    # Standard location mappings
    LOCATION_STANDARDS = {
        'hq': 'Headquarters',
        'head office': 'Headquarters',
        'main office': 'Headquarters',
        'warehouse': 'Warehouse',
        'storage': 'Warehouse',
        'store': 'Warehouse',
    }
    
    @staticmethod
    def clean_string(value: Any) -> str:
        """
        Clean and normalize string values
        - Remove extra whitespace
        - Normalize unicode characters
        - Strip leading/trailing spaces
        """
        if value is None or value == '':
            return ''
        
        # Convert to string
        value = str(value)
        
        # Normalize unicode (remove accents, special characters)
        value = unicodedata.normalize('NFKD', value)
        value = value.encode('ASCII', 'ignore').decode('ASCII')
        
        # Remove extra whitespace
        value = ' '.join(value.split())
        
        # Strip and return
        return value.strip()
    
    @staticmethod
    def standardize_category(category: str) -> str:
        """
        Standardize category names to singular, proper case
        """
        if not category:
            return 'Uncategorized'
        
        # Clean the input
        category_clean = DataQualityCleaner.clean_string(category).lower()
        
        # Check if we have a standard mapping
        if category_clean in DataQualityCleaner.CATEGORY_STANDARDS:
            return DataQualityCleaner.CATEGORY_STANDARDS[category_clean]
        
        # Otherwise, capitalize first letter
        return category.strip().capitalize()
    
    @staticmethod
    def standardize_supplier(supplier: str) -> str:
        """
        Standardize supplier names
        """
        if not supplier:
            return 'Unknown Supplier'
        
        # Clean the input
        supplier_clean = DataQualityCleaner.clean_string(supplier).lower()
        
        # Check if we have a standard mapping
        if supplier_clean in DataQualityCleaner.SUPPLIER_STANDARDS:
            return DataQualityCleaner.SUPPLIER_STANDARDS[supplier_clean]
        
        # Otherwise, title case
        return supplier.strip().title()
    
    @staticmethod
    def standardize_location(location: str) -> str:
        """
        Standardize location names
        """
        if not location:
            return 'Unassigned'
        
        # Clean the input
        location_clean = DataQualityCleaner.clean_string(location).lower()
        
        # Check if we have a standard mapping
        if location_clean in DataQualityCleaner.LOCATION_STANDARDS:
            return DataQualityCleaner.LOCATION_STANDARDS[location_clean]
        
        # Otherwise, title case
        return location.strip().title()
    
    @staticmethod
    def clean_numeric(value: Any, default: float = 0.0) -> float:
        """
        Clean and convert numeric values
        """
        if value is None or value == '':
            return default
        
        try:
            # Remove currency symbols and commas
            if isinstance(value, str):
                value = value.replace('VT', '').replace('$', '').replace(',', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def validate_date(date_value: Any) -> Tuple[bool, Any]:
        """
        Validate and standardize date values
        Returns (is_valid, cleaned_date)
        """
        if date_value is None:
            return False, None
        
        # If already a date object
        if isinstance(date_value, (date, datetime)):
            return True, date_value
        
        # Try to parse string dates
        if isinstance(date_value, str):
            date_formats = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%Y/%m/%d',
                '%d-%m-%Y',
                '%m-%d-%Y',
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_value.strip(), fmt).date()
                    return True, parsed_date
                except ValueError:
                    continue
        
        return False, None
    
    @staticmethod
    def calculate_age_years(purchase_date: Any) -> float:
        """
        Calculate asset age in years
        """
        is_valid, cleaned_date = DataQualityCleaner.validate_date(purchase_date)
        
        if not is_valid:
            return 0.0
        
        today = date.today()
        age_days = (today - cleaned_date).days
        return round(age_days / 365.25, 2)
    
    @staticmethod
    def calculate_depreciation(purchase_price: float, purchase_date: Any, 
                              useful_life_years: int = 5, 
                              salvage_value: float = 0.0) -> Dict[str, float]:
        """
        Calculate depreciation using straight-line method
        Returns dict with depreciation details
        """
        age_years = DataQualityCleaner.calculate_age_years(purchase_date)
        
        if age_years <= 0 or purchase_price <= 0:
            return {
                'annual_depreciation': 0.0,
                'accumulated_depreciation': 0.0,
                'book_value': purchase_price,
                'depreciation_rate': 0.0
            }
        
        # Straight-line depreciation
        annual_depreciation = (purchase_price - salvage_value) / useful_life_years
        accumulated_depreciation = min(annual_depreciation * age_years, purchase_price - salvage_value)
        book_value = max(purchase_price - accumulated_depreciation, salvage_value)
        depreciation_rate = (accumulated_depreciation / purchase_price * 100) if purchase_price > 0 else 0
        
        return {
            'annual_depreciation': round(annual_depreciation, 2),
            'accumulated_depreciation': round(accumulated_depreciation, 2),
            'book_value': round(book_value, 2),
            'depreciation_rate': round(depreciation_rate, 2)
        }
    
    @staticmethod
    def calculate_total_cost_ownership(purchase_price: float, 
                                      maintenance_costs: List[float] = None,
                                      operating_costs: List[float] = None) -> float:
        """
        Calculate Total Cost of Ownership (TCO)
        """
        tco = purchase_price
        
        if maintenance_costs:
            tco += sum(maintenance_costs)
        
        if operating_costs:
            tco += sum(operating_costs)
        
        return round(tco, 2)
    
    @staticmethod
    def enrich_asset_data(asset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich asset data with calculated fields
        """
        enriched = asset.copy()
        
        # Clean and standardize
        enriched['category'] = DataQualityCleaner.standardize_category(asset.get('category', ''))
        enriched['supplier'] = DataQualityCleaner.standardize_supplier(asset.get('supplier', ''))
        enriched['location'] = DataQualityCleaner.standardize_location(asset.get('location', ''))
        
        # Clean numeric values
        enriched['price'] = DataQualityCleaner.clean_numeric(asset.get('price', 0))
        enriched['quantity'] = int(DataQualityCleaner.clean_numeric(asset.get('quantity', 0)))
        
        # Calculate total value
        enriched['total_value'] = enriched['price'] * enriched['quantity']
        
        # Calculate age
        if 'purchase_date' in asset:
            enriched['age_years'] = DataQualityCleaner.calculate_age_years(asset['purchase_date'])
            
            # Calculate depreciation
            depreciation = DataQualityCleaner.calculate_depreciation(
                enriched['price'],
                asset['purchase_date'],
                useful_life_years=asset.get('useful_life', 5)
            )
            enriched.update({
                'annual_depreciation': depreciation['annual_depreciation'],
                'accumulated_depreciation': depreciation['accumulated_depreciation'],
                'book_value': depreciation['book_value'],
                'depreciation_rate': depreciation['depreciation_rate']
            })
            
            # Asset lifecycle status
            if enriched['age_years'] >= 5:
                enriched['lifecycle_status'] = 'End of Life'
            elif enriched['age_years'] >= 3:
                enriched['lifecycle_status'] = 'Aging'
            elif enriched['age_years'] >= 1:
                enriched['lifecycle_status'] = 'Mature'
            else:
                enriched['lifecycle_status'] = 'New'
        
        # Utilization status
        if asset.get('checked_out', False):
            enriched['utilization_status'] = 'In Use'
        elif asset.get('maintenance_status') == 'pending':
            enriched['utilization_status'] = 'Under Maintenance'
        else:
            enriched['utilization_status'] = 'Available'
        
        # Risk assessment based on age and maintenance
        risk_score = 0
        if enriched.get('age_years', 0) >= 5:
            risk_score += 3
        elif enriched.get('age_years', 0) >= 3:
            risk_score += 2
        elif enriched.get('age_years', 0) >= 1:
            risk_score += 1
        
        if asset.get('maintenance_status') == 'pending':
            risk_score += 2
        
        if risk_score >= 4:
            enriched['risk_level'] = 'High'
        elif risk_score >= 2:
            enriched['risk_level'] = 'Medium'
        else:
            enriched['risk_level'] = 'Low'
        
        return enriched
    
    @staticmethod
    def remove_duplicates(assets: List[Dict[str, Any]], 
                         key_fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        Remove duplicate assets based on key fields
        Default: name, category, supplier
        """
        if key_fields is None:
            key_fields = ['name', 'category', 'supplier']
        
        seen = set()
        unique_assets = []
        
        for asset in assets:
            # Create a unique key from specified fields
            key = tuple(str(asset.get(field, '')).lower().strip() for field in key_fields)
            
            if key not in seen:
                seen.add(key)
                unique_assets.append(asset)
        
        return unique_assets
    
    @staticmethod
    def handle_missing_values(asset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle missing values with appropriate defaults
        """
        defaults = {
            'category': 'Uncategorized',
            'supplier': 'Unknown Supplier',
            'location': 'Unassigned',
            'department': 'Unassigned',
            'price': 0.0,
            'quantity': 0,
            'condition': 'Unknown',
            'status': 'Active',
            'notes': '',
            'description': '',
        }
        
        for field, default_value in defaults.items():
            if field not in asset or asset[field] is None or asset[field] == '':
                asset[field] = default_value
        
        return asset
    
    @staticmethod
    def generate_data_quality_report(assets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a data quality report
        """
        total_assets = len(assets)
        
        # Count issues
        missing_categories = sum(1 for a in assets if not a.get('category') or a.get('category') == 'Uncategorized')
        missing_suppliers = sum(1 for a in assets if not a.get('supplier') or a.get('supplier') == 'Unknown Supplier')
        missing_locations = sum(1 for a in assets if not a.get('location') or a.get('location') == 'Unassigned')
        missing_dates = sum(1 for a in assets if not a.get('purchase_date'))
        zero_prices = sum(1 for a in assets if DataQualityCleaner.clean_numeric(a.get('price', 0)) == 0)
        
        # Calculate quality score (0-100)
        issues = missing_categories + missing_suppliers + missing_locations + missing_dates + zero_prices
        max_issues = total_assets * 5  # 5 fields checked
        quality_score = 100 - (issues / max_issues * 100) if max_issues > 0 else 100
        
        return {
            'total_assets': total_assets,
            'quality_score': round(quality_score, 2),
            'issues': {
                'missing_categories': missing_categories,
                'missing_suppliers': missing_suppliers,
                'missing_locations': missing_locations,
                'missing_dates': missing_dates,
                'zero_prices': zero_prices,
                'total_issues': issues
            },
            'recommendations': [
                f"Complete category information for {missing_categories} assets" if missing_categories > 0 else None,
                f"Add supplier information for {missing_suppliers} assets" if missing_suppliers > 0 else None,
                f"Assign locations for {missing_locations} assets" if missing_locations > 0 else None,
                f"Add purchase dates for {missing_dates} assets" if missing_dates > 0 else None,
                f"Update pricing for {zero_prices} assets" if zero_prices > 0 else None,
            ]
        }
