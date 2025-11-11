"""
Report Generation Utilities
Provides comprehensive scripts and helpers for generating all report types
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple, Any, Optional
from decimal import Decimal


class ReportGenerator:
    """Base class for report generation with common utilities"""
    
    def __init__(self, system):
        """Initialize with InventorySystem instance"""
        self.system = system
        
    def format_currency(self, value: float) -> str:
        """Format value as currency"""
        return f"${value:,.2f}"
    
    def format_date(self, date_obj) -> str:
        """Format date object as string"""
        if isinstance(date_obj, str):
            return date_obj
        if isinstance(date_obj, (date, datetime)):
            return date_obj.strftime('%Y-%m-%d')
        return str(date_obj)
    
    def format_percentage(self, value: float) -> str:
        """Format value as percentage"""
        return f"{value:.2f}%"
    
    def calculate_age(self, purchase_date) -> str:
        """Calculate asset age in years and months"""
        if not purchase_date:
            return "N/A"
        
        if isinstance(purchase_date, str):
            purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
        
        delta = date.today() - purchase_date
        years = delta.days // 365
        months = (delta.days % 365) // 30
        
        if years > 0:
            return f"{years}y {months}m"
        return f"{months}m"
    
    def get_date_range(self, period: str) -> Tuple[date, date]:
        """Get date range for common periods"""
        today = date.today()
        
        if period == 'today':
            return today, today
        elif period == 'week':
            start = today - timedelta(days=today.weekday())
            return start, today
        elif period == 'month':
            start = today.replace(day=1)
            return start, today
        elif period == 'quarter':
            quarter = (today.month - 1) // 3
            start = today.replace(month=quarter * 3 + 1, day=1)
            return start, today
        elif period == 'year':
            start = today.replace(month=1, day=1)
            return start, today
        else:
            return today - timedelta(days=30), today


class AutomatedReportGenerator(ReportGenerator):
    """Generate automated/dashboard reports with key metrics"""
    
    def generate(self) -> Dict[str, Any]:
        """Generate comprehensive automated report"""
        
        # Total assets
        total_assets = len(self.system.inventory)
        
        # Total value calculation
        total_value = sum(
            item.get('price', 0) * item.get('quantity', 0)
            for item in self.system.inventory.values()
        )
        
        # Assets by status
        status_breakdown = {
            'available': 0,
            'checked_out': 0,
            'maintenance': 0,
            'retired': 0
        }
        
        for item in self.system.inventory.values():
            status = item.get('status', 'available').lower()
            if status in status_breakdown:
                status_breakdown[status] += 1
        
        # Recent activity (last 30 days)
        recent_activity = self._get_recent_activity()
        
        # Top assets by value
        top_assets = self._get_top_assets_by_value(limit=10)
        
        # Depreciation summary
        depreciation_summary = self._get_depreciation_summary()
        
        # Maintenance alerts
        maintenance_alerts = self._get_maintenance_alerts()
        
        return {
            'generated_at': datetime.now(),
            'total_assets': total_assets,
            'total_value': total_value,
            'status_breakdown': status_breakdown,
            'recent_activity': recent_activity,
            'top_assets': top_assets,
            'depreciation_summary': depreciation_summary,
            'maintenance_alerts': maintenance_alerts,
            'summary': self._generate_summary(total_assets, total_value, status_breakdown)
        }
    
    def _get_recent_activity(self) -> List[Dict]:
        """Get recent transactions in last 30 days"""
        thirty_days_ago = date.today() - timedelta(days=30)
        recent = []
        
        try:
            # Query asset_transactions table
            self.system.cursor.execute("""
                SELECT asset_name, action, created_at, username, person, notes
                FROM asset_transactions
                WHERE created_at >= %s
                ORDER BY created_at DESC
                LIMIT 20
            """, (thirty_days_ago,))
            
            for row in self.system.cursor.fetchall():
                trans_date = row[2].date() if hasattr(row[2], 'date') else row[2]
                recent.append({
                    'asset': row[0] or 'N/A',
                    'type': row[1] or 'unknown',
                    'date': trans_date,
                    'user': row[3] or row[4] or 'N/A',
                    'details': row[5] or ''
                })
        except Exception as e:
            print(f"Warning: Could not load recent activity: {e}")
        
        return recent
    
    def _get_top_assets_by_value(self, limit: int = 10) -> List[Dict]:
        """Get top assets by total value"""
        assets_with_value = []
        
        for name, item in self.system.inventory.items():
            total_value = item.get('price', 0) * item.get('quantity', 0)
            assets_with_value.append({
                'name': name,
                'quantity': item.get('quantity', 0),
                'unit_price': item.get('price', 0),
                'total_value': total_value,
                'category': item.get('category', 'N/A'),
                'status': item.get('status', 'available')
            })
        
        return sorted(assets_with_value, key=lambda x: x['total_value'], reverse=True)[:limit]
    
    def _get_depreciation_summary(self) -> Dict[str, float]:
        """Calculate depreciation summary"""
        total_original = 0
        total_current = 0
        
        for item in self.system.inventory.values():
            quantity = item.get('quantity', 0)
            original = item.get('price', 0) * quantity
            total_original += original
            
            # If depreciation info available, calculate current value
            if item.get('depreciation_method') and item.get('depreciation_method') != 'none':
                # Would call calculate_depreciation here
                total_current += original * 0.8  # Placeholder
            else:
                total_current += original
        
        return {
            'original_value': total_original,
            'current_value': total_current,
            'total_depreciation': total_original - total_current,
            'depreciation_rate': ((total_original - total_current) / total_original * 100) if total_original > 0 else 0
        }
    
    def _get_maintenance_alerts(self) -> List[Dict]:
        """Get assets requiring maintenance"""
        alerts = []
        
        for name, item in self.system.inventory.items():
            if item.get('status') == 'maintenance':
                alerts.append({
                    'asset': name,
                    'reason': 'Currently in maintenance',
                    'severity': 'medium'
                })
            
            # Check warranty expiration
            warranty_date = item.get('warranty_expiration')
            if warranty_date:
                if isinstance(warranty_date, str):
                    warranty_date = datetime.strptime(warranty_date, '%Y-%m-%d').date()
                
                if warranty_date < date.today():
                    alerts.append({
                        'asset': name,
                        'reason': 'Warranty expired',
                        'severity': 'low'
                    })
                elif warranty_date < date.today() + timedelta(days=30):
                    alerts.append({
                        'asset': name,
                        'reason': 'Warranty expiring soon',
                        'severity': 'medium'
                    })
        
        return alerts
    
    def _generate_summary(self, total_assets: int, total_value: float, status: Dict) -> str:
        """Generate text summary"""
        available_pct = (status['available'] / total_assets * 100) if total_assets > 0 else 0
        
        return f"""Asset Management Summary:
