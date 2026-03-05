"""Report generation utilities"""

from datetime import datetime, timedelta
from collections import defaultdict


def generate_inventory_report(system):
    """Generate comprehensive inventory report"""
    report_data = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_assets': len(system.inventory),
        'total_value': sum(asset.get('price', 0) * asset.get('quantity', 1) 
                          for asset in system.inventory.values()),
        'by_category': defaultdict(lambda: {'count': 0, 'value': 0}),
        'by_location': defaultdict(lambda: {'count': 0, 'value': 0}),
        'by_status': defaultdict(int),
        'assets': []
    }
    
    for name, asset in system.inventory.items():
        category = asset.get('category', 'Uncategorized')
        location = asset.get('location', 'Unknown')
        status = asset.get('status', 'Available')
        value = asset.get('price', 0) * asset.get('quantity', 1)
        
        report_data['by_category'][category]['count'] += 1
        report_data['by_category'][category]['value'] += value
        report_data['by_location'][location]['count'] += 1
        report_data['by_location'][location]['value'] += value
        report_data['by_status'][status] += 1
        
        report_data['assets'].append({
            'name': name,
            'category': category,
            'quantity': asset.get('quantity', 0),
            'price': asset.get('price', 0),
            'total_value': value,
            'location': location,
            'status': status
        })
    
    return report_data


def generate_depreciation_report(system, calculate_depreciation_func):
    """Generate asset depreciation report"""
    report_data = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'assets': [],
        'total_original_value': 0,
        'total_current_value': 0,
        'total_depreciation': 0
    }
    
    for name, asset in system.inventory.items():
        original_value = asset.get('price', 0)
        current_value = calculate_depreciation_func(
            original_value,
            asset.get('purchase_date'),
            asset.get('salvage_value', 0),
            asset.get('useful_life_years', 5),
            asset.get('depreciation_method', 'straight_line')
        )
        
        depreciation = original_value - current_value
        
        report_data['assets'].append({
            'name': name,
            'purchase_date': asset.get('purchase_date', ''),
            'original_value': original_value,
            'current_value': current_value,
            'depreciation': depreciation,
            'depreciation_percent': (depreciation / original_value * 100) if original_value > 0 else 0,
            'method': asset.get('depreciation_method', 'straight_line')
        })
        
        report_data['total_original_value'] += original_value
        report_data['total_current_value'] += current_value
        report_data['total_depreciation'] += depreciation
    
    return report_data


def generate_maintenance_report(maintenance_records):
    """Generate maintenance summary report"""
    report_data = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_records': len(maintenance_records),
        'by_status': defaultdict(int),
        'by_type': defaultdict(int),
        'total_cost': 0,
        'upcoming_count': 0,
        'overdue_count': 0,
        'records': []
    }
    
    today = datetime.now().date()
    
    for record in maintenance_records:
        status = record.get('status', 'Pending')
        mtype = record.get('maintenance_type', 'General')
        cost = record.get('cost', 0)
        
        report_data['by_status'][status] += 1
        report_data['by_type'][mtype] += 1
        report_data['total_cost'] += cost
        
        # Check if upcoming or overdue
        scheduled_date = record.get('scheduled_date')
        if scheduled_date:
            try:
                if isinstance(scheduled_date, str):
                    sched = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
                else:
                    sched = scheduled_date
                    
                if sched > today and status != 'Completed':
                    report_data['upcoming_count'] += 1
                elif sched < today and status != 'Completed':
                    report_data['overdue_count'] += 1
            except Exception:
                pass
        
        report_data['records'].append(record)
    
    return report_data


def generate_checkout_report(transactions):
    """Generate asset checkout report"""
    report_data = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_checkouts': 0,
        'active_checkouts': 0,
        'returned': 0,
        'by_user': defaultdict(int),
        'by_asset': defaultdict(int),
        'transactions': []
    }
    
    for transaction in transactions:
        if transaction.get('transaction_type') == 'check-out':
            report_data['total_checkouts'] += 1
            
            if not transaction.get('return_date'):
                report_data['active_checkouts'] += 1
            else:
                report_data['returned'] += 1
            
            username = transaction.get('username', 'Unknown')
            asset_name = transaction.get('asset_name', 'Unknown')
            
            report_data['by_user'][username] += 1
            report_data['by_asset'][asset_name] += 1
            report_data['transactions'].append(transaction)
    
    return report_data


def generate_alert_data(system):
    """Generate alert data for all alert types"""
    alerts = {
        'assets_past_due': [],
        'contracts_expiring': [],
        'leases_expiring': [],
        'maintenance_due': [],
        'maintenance_overdue': [],
        'warranties_expiring': []
    }
    
    today = datetime.now().date()
    thirty_days = today + timedelta(days=30)
    
    # Check warranties
    for name, asset in system.inventory.items():
        warranty_date = asset.get('warranty_date')
        if warranty_date:
            try:
                if isinstance(warranty_date, str):
                    warranty = datetime.strptime(warranty_date, '%Y-%m-%d').date()
                else:
                    warranty = warranty_date
                
                if today < warranty < thirty_days:
                    alerts['warranties_expiring'].append({
                        'asset_name': name,
                        'warranty_date': warranty,
                        'days_remaining': (warranty - today).days
                    })
            except Exception:
                pass
    
    return alerts


def format_currency(value):
    """Format value as currency"""
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return "$0.00"


def format_percentage(value):
    """Format value as percentage"""
    try:
        return f"{float(value):.2f}%"
    except Exception:
        return "0.00%"
