"""
Helper utilities for enhanced user feedback and smart defaults
"""
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import re

def get_user_friendly_error(error, field_name=None):
    """
    Convert technical error messages to user-friendly guidance.
    
    Args:
        error: The exception or error message
        field_name: Optional name of the field that caused the error
        
    Returns:
        str: User-friendly error message with guidance
    """
    error_str = str(error).lower()
    field = field_name or "This field"
    
    # Database errors
    if "duplicate entry" in error_str or "unique constraint" in error_str:
        return f"❌ {field} already exists. Please use a different value."
    
    if "foreign key constraint" in error_str:
        return f"❌ Cannot complete this action because {field.lower()} is referenced by other records. Please remove related items first."
    
    if "cannot be null" in error_str or "not null constraint" in error_str:
        return f"⚠️ {field} is required. Please provide a value."
    
    # Data type errors
    if "invalid literal" in error_str or "could not convert" in error_str:
        if "int" in error_str:
            return f"⚠️ {field} must be a whole number (e.g., 10, 25, 100)."
        elif "float" in error_str or "decimal" in error_str:
            return f"⚠️ {field} must be a number (e.g., 10.5, 25, 100.75)."
        elif "date" in error_str or "datetime" in error_str:
            return f"⚠️ {field} must be a valid date (e.g., 2025-01-15 or 01/15/2025)."
    
    # Value errors
    if "value error" in error_str:
        if "date" in error_str or "time" in error_str:
            return f"⚠️ Please enter a valid date and time format (e.g., 2025-11-04 14:30)."
        return f"⚠️ Invalid value for {field.lower()}. Please check your input and try again."
    
    # File upload errors
    if "file" in error_str and ("size" in error_str or "too large" in error_str):
        return f"⚠️ File is too large. Maximum file size is 10 MB. Please choose a smaller file."
    
    if "file" in error_str and ("extension" in error_str or "format" in error_str):
        return f"⚠️ Invalid file format. Please upload a file with the correct extension (e.g., .pdf, .jpg, .xlsx)."
    
    # Permission errors
    if "permission denied" in error_str or "access denied" in error_str:
        return f"🔒 You don't have permission to perform this action. Please contact your administrator."
    
    # Connection errors
    if "connection" in error_str or "timeout" in error_str:
        return f"⚠️ Connection issue. Please check your internet connection and try again."
    
    # Default friendly message
    if field_name:
        return f"⚠️ There was a problem with {field.lower()}. Please check your input and try again."
    return f"⚠️ An error occurred. Please check your input and try again."


def validate_number(value, field_name="Number", min_val=None, max_val=None, allow_decimal=True):
    """
    Validate and convert a number with user-friendly error messages.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        allow_decimal: Whether to allow decimal values
        
    Returns:
        tuple: (is_valid, value_or_error_message)
    """
    if not value or str(value).strip() == "":
        return False, f"⚠️ {field_name} is required."
    
    try:
        if allow_decimal:
            num = float(value)
            if '.' in str(value) and len(str(value).split('.')[1]) > 2:
                return False, f"⚠️ {field_name} can have at most 2 decimal places (e.g., 10.50 or 25.99)."
        else:
            if '.' in str(value):
                return False, f"⚠️ {field_name} must be a whole number (e.g., 10, 25, 100)."
            num = int(value)
        
        if min_val is not None and num < min_val:
            return False, f"⚠️ {field_name} must be at least {min_val}."
        
        if max_val is not None and num > max_val:
            return False, f"⚠️ {field_name} must be no more than {max_val}."
        
        return True, num
    
    except (ValueError, TypeError):
        example = "10.50 or 25" if allow_decimal else "10 or 25"
        return False, f"⚠️ {field_name} must be a valid number (e.g., {example})."


def validate_email(email):
    """
    Validate email with user-friendly error message.
    
    Returns:
        tuple: (is_valid, error_message_or_none)
    """
    if not email or not email.strip():
        return False, "⚠️ Email address is required."
    
    email = email.strip()
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "⚠️ Please enter a valid email address (e.g., user@example.com)."
    
    return True, None


def validate_phone(phone):
    """
    Validate phone number with user-friendly error message.
    
    Returns:
        tuple: (is_valid, error_message_or_none)
    """
    if not phone or not phone.strip():
        return False, "⚠️ Phone number is required."
    
    phone = phone.strip()
    # Allow digits, spaces, hyphens, parentheses, and plus sign
    phone_pattern = r'^[\d\s\-\+\(\)]+$'
    
    if not re.match(phone_pattern, phone):
        return False, "⚠️ Please enter a valid phone number (e.g., +1-234-567-8900 or (123) 456-7890)."
    
    # Check minimum length
    digits_only = re.sub(r'\D', '', phone)
    if len(digits_only) < 10:
        return False, "⚠️ Phone number must be at least 10 digits long."
    
    return True, None