- Total Assets: {total_assets}
- Total Value: {self.format_currency(total_value)}
- Available: {status['available']} ({available_pct:.1f}%)
- Checked Out: {status['checked_out']}
- In Maintenance: {status['maintenance']}
- Retired: {status['retired']}
"""


class InventoryReportGenerator(ReportGenerator):
    """Generate inventory reports with stock levels and valuations"""
    
    def generate(self, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate inventory report with optional filters"""
        
        assets = []
        total_items = 0
        total_units = 0
        total_value = 0
        
        for name, item in self.system.inventory.items():
            # Apply filters if provided
            if filters:
                if filters.get('category') and item.get('category') != filters['category']:
                    continue
                if filters.get('status') and item.get('status') != filters['status']:
                    continue
                if filters.get('location') and item.get('location') != filters['location']:
                    continue
            
            quantity = item.get('quantity', 0)
            price = item.get('price', 0)
            item_value = quantity * price
            
            assets.append({
                'name': name,
                'category': item.get('category', 'N/A'),
                'quantity': quantity,
                'unit_price': price,
                'total_value': item_value,
                'location': item.get('location', 'N/A'),
                'status': item.get('status', 'available'),
                'stock_level': self._assess_stock_level(quantity, item.get('reorder_point', 0))
            })
            
            total_items += 1
            total_units += quantity
            total_value += item_value
        
        # Sort by value (highest first)
        assets.sort(key=lambda x: x['total_value'], reverse=True)
        
        # Category breakdown
        category_breakdown = self._get_category_breakdown(assets)
        
        # Location breakdown
        location_breakdown = self._get_location_breakdown(assets)
        
        return {
            'generated_at': datetime.now(),
            'filters_applied': filters or {},
            'assets': assets,
            'total_items': total_items,
            'total_units': total_units,
            'total_value': total_value,
            'category_breakdown': category_breakdown,
            'location_breakdown': location_breakdown,
            'low_stock_items': [a for a in assets if a['stock_level'] == 'low']
        }
    
    def _assess_stock_level(self, quantity: int, reorder_point: int) -> str:
        """Assess stock level status"""
        if quantity == 0:
            return 'out_of_stock'
        elif quantity <= reorder_point:
            return 'low'
        elif quantity <= reorder_point * 2:
            return 'medium'
        else:
            return 'healthy'
    
    def _get_category_breakdown(self, assets: List[Dict]) -> Dict[str, Dict]:
        """Break down inventory by category"""
        breakdown = {}
        
        for asset in assets:
            category = asset['category']
            if category not in breakdown:
                breakdown[category] = {
                    'count': 0,
                    'total_value': 0,
                    'items': []
                }
            
            breakdown[category]['count'] += 1
            breakdown[category]['total_value'] += asset['total_value']
            breakdown[category]['items'].append(asset['name'])
        
        return breakdown
    
    def _get_location_breakdown(self, assets: List[Dict]) -> Dict[str, Dict]:
        """Break down inventory by location"""
        breakdown = {}
        
        for asset in assets:
            location = asset['location']
            if location not in breakdown:
                breakdown[location] = {
                    'count': 0,
                    'total_value': 0
                }
            
            breakdown[location]['count'] += 1
            breakdown[location]['total_value'] += asset['total_value']
        
        return breakdown


