def send_email(sender, recipient, subject, body, smtp_server='smtp.gmail.com', port=587, password=None):
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            if password:
                server.login(sender, password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

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