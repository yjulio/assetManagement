# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please email security@vbos.gov.vu with details. We will respond within 48 hours.

**Please do NOT open public issues for security vulnerabilities.**

## Security Features

### Authentication & Authorization
- ✅ Password hashing with bcrypt
- ✅ Session management with secure cookies
- ✅ CSRF protection on all forms
- ✅ Role-based access control (Admin, Manager, User)

### Data Protection
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS protection (input sanitization)
- ✅ HTTPS enforcement in production
- ✅ Secure session cookies (HttpOnly, Secure, SameSite)

### Network Security
- ✅ Rate limiting (200 requests/hour default)
- ✅ Security headers (Flask-Talisman)
- ✅ File upload restrictions (type, size validation)

### Database Security
- ✅ Connection pooling
- ✅ Prepared statements
- ✅ Encrypted credentials
- ✅ Regular backup system

## Security Best Practices

### For Administrators

1. **Strong Passwords**
   - Minimum 12 characters
   - Mix of uppercase, lowercase, numbers, special characters
   - Change default passwords immediately

2. **Environment Variables**
   - Never commit `.env` to version control
   - Use strong random `SECRET_KEY`
   - Rotate credentials regularly (every 90 days)

3. **HTTPS Configuration**
   - Always use HTTPS in production
   - Configure SSL/TLS certificates properly
   - Set `FORCE_HTTPS=true` in `.env`

4. **Regular Updates**
   - Keep Python dependencies updated
   - Monitor security advisories
   - Apply security patches promptly

5. **Access Control**
   - Limit admin account creation
   - Review user permissions regularly
   - Disable unused accounts

6. **Backup Security**
   - Store backups securely off-site
   - Encrypt sensitive backups
   - Test restore procedures regularly

7. **Monitoring**
   - Enable query logging in production
   - Monitor failed login attempts
   - Set up alerts for suspicious activity

### For Developers

1. **Code Security**
   ```python
   # ✅ GOOD - Parameterized query
   cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
   
   # ❌ BAD - SQL injection vulnerable
   cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
   ```

2. **Input Validation**
   ```python
   # ✅ GOOD - Validate and sanitize
   from flask_wtf import FlaskForm
   from wtforms.validators import DataRequired, Length
   
   class LoginForm(FlaskForm):
       username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
   ```

3. **CSRF Protection**
   ```html
   <!-- ✅ GOOD - Include CSRF token -->
   <form method="post">
       <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
   </form>
   ```

4. **File Uploads**
   ```python
   # ✅ GOOD - Validate file type and size
   ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
   MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
   
   def allowed_file(filename):
       return '.' in filename and \
              filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
   ```

## Deployment Checklist

Before deploying to production, ensure:

- [ ] `FLASK_DEBUG=false` in `.env`
- [ ] Strong `SECRET_KEY` generated and set
- [ ] Database password changed from default
- [ ] HTTPS/SSL configured and enforced
- [ ] `SESSION_COOKIE_SECURE=true`
- [ ] Rate limiting enabled
- [ ] File upload directory has proper permissions (chmod 755)
- [ ] Database backups configured
- [ ] Error logging enabled
- [ ] Security headers configured
- [ ] All default accounts disabled or removed
- [ ] Firewall rules configured
- [ ] Redis configured for rate limiting (not memory://)
- [ ] Regular security updates scheduled

## Common Vulnerabilities & Mitigations

### SQL Injection
**Status:** ✅ Mitigated
- All queries use parameterized statements
- No string concatenation in queries

### Cross-Site Scripting (XSS)
**Status:** ✅ Mitigated
- Flask auto-escapes templates
- CSRF tokens on all forms
- Content Security Policy headers

### Cross-Site Request Forgery (CSRF)
**Status:** ✅ Mitigated
- Flask-WTF CSRF protection enabled
- Tokens required on all POST requests

### Session Hijacking
**Status:** ✅ Mitigated
- Secure, HttpOnly, SameSite cookies
- Session timeout (1 hour default)
- HTTPS enforcement

### Brute Force Attacks
**Status:** ✅ Mitigated
- Rate limiting (200 req/hour)
- Account lockout after failed attempts
- Login attempt logging

### File Upload Attacks
**Status:** ✅ Mitigated
- File type whitelist
- File size limits (16MB default)
- Secure file storage

## Security Configuration Examples

### Production `.env`
```bash
FLASK_DEBUG=false
SECRET_KEY=<64-char-random-hex-string>
DB_PASSWORD=<strong-password-16+chars>
FORCE_HTTPS=true
RATELIMIT_ENABLED=true
REDIS_URL=redis://localhost:6379/0
WTF_CSRF_SSL_STRICT=true
SESSION_LIFETIME=3600
```

### Nginx Security Headers
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Database User Permissions
```sql
-- Create restricted user
CREATE USER 'user_asset'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON db_asset.* TO 'user_asset'@'localhost';
FLUSH PRIVILEGES;

-- Do NOT grant: DROP, CREATE, ALTER, GRANT OPTION
```

## Incident Response

If you detect a security incident:

1. **Immediate Actions**
   - Disconnect affected systems from network
   - Preserve logs and evidence
   - Change all passwords and secrets
   - Notify security team

2. **Investigation**
   - Review logs for entry point
   - Identify compromised data
   - Assess impact scope

3. **Recovery**
   - Patch vulnerabilities
   - Restore from clean backup
   - Update security measures

4. **Post-Incident**
   - Document lessons learned
   - Update security procedures
   - Notify affected parties if required

## Security Contacts

- **Security Team:** security@vbos.gov.vu
- **Emergency Contact:** +678-23450
- **Report Vulnerabilities:** https://vbos.gov.vu/security

## Updates & Changelog

This security policy was last updated: November 3, 2025

### Recent Security Updates
- Added Flask-Talisman for security headers
- Implemented rate limiting
- Enhanced session security
- Added connection pooling
- Improved input validation

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [Python Security](https://python.readthedocs.io/en/latest/library/security_warnings.html)