class AssetReportGenerator(ReportGenerator):
    """Generate detailed asset reports"""
    
    def generate(self, asset_name: Optional[str] = None) -> Dict[str, Any]:
        """Generate detailed asset report for one or all assets"""
        
        if asset_name:
            return self._generate_single_asset_report(asset_name)
        else:
            return self._generate_all_assets_report()
    
    def _generate_single_asset_report(self, asset_name: str) -> Dict[str, Any]:
        """Generate comprehensive report for a single asset"""
        
        if asset_name not in self.system.inventory:
            return {'error': f'Asset {asset_name} not found'}
        
        item = self.system.inventory[asset_name]
        
        # Basic information
        basic_info = {
            'name': asset_name,
            'category': item.get('category', 'N/A'),
            'description': item.get('description', 'N/A'),
            'quantity': item.get('quantity', 0),
            'unit_price': item.get('price', 0),
            'total_value': item.get('price', 0) * item.get('quantity', 0),
            'status': item.get('status', 'available'),
            'location': item.get('location', 'N/A')
        }
        
        # Purchase information
        purchase_info = {
            'purchase_date': self.format_date(item.get('purchase_date')),
            'age': self.calculate_age(item.get('purchase_date')),
            'vendor': item.get('vendor', 'N/A'),
            'purchase_order': item.get('purchase_order', 'N/A')
        }
        
        # Depreciation information
        depreciation_info = {
            'method': item.get('depreciation_method', 'none'),
            'useful_life': item.get('useful_life_years', 0),
            'salvage_value': item.get('salvage_value', 0)
        }
        
        # Warranty information
        warranty_info = {
            'warranty_expiration': self.format_date(item.get('warranty_expiration')),
            'warranty_status': self._get_warranty_status(item.get('warranty_expiration'))
        }
        
        # Transaction history
        try:
            self.system.cursor.execute("""
                SELECT created_at, action, username, person, notes
                FROM asset_transactions
                WHERE asset_name = %s
                ORDER BY created_at DESC
                LIMIT 50
            """, (asset_name,))
            
            transaction_history = [
                {
                    'date': row[0],
                    'type': row[1],
                    'user': row[2] or row[3] or 'N/A',
                    'notes': row[4] or ''
                }
                for row in self.system.cursor.fetchall()
            ]
        except Exception:
            transaction_history = []
        
        # Usage statistics
        usage_stats = self._calculate_usage_stats(asset_name)
        
        return {
            'generated_at': datetime.now(),
            'basic_info': basic_info,
            'purchase_info': purchase_info,
            'depreciation_info': depreciation_info,
            'warranty_info': warranty_info,
            'transaction_history': transaction_history,
            'usage_stats': usage_stats,
            'assigned_to': item.get('assigned_to', 'N/A'),
            'notes': item.get('notes', '')
        }
    
    def _generate_all_assets_report(self) -> Dict[str, Any]:
        """Generate summary report for all assets"""
        
        assets = []
        
        for name, item in self.system.inventory.items():
            assets.append({
                'name': name,
                'category': item.get('category', 'N/A'),
                'quantity': item.get('quantity', 0),
                'unit_price': item.get('price', 0),
                'total_value': item.get('price', 0) * item.get('quantity', 0),
                'status': item.get('status', 'available'),
                'location': item.get('location', 'N/A'),
                'age': self.calculate_age(item.get('purchase_date')),
                'assigned_to': item.get('assigned_to', 'Unassigned')
            })
        
        return {
            'generated_at': datetime.now(),
            'total_assets': len(assets),
            'assets': sorted(assets, key=lambda x: x['name'])
        }
    
    def _get_warranty_status(self, warranty_date) -> str:
        """Determine warranty status"""
        if not warranty_date:
            return 'no_warranty'
        
        if isinstance(warranty_date, str):
            warranty_date = datetime.strptime(warranty_date, '%Y-%m-%d').date()
        
        today = date.today()
        
        if warranty_date < today:
            return 'expired'
        elif warranty_date < today + timedelta(days=30):
            return 'expiring_soon'
        else:
            return 'active'
    
    def _calculate_usage_stats(self, asset_name: str) -> Dict[str, Any]:
        """Calculate usage statistics from transactions"""
        
        try:
            self.system.cursor.execute("""
                SELECT action FROM asset_transactions
                WHERE asset_name = %s
            """, (asset_name,))
            
            transactions = [row[0] for row in self.system.cursor.fetchall()]
            
            total_transactions = len(transactions)
            checkouts = sum(1 for t in transactions if t and 'checkout' in t.lower())
            checkins = sum(1 for t in transactions if t and 'checkin' in t.lower())
            maintenance = sum(1 for t in transactions if t and 'maintenance' in t.lower())
            
            return {
                'total_transactions': total_transactions,
                'checkouts': checkouts,
                'checkins': checkins,
                'maintenance_events': maintenance,
                'current_status': 'checked_out' if checkouts > checkins else 'available'
            }
        except Exception:
            return {
                'total_transactions': 0,
                'checkouts': 0,
                'checkins': 0,
                'maintenance_events': 0,
                'current_status': 'unknown'
            }