def validate_date(date_str, field_name="Date", allow_future=True, allow_past=True):
    """
    Validate date with user-friendly error message.
    
    Returns:
        tuple: (is_valid, date_object_or_error_message)
    """
    if not date_str or not str(date_str).strip():
        return False, f"⚠️ {field_name} is required."
    
    try:
        # Try to parse the date
        if isinstance(date_str, (date, datetime)):
            parsed_date = date_str if isinstance(date_str, date) else date_str.date()
        else:
            # Try common formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    parsed_date = datetime.strptime(str(date_str).strip(), fmt).date()
                    break
                except ValueError:
                    continue
            else:
                return False, f"⚠️ {field_name} must be in format YYYY-MM-DD (e.g., 2025-11-04) or MM/DD/YYYY."
        
        today = date.today()
        
        if not allow_future and parsed_date > today:
            return False, f"⚠️ {field_name} cannot be in the future. Please select today or an earlier date."
        
        if not allow_past and parsed_date < today:
            return False, f"⚠️ {field_name} cannot be in the past. Please select today or a later date."
        
        return True, parsed_date
    
    except Exception as e:
        return False, f"⚠️ Invalid date format for {field_name}. Please use YYYY-MM-DD (e.g., 2025-11-04)."


def get_smart_default(field_type, **kwargs):
    """
    Get smart default values for common form fields.
    
    Args:
        field_type: Type of field ('date', 'datetime', 'user', 'status', etc.)
        **kwargs: Additional parameters for customization
        
    Returns:
        Appropriate default value
    """
    if field_type == 'date':
        return date.today()
    
    elif field_type == 'datetime':
        return datetime.now()
    
    elif field_type == 'status':
        return kwargs.get('default_status', 'Active')
    
    elif field_type == 'quantity':
        return 1
    
    elif field_type == 'condition':
        return kwargs.get('default_condition', 'Good')
    
    elif field_type == 'currency':
        return '0.00'
    
    return None


def format_success_message(action, item_name=None, details=None):
    """
    Format a consistent success message.
    
    Args:
        action: The action performed ('created', 'updated', 'deleted', etc.)
        item_name: Optional name of the item
        details: Optional additional details
        
    Returns:
        str: Formatted success message
    """
    actions = {
        'created': '✅ Successfully created',
        'added': '✅ Successfully added',
        'updated': '✅ Successfully updated',
        'deleted': '✅ Successfully deleted',
        'saved': '✅ Successfully saved',
        'imported': '✅ Successfully imported',
        'exported': '✅ Successfully exported',
        'assigned': '✅ Successfully assigned',
        'checked_out': '✅ Successfully checked out',
        'checked_in': '✅ Successfully checked in',
        'reserved': '✅ Successfully reserved',
        'moved': '✅ Successfully moved',
        'disposed': '✅ Successfully disposed',
        'backed_up': '✅ Successfully backed up',
        'restored': '✅ Successfully restored',
    }
    
    message = actions.get(action, f'✅ {action.capitalize()} successfully')
    
    if item_name:
        message += f' {item_name}'
    
    if details:
        message += f'. {details}'
    else:
        message += '!'
    
    return message


def format_warning_message(message, suggestion=None):
    """
    Format a warning message with optional suggestion.
    
    Returns:
        str: Formatted warning message
    """
    warning = f"⚠️ {message}"
    if suggestion:
        warning += f" {suggestion}"
    return warning


def format_info_message(message):
    """
    Format an informational message.
    
    Returns:
        str: Formatted info message
    """
    return f"ℹ️ {message}"


def get_field_suggestions(field_name):
    """
    Get helpful suggestions for common field types.
    
    Returns:
        str: Suggestion text or empty string
    """
    suggestions = {
        'asset_tag': 'Use a unique identifier like AST-001 or TAG-2025-001',
        'serial_number': 'Usually found on a label or sticker on the device',
        'purchase_price': 'Enter the amount in dollars (e.g., 1500.00)',
        'quantity': 'Enter a whole number (e.g., 1, 5, 10)',
        'email': 'Must be a valid email format (e.g., user@example.com)',
        'phone': 'Include area code (e.g., +1-234-567-8900)',
        'date': 'Use format YYYY-MM-DD (e.g., 2025-11-04)',
        'warranty_expiry': 'Usually 1-3 years from purchase date',
        'useful_life': 'Typical useful life: Computers 3-5 years, Furniture 7-10 years',
    }
    
    return suggestions.get(field_name.lower(), '')


# Example usage in routes:
"""
from utils.feedback import (
    get_user_friendly_error,
    validate_number,
    validate_email,
    format_success_message,
    get_smart_default
)

@app.route('/example', methods=['POST'])
def example():
    try:
        # Validate quantity
        is_valid, result = validate_number(
            request.form.get('quantity'),
            field_name='Quantity',
            min_val=1,
            allow_decimal=False
        )
        if not is_valid:
            flash(result, 'warning')
            return redirect(url_for('example'))
        
        quantity = result
        
        # Validate email
        is_valid, error = validate_email(request.form.get('email'))
        if not is_valid:
            flash(error, 'warning')
            return redirect(url_for('example'))
        
        # ... perform operation ...
        
        flash(format_success_message('created', 'Asset'), 'success')
        return redirect(url_for('assets'))
        
    except Exception as e:
        error_msg = get_user_friendly_error(e, 'Asset')
        flash(error_msg, 'error')
        return redirect(url_for('example'))
"""
