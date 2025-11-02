def send_email(sender, recipient, subject, body, smtp_server='smtp.gmail.com', port=587, password=None):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Create message with HTML support
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    
    # Create both plain text and HTML versions
    text_part = MIMEText(body, 'plain')
    html_body = body.replace('\n', '<br>')
    html_part = MIMEText(f'<html><body>{html_body}</body></html>', 'html')
    
    msg.attach(text_part)
    msg.attach(html_part)

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            if password:
                server.login(sender, password)
            server.send_message(msg)
        print(f"Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_asset_assignment_email(recipient_email, recipient_name, asset_name, asset_details, assigned_by, notes=None):
    """Send email notification when an asset is assigned to a user"""
    subject = f"Asset Assignment Notification: {asset_name}"
    
    body = f"""
Dear {recipient_name},

You have been assigned a new asset. Please review the details below:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ASSET DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Asset Name: {asset_name}
Category: {asset_details.get('category', 'N/A')}
Brand: {asset_details.get('brand', 'N/A')}
Model: {asset_details.get('model', 'N/A')}
Serial Number: {asset_details.get('serial_number', 'N/A')}
Department: {asset_details.get('department', 'N/A')}
Location: {asset_details.get('location', 'N/A')}

Assigned By: {assigned_by}
Assignment Date: {asset_details.get('assignment_date', 'N/A')}
"""
    
    if notes:
        body += f"\nAdditional Notes:\n{notes}\n"
    
    body += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT REMINDERS:
• Please take good care of this asset
• Report any issues or damages immediately
• Return the asset when required
• Contact IT department for technical support

This is an automated notification from the Asset Management System.
Please do not reply to this email.

Best regards,
Asset Management Team
"""
    
    # Get email configuration from database or config
    try:
        from config import EMAIL_CONFIG
        sender = EMAIL_CONFIG.get('sender_email')
        password = EMAIL_CONFIG.get('sender_password')
        smtp_server = EMAIL_CONFIG.get('smtp_server', 'smtp.gmail.com')
        port = EMAIL_CONFIG.get('smtp_port', 587)
        
        if sender and password and recipient_email:
            return send_email(sender, recipient_email, subject, body, smtp_server, port, password)
        else:
            print("Email configuration incomplete. Skipping email notification.")
            return False
    except Exception as e:
        print(f"Email notification failed: {e}")
        return False

def send_checkout_notification_email(recipient_email, recipient_name, item_name, quantity, checkout_details, notes=None):
    """Send email notification when items are checked out to a user"""
    subject = f"Asset Checkout Notification: {item_name}"
    
    body = f"""
Dear {recipient_name},

You have checked out the following item(s):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHECKOUT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Item Name: {item_name}
Quantity: {quantity}
Department: {checkout_details.get('department', 'N/A')}
Location: {checkout_details.get('location', 'N/A')}
Checkout Date: {checkout_details.get('checkout_date', 'N/A')}
Checked Out By: {checkout_details.get('checked_out_by', 'N/A')}
"""
    
    if notes:
        body += f"\nAdditional Notes:\n{notes}\n"
    
    body += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT REMINDERS:
• You are responsible for the checked out items
• Please return items when no longer needed
• Report any issues or damages immediately
• Keep items in good condition

This is an automated notification from the Asset Management System.
Please do not reply to this email.

Best regards,
Asset Management Team
"""
    
    # Get email configuration from database or config
    try:
        from config import EMAIL_CONFIG
        sender = EMAIL_CONFIG.get('sender_email')
        password = EMAIL_CONFIG.get('sender_password')
        smtp_server = EMAIL_CONFIG.get('smtp_server', 'smtp.gmail.com')
        port = EMAIL_CONFIG.get('smtp_port', 587)
        
        if sender and password and recipient_email:
            return send_email(sender, recipient_email, subject, body, smtp_server, port, password)
        else:
            print("Email configuration incomplete. Skipping email notification.")
            return False
    except Exception as e:
        print(f"Email notification failed: {e}")
        return False

def configure_email_settings():
    sender = input("Enter sender email: ")
    password = input("Enter sender email password: ")
    recipient = input("Enter recipient email: ")
    smtp_server = input("Enter SMTP server [default: smtp.gmail.com]: ") or 'smtp.gmail.com'
    port = input("Enter SMTP port [default: 587]: ") or 587

    return {
        'sender': sender,
        'password': password,
        'recipient': recipient,
        'smtp_server': smtp_server,
        'port': int(port)
    }