class AuditReportGenerator(ReportGenerator):
    """Generate audit reports for data integrity and compliance"""
    
    def generate(self) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        
        findings = []
        
        # Check for negative quantities
        negative_qty = self._check_negative_quantities()
        if negative_qty:
            findings.append({
                'category': 'Negative Quantities',
                'severity': 'high',
                'count': len(negative_qty),
                'items': negative_qty,
                'recommendation': 'Investigate and correct negative stock levels'
            })
        
        # Check for invalid prices
        invalid_prices = self._check_invalid_prices()
        if invalid_prices:
            findings.append({
                'category': 'Invalid Prices',
                'severity': 'medium',
                'count': len(invalid_prices),
                'items': invalid_prices,
                'recommendation': 'Update assets with valid pricing information'
            })
        
        # Check for missing required fields
        missing_fields = self._check_missing_fields()
        if missing_fields:
            findings.append({
                'category': 'Missing Required Fields',
                'severity': 'medium',
                'count': len(missing_fields),
                'items': missing_fields,
                'recommendation': 'Complete asset information for better tracking'
            })
        
        # Check for expired warranties without maintenance
        warranty_issues = self._check_warranty_status()
        if warranty_issues:
            findings.append({
                'category': 'Warranty Issues',
                'severity': 'low',
                'count': len(warranty_issues),
                'items': warranty_issues,
                'recommendation': 'Review assets with expired warranties'
            })
        
        # Check for assets without transactions
        inactive_assets = self._check_inactive_assets()
        if inactive_assets:
            findings.append({
                'category': 'Inactive Assets',
                'severity': 'low',
                'count': len(inactive_assets),
                'items': inactive_assets,
                'recommendation': 'Review unused assets for potential disposal'
            })
        
        # Calculate overall health score
        health_score = self._calculate_health_score(findings)
        
        return {
            'generated_at': datetime.now(),
            'total_assets_audited': len(self.system.inventory),
            'findings': findings,
            'total_issues': sum(f['count'] for f in findings),
            'health_score': health_score,
            'status': self._get_audit_status(health_score),
            'summary': self._generate_audit_summary(findings, health_score)
        }
    
    def _check_negative_quantities(self) -> List[Dict]:
        """Check for assets with negative quantities"""
        issues = []
        for name, item in self.system.inventory.items():
            if item.get('quantity', 0) < 0:
                issues.append({
                    'asset': name,
                    'quantity': item['quantity'],
                    'issue': f'Negative quantity: {item["quantity"]}'
                })
        return issues
    
    def _check_invalid_prices(self) -> List[Dict]:
        """Check for assets with invalid prices"""
        issues = []
        for name, item in self.system.inventory.items():
            price = item.get('price', 0)
            if price <= 0:
                issues.append({
                    'asset': name,
                    'price': price,
                    'issue': f'Invalid price: {price}'
                })
        return issues
    
    def _check_missing_fields(self) -> List[Dict]:
        """Check for assets missing required fields"""
        issues = []
        required_fields = ['category', 'description', 'location', 'purchase_date']
        
        for name, item in self.system.inventory.items():
            missing = [field for field in required_fields if not item.get(field)]
            if missing:
                issues.append({
                    'asset': name,
                    'missing_fields': missing,
                    'issue': f'Missing fields: {", ".join(missing)}'
                })
        return issues
    
    def _check_warranty_status(self) -> List[Dict]:
        """Check for warranty-related issues"""
        issues = []
        for name, item in self.system.inventory.items():
            warranty_date = item.get('warranty_expiration')
            if warranty_date:
                if isinstance(warranty_date, str):
                    warranty_date = datetime.strptime(warranty_date, '%Y-%m-%d').date()
                
                if warranty_date < date.today():
                    issues.append({
                        'asset': name,
                        'warranty_date': self.format_date(warranty_date),
                        'issue': 'Warranty expired'
                    })
        return issues
    
    def _check_inactive_assets(self) -> List[Dict]:
        """Check for assets with no recent activity"""
        issues = []
        ninety_days_ago = date.today() - timedelta(days=90)
        
        for name, item in self.system.inventory.items():
            try:
                # Check last transaction date
                self.system.cursor.execute("""
                    SELECT MAX(created_at) 
                    FROM asset_transactions
                    WHERE asset_name = %s
                """, (name,))
                
                result = self.system.cursor.fetchone()
                last_date = result[0] if result and result[0] else None
                
                if not last_date:
                    issues.append({
                        'asset': name,
                        'last_activity': 'Never',
                        'issue': 'No transaction history'
                    })
                    continue
                
                if isinstance(last_date, str):
                    last_date = datetime.strptime(last_date, '%Y-%m-%d').date()
                elif hasattr(last_date, 'date'):
                    last_date = last_date.date()
                
                if last_date < ninety_days_ago:
                    issues.append({
                        'asset': name,
                        'last_activity': self.format_date(last_date),
                        'issue': f'No activity since {self.format_date(last_date)}'
                    })
            except Exception:
                continue
        
        return issues
    
    def _calculate_health_score(self, findings: List[Dict]) -> float:
        """Calculate overall data health score (0-100)"""
        total_assets = len(self.system.inventory)
        if total_assets == 0:
            return 100.0
        
        # Weight by severity
        severity_weights = {'high': 3, 'medium': 2, 'low': 1}
        
        total_deductions = sum(
            f['count'] * severity_weights.get(f['severity'], 1)
            for f in findings
        )
        
        # Calculate score
        max_possible_deductions = total_assets * 3  # Assuming worst case
        score = max(0, 100 - (total_deductions / max_possible_deductions * 100))
        
        return round(score, 2)
    
    def _get_audit_status(self, health_score: float) -> str:
        """Get audit status based on health score"""
        if health_score >= 90:
            return 'excellent'
        elif health_score >= 75:
            return 'good'
        elif health_score >= 60:
            return 'fair'
        else:
            return 'needs_attention'
    
    def _generate_audit_summary(self, findings: List[Dict], health_score: float) -> str:
        """Generate text summary of audit"""
        total_issues = sum(f['count'] for f in findings)
        high_severity = sum(f['count'] for f in findings if f['severity'] == 'high')
        
        return f"""Audit Summary:
Health Score: {health_score}/100 ({self._get_audit_status(health_score).replace('_', ' ').title()})
Total Issues Found: {total_issues}
High Severity Issues: {high_severity}
Categories with Issues: {len(findings)}

Recommendations:
{'- Address high severity issues immediately' if high_severity > 0 else '- No critical issues found'}
- Review and update incomplete asset records
- Establish regular audit schedule
"""


