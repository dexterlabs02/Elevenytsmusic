# 🔐 Security Best Practices for Grace Music Bot

## ⚠️ CRITICAL: Credential Security

### 🚨 NEVER Share These:
- Bot token
- API ID and Hash
- AWS access keys
- MongoDB connection strings
- Userbot session strings
- API credentials

### ✅ DO This Immediately:

If you've exposed credentials:
1. **Bot Token**: Message [@BotFather](https://t.me/BotFather) → `/revoke` → Create new token
2. **AWS Keys**: Go to IAM console → Deactivate exposed keys → Create new ones
3. **Sensitive Info**: Delete from message history

---

## 🛡️ Environment Variable Security

### ✅ Correct Way:
```bash
# .env file (NEVER commit to Git)
API_ID=12345
BOT_TOKEN=123456:XXXXXXXXX
AWS_SECRET_KEY=xxxxxxxx

# .gitignore (ensure these files are ignored)
.env
.env.*
*.env
```

### ❌ Wrong Way:
```bash
# DON'T do this:
export BOT_TOKEN="123456:XXXXXXXXX"  # Visible in shell history
python -m GraceMusic --token="123456:XXXXXXXXX"  # In command line
# Hardcode in source files
# Share in screenshots/messages
```

---

## 📋 Pre-Deployment Checklist

- [ ] `.env` file is in `.gitignore`
- [ ] No credentials in source code comments
- [ ] No credentials in Git history
- [ ] All secrets in `.env` file only
- [ ] `.env` is NOT committed to repository
- [ ] Used environment variables in code, not hardcoded values
- [ ] Created strong, unique bot credentials
- [ ] Used IAM user (not root) for AWS access
- [ ] Tested bot on local machine before deployment
- [ ] Removed any test credentials from code
- [ ] Database access limited by IP/firewall
- [ ] Used HTTPS everywhere
- [ ] Enable 2FA on service accounts

---

## 🔑 Access Key Management

### For MongoDB Atlas:
```bash
# Use IP Whitelist
- Add your server's IP only
- Monitor access logs
- Rotate credentials quarterly
```

### For AWS:
```bash
# Use IAM Policies (least privilege)
- Only AmazonDynamoDBFullAccess for DynamoDB
- Consider read-only policy for backups
- Enable CloudTrail for auditing
- Rotate keys every 90 days
```

### For Telegram:
```bash
# Use per-bot credentials
- Each bot: own API credentials
- Revoke lost credentials immediately
- Use userbot sessions carefully
```

---

## 🚫 Common Security Mistakes

### ❌ Mistake 1: Credentials in Logs
```python
# BAD
logger.info(f"Connecting: {config.MONGO_URL}")

# GOOD
logger.info("Connecting to MongoDB...")
```

### ❌ Mistake 2: Credentials in Error Messages
```python
# BAD
except Exception as e:
    logger.error(f"Connection failed with token: {self.BOT_TOKEN}")

# GOOD
except Exception as e:
    logger.error("Connection to Telegram API failed")
```

### ❌ Mistake 3: Storing Credentials in Database
```python
# BAD
db.save_user({"user_id": 123, "token": user_token})

# GOOD - Only store non-sensitive ID
db.save_user({"user_id": 123, "username": "username"})
```

### ❌ Mistake 4: Hardcoded Fallbacks
```python
# BAD
API_ID = getenv("API_ID", "123456789")  # Default exposed

# GOOD
if not API_ID:
    raise SystemExit("API_ID not set in .env")
```

---

## 📊 Audit Logging

### Enable for Production:
```python
# Log important events (NO sensitive data)
logger.info("User joined group")
logger.info("Broadcast sent to 50 chats")
logger.warning("Failed to play media - invalid URL")

# Monitor for suspicious activity:
# - Repeated failed authentication
# - Unusual API calls
# - Large data transfers
# - Access from new IPs
```

---

## 🔍 Code Review Checklist

Before pushing code:

1. **No Hardcoded Secrets**
   ```bash
   grep -r "token\|password\|key\|secret" --include="*.py" | grep -v getenv
   ```

2. **Proper Error Handling**
   - Don't expose sensitive info in exceptions
   - Log generically, debug specifically

3. **Input Validation**
   - Sanitize user input
   - Validate file uploads
   - Check message content

4. **Rate Limiting**
   - Prevent bot API abuse
   - Implement request throttling
   - Set command cooldowns

5. **Permission Checks**
   - Verify admin status
   - Check user authorization
   - Validate chat permissions

---

## 🚨 Incident Response

### If Credentials are Exposed:

**Immediate (< 5 min):**
1. Disable the credential
2. Generate new credential
3. Update .env file
4. Restart bot

**Short-term (< 1 hour):**
1. Review access logs
2. Check for unauthorized usage
3. Monitor bot activity
4. Alert team members

**Medium-term (< 1 day):**
1. Post-mortem analysis
2. Update security procedures
3. Add detection alerts
4. Document incident

**Long-term:**
1. Implement automation
2. Add security scanning
3. Regular security audits
4. Team security training

---

## 🔐 Database Security

### MongoDB Atlas:
```bash
# Security settings:
- Enable encryption at rest
- Use VPC/Network peering
- IP whitelist only allowed IPs
- Enable authentication
- Use strong passwords (20+ chars)
- Enable audit logging
- Enable access control
```

### DynamoDB:
```bash
# Security settings:
- Use IAM roles (not access keys in code)
- Enable encryption (KMS)
- Enable point-in-time recovery
- CloudTrail logging
- VPC endpoints (private access)
- Resource-based policies
```

---

## ✅ Production Deployment Checklist

Database Security:
- [ ] Encryption enabled
- [ ] Backups configured
- [ ] Access logging enabled
- [ ] IP whitelisting active
- [ ] Strong authentication passwords
- [ ] Regular backups tested

Bot Security:
- [ ] All credentials in .env
- [ ] .env in .gitignore
- [ ] Error handling doesn't leak info
- [ ] Input validation implemented
- [ ] Rate limiting enabled
- [ ] Admin checks on restricted commands
- [ ] Audit logging active

Infrastructure:
- [ ] Firewall configured
- [ ] SSL/TLS enabled
- [ ] DDoS protection
- [ ] Monitoring/alerting setup
- [ ] Backup/recovery plan
- [ ] Disaster recovery tested

---

## 🛠️ Security Tools

### Scanning Tools:
```bash
# Check for secrets in code
pip install detect-secrets
detect-secrets scan

# Find hardcoded credentials
pip install truffleHog
truffleHog filesystem .

# Dependency vulnerabilities
pip install safety
safety check

# SAST (Static Application Security Testing)
pip install bandit
bandit -r GraceMusic/
```

### Monitoring:
- CloudWatch (AWS monitoring)
- MongoDB Atlas monitoring
- Bot activity logs
- Error tracking (Sentry)
- Performance monitoring

---

## 📞 Security Contacts

- **Telegram Support**: [@t.me](https://t.me)
- **AWS Security**: https://aws.amazon.com/security/
- **MongoDB Security**: https://docs.mongodb.com/manual/security/
- **Python Security**: https://python-security.readthedocs.io/

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [AWS Security Best Practices](https://docs.aws.amazon.com/security/)
- [Python Security](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [Telegram Bot Security](https://core.telegram.org/bots/security)

---

**Remember**: Security is not a one-time task, it's continuous!

Last Updated: April 2024