class DepreciationReportGenerator(ReportGenerator):
    """Generate depreciation reports for financial analysis"""
    
    def generate(self, calculate_depreciation_func=None) -> Dict[str, Any]:
        """Generate comprehensive depreciation report"""
        
        depreciation_data = []
        total_purchase_value = 0
        total_current_value = 0
        total_depreciation = 0
        
        for name, item in self.system.inventory.items():
            if not item.get('purchase_date'):
                continue
            
            depreciation_method = item.get('depreciation_method', 'none')
            if depreciation_method == 'none':
                continue
            
            purchase_price = item.get('price', 0)
            quantity = item.get('quantity', 0)
            purchase_value = purchase_price * quantity
            
            # Calculate current value (if function provided)
            if calculate_depreciation_func:
                current_unit_value = calculate_depreciation_func(
                    purchase_price,
                    item.get('purchase_date'),
                    item.get('salvage_value', 0),
                    item.get('useful_life_years', 5),
                    depreciation_method
                )
                current_value = current_unit_value * quantity
            else:
                # Fallback: simple straight-line estimation
                age = self.calculate_age(item.get('purchase_date'))
                current_value = purchase_value * 0.8  # Placeholder
            
            depreciation_amount = purchase_value - current_value
            depreciation_percent = (depreciation_amount / purchase_value * 100) if purchase_value > 0 else 0
            
            asset_info = {
                'name': name,
                'category': item.get('category', 'N/A'),
                'purchase_date': self.format_date(item.get('purchase_date')),
                'age': self.calculate_age(item.get('purchase_date')),
                'quantity': quantity,
                'purchase_value': purchase_value,
                'current_value': current_value,
                'depreciation_amount': depreciation_amount,
                'depreciation_percent': depreciation_percent,
                'method': depreciation_method,
                'useful_life': item.get('useful_life_years', 5),
                'salvage_value': item.get('salvage_value', 0)
            }
            
            depreciation_data.append(asset_info)
            
            total_purchase_value += purchase_value
            total_current_value += current_value
            total_depreciation += depreciation_amount
        
        # Sort by depreciation amount (highest first)
        depreciation_data.sort(key=lambda x: x['depreciation_amount'], reverse=True)
        
        # Method breakdown
        method_breakdown = self._get_method_breakdown(depreciation_data)
        
        # Category breakdown
        category_breakdown = self._get_category_depreciation(depreciation_data)
        
        return {
            'generated_at': datetime.now(),
            'assets': depreciation_data,
            'total_purchase_value': total_purchase_value,
            'total_current_value': total_current_value,
            'total_depreciation': total_depreciation,
            'depreciation_rate': (total_depreciation / total_purchase_value * 100) if total_purchase_value > 0 else 0,
            'method_breakdown': method_breakdown,
            'category_breakdown': category_breakdown,
            'summary': self._generate_depreciation_summary(
                total_purchase_value, total_current_value, total_depreciation
            )
        }
    
    def _get_method_breakdown(self, assets: List[Dict]) -> Dict[str, Dict]:
        """Break down depreciation by method"""
        breakdown = {}
        
        for asset in assets:
            method = asset['method']
            if method not in breakdown:
                breakdown[method] = {
                    'count': 0,
                    'total_depreciation': 0,
                    'assets': []
                }
            
            breakdown[method]['count'] += 1
            breakdown[method]['total_depreciation'] += asset['depreciation_amount']
            breakdown[method]['assets'].append(asset['name'])
        
        return breakdown
    
    def _get_category_depreciation(self, assets: List[Dict]) -> Dict[str, Dict]:
        """Break down depreciation by category"""
        breakdown = {}
        
        for asset in assets:
            category = asset['category']
            if category not in breakdown:
                breakdown[category] = {
                    'count': 0,
                    'total_depreciation': 0,
                    'avg_depreciation_rate': 0
                }
            
            breakdown[category]['count'] += 1
            breakdown[category]['total_depreciation'] += asset['depreciation_amount']
        
        # Calculate average rates
        for category, data in breakdown.items():
            category_assets = [a for a in assets if a['category'] == category]
            avg_rate = sum(a['depreciation_percent'] for a in category_assets) / len(category_assets)
            data['avg_depreciation_rate'] = round(avg_rate, 2)
        
        return breakdown
    
    def _generate_depreciation_summary(self, purchase: float, current: float, depreciation: float) -> str:
        """Generate text summary"""
        rate = (depreciation / purchase * 100) if purchase > 0 else 0
        
        return f"""Depreciation Summary:
Total Original Value: {self.format_currency(purchase)}
Total Current Value: {self.format_currency(current)}
Total Depreciation: {self.format_currency(depreciation)}
Overall Depreciation Rate: {rate:.2f}%
"""


class MaintenanceReportGenerator(ReportGenerator):
    """Generate maintenance reports"""
    
    def generate(self) -> Dict[str, Any]:
        """Generate maintenance report"""
        
        maintenance_records = []
        
        try:
            # Query maintenance transactions
            self.system.cursor.execute("""
                SELECT asset_name, COUNT(*) as event_count, MAX(created_at) as last_maintenance
                FROM asset_transactions
                WHERE action LIKE '%maintenance%'
                GROUP BY asset_name
                ORDER BY event_count DESC
            """)
            
            for row in self.system.cursor.fetchall():
                asset_name = row[0]
                item = self.system.inventory.get(asset_name, {})
                
                maintenance_records.append({
                    'asset': asset_name,
                    'category': item.get('category', 'N/A'),
                    'total_events': row[1],
                    'last_maintenance': self.format_date(row[2]),
                    'status': item.get('status', 'available'),
                    'events': []  # Can be loaded separately if needed
                })
        except Exception as e:
            print(f"Warning: Could not load maintenance records: {e}")
        
        # Assets needing maintenance (no maintenance in 90 days)
        needs_maintenance = self._identify_maintenance_needed()
        
        # Maintenance costs (if available)
        maintenance_costs = self._calculate_maintenance_costs(maintenance_records)
        
        return {
            'generated_at': datetime.now(),
            'maintenance_records': maintenance_records,
            'total_assets_with_maintenance': len(maintenance_records),
            'needs_maintenance': needs_maintenance,
            'maintenance_costs': maintenance_costs,
            'summary': self._generate_maintenance_summary(maintenance_records, needs_maintenance)
        }
    
    def _identify_maintenance_needed(self) -> List[Dict]:
        """Identify assets that may need maintenance"""
        needs_maintenance = []
        ninety_days_ago = date.today() - timedelta(days=90)
        
        for name, item in self.system.inventory.items():
            try:
                # Check last maintenance date
                self.system.cursor.execute("""
                    SELECT MAX(created_at) 
                    FROM asset_transactions
                    WHERE asset_name = %s AND action LIKE '%maintenance%'
                """, (name,))
                
                result = self.system.cursor.fetchone()
                last_maintenance = result[0] if result and result[0] else None
                
                if not last_maintenance:
                    needs_maintenance.append({
                        'asset': name,
                        'reason': 'No maintenance history',
                        'priority': 'low'
                    })
                    continue
                
                if isinstance(last_maintenance, str):
                    last_maintenance = datetime.strptime(last_maintenance, '%Y-%m-%d').date()
                elif hasattr(last_maintenance, 'date'):
                    last_maintenance = last_maintenance.date()
                
                if last_maintenance < ninety_days_ago:
                    needs_maintenance.append({
                        'asset': name,
                        'reason': f'Last maintenance: {self.format_date(last_maintenance)}',
                        'priority': 'medium'
                    })
            except Exception:
                continue
        
        return needs_maintenance
    
    def _calculate_maintenance_costs(self, records: List[Dict]) -> Dict[str, float]:
        """Calculate maintenance costs if available"""
        total_cost = 0
        by_asset = {}
        
        for record in records:
            asset_cost = 0
            for event in record['events']:
                cost = event.get('cost', 0)
                if isinstance(cost, (int, float)):
                    asset_cost += cost
                    total_cost += cost
            
            by_asset[record['asset']] = asset_cost
        
        return {
            'total': total_cost,
            'by_asset': by_asset,
            'average': total_cost / len(records) if records else 0
        }
    
    def _generate_maintenance_summary(self, records: List[Dict], needs: List[Dict]) -> str:
        """Generate maintenance summary"""
        return f"""Maintenance Summary:
Assets with Maintenance History: {len(records)}
Assets Needing Maintenance: {len(needs)}
Total Maintenance Events: {sum(r['total_events'] for r in records)}

Recommendations:
- Schedule maintenance for {len(needs)} assets
- Review high-maintenance assets for replacement
- Implement preventive maintenance schedule
"""


class CheckoutReportGenerator(ReportGenerator):
    """Generate checkout/usage reports"""
    
    def generate(self, period: str = 'month') -> Dict[str, Any]:
        """Generate checkout report for specified period"""
        
        start_date, end_date = self.get_date_range(period)
        
        checkout_data = []
        
        try:
            # Query checkouts within period
            self.system.cursor.execute("""
                SELECT asset_name, action, created_at, username, person, notes
                FROM asset_transactions
                WHERE action LIKE '%checkout%'
                AND created_at BETWEEN %s AND %s
                ORDER BY created_at DESC
            """, (start_date, end_date))
            
            # Group by asset
            asset_checkouts = {}
            for row in self.system.cursor.fetchall():
                asset_name = row[0]
                if asset_name not in asset_checkouts:
                    asset_checkouts[asset_name] = []
                
                asset_checkouts[asset_name].append({
                    'type': row[1],
                    'date': row[2],
                    'user': row[3] or row[4] or 'N/A',
                    'notes': row[5] or ''
                })
            
            # Build checkout data
            for asset_name, checkouts in asset_checkouts.items():
                item = self.system.inventory.get(asset_name, {})
                checkout_data.append({
                    'asset': asset_name,
                    'category': item.get('category', 'N/A'),
                    'total_checkouts': len(checkouts),
                    'checkouts': checkouts,
                    'current_status': item.get('status', 'available')
                })
        except Exception as e:
            print(f"Warning: Could not load checkout data: {e}")
        
        # Most checked out assets
        most_used = sorted(checkout_data, key=lambda x: x['total_checkouts'], reverse=True)[:10]
        
        # User checkout statistics
        user_stats = self._get_user_checkout_stats(checkout_data)
        
        return {
            'generated_at': datetime.now(),
            'period': period,
            'start_date': self.format_date(start_date),
            'end_date': self.format_date(end_date),
            'checkout_data': checkout_data,
            'total_checkouts': sum(d['total_checkouts'] for d in checkout_data),
            'most_used_assets': most_used,
            'user_statistics': user_stats,
            'summary': self._generate_checkout_summary(checkout_data, period)
        }
    
    def _get_user_checkout_stats(self, checkout_data: List[Dict]) -> Dict[str, Dict]:
        """Get checkout statistics by user"""
        user_stats = {}
        
        for asset in checkout_data:
            for checkout in asset['checkouts']:
                user = checkout.get('user', 'Unknown')
                
                if user not in user_stats:
                    user_stats[user] = {
                        'total_checkouts': 0,
                        'assets_checked_out': []
                    }
                
                user_stats[user]['total_checkouts'] += 1
                if asset['asset'] not in user_stats[user]['assets_checked_out']:
                    user_stats[user]['assets_checked_out'].append(asset['asset'])
        
        return user_stats
    
    def _generate_checkout_summary(self, data: List[Dict], period: str) -> str:
        """Generate checkout summary"""
        total_checkouts = sum(d['total_checkouts'] for d in data)
        assets_used = len(data)
        
        return f"""Checkout Report ({period.title()}):
Total Checkouts: {total_checkouts}
Assets Checked Out: {assets_used}
Average Checkouts per Asset: {total_checkouts / assets_used if assets_used > 0 else 0:.1f}

Most Active Assets: {', '.join(d['asset'] for d in sorted(data, key=lambda x: x['total_checkouts'], reverse=True)[:3])}
"""


# Export all generator classes
__all__ = [
    'ReportGenerator',
    'AutomatedReportGenerator',
    'InventoryReportGenerator',
    'AssetReportGenerator',
    'AuditReportGenerator',
    'DepreciationReportGenerator',
    'MaintenanceReportGenerator',
    'CheckoutReportGenerator'
]
