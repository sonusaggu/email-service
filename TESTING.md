# Testing Guide for Email Service

Quick reference for testing the email service after deployment.

## Prerequisites

- Email service deployed on Railway
- Service URL (e.g., `https://email-service.railway.app`)
- API key from Railway environment variables

## Test Commands

### 1. Health Check

```bash
curl https://your-email-service.railway.app/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "email-service",
  "timestamp": "2025-11-24T..."
}
```

### 2. Test Generic Email

```bash
curl -X POST https://your-email-service.railway.app/send \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "your_email@example.com",
    "subject": "Test Email",
    "html": "<h1>Hello</h1><p>This is a test email.</p>",
    "text": "Hello\n\nThis is a test email."
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Email sent successfully",
  "service_used": "smtp",
  "to": "your_email@example.com"
}
```

### 3. Test Verification Email

```bash
curl -X POST https://your-email-service.railway.app/send-verification \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "your_email@example.com",
    "verification_url": "https://dividend.forum/verify-email/token123/",
    "username": "John Doe"
  }'
```

### 4. Test Password Reset Email

```bash
curl -X POST https://your-email-service.railway.app/send-password-reset \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "your_email@example.com",
    "reset_url": "https://dividend.forum/password-reset-confirm/uid/token/",
    "username": "John Doe"
  }'
```

### 5. Test Dividend Alert

```bash
curl -X POST https://your-email-service.railway.app/send-dividend-alert \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "your_email@example.com",
    "stock_symbol": "AAPL",
    "dividend_date": "2025-12-01",
    "dividend_amount": "0.24",
    "dividend_currency": "USD",
    "days_advance": 7,
    "dividend_frequency": "Quarterly"
  }'
```

## Testing from Django

### Test Email Service Client

```python
# In Django shell: python manage.py shell
from portfolio.utils.email_service_client import send_email_via_service

success, message = send_email_via_service(
    to_email="test@example.com",
    subject="Django Test",
    html_content="<h1>Test</h1>",
    text_content="Test"
)
print(f"Success: {success}, Message: {message}")
```

### Test Email Verification

```python
from django.contrib.auth.models import User
from portfolio.utils.email_verification import send_verification_email, create_verification_token

user = User.objects.get(email="test@example.com")
verification = create_verification_token(user)
success = send_verification_email(user, verification.token)
print(f"Verification email sent: {success}")
```

### Test Password Reset

1. Go to your Django app: `https://dividend.forum/password-reset/`
2. Enter your email
3. Check if email arrives
4. Check Railway logs to confirm email was sent via Railway service

## Common Errors and Fixes

### Error: 401 Unauthorized

**Cause**: Wrong API key or missing Authorization header

**Fix**:
```bash
# Verify API key matches in Railway and Django
# Check header format: Authorization: Bearer YOUR_KEY
```

### Error: 500 Internal Server Error

**Cause**: SMTP configuration issue

**Fix**:
- Check Railway logs for detailed error
- Verify Gmail App Password is correct
- Ensure `SMTP_USER` and `SMTP_PASSWORD` are set

### Error: Connection Timeout

**Cause**: Railway service not running or wrong URL

**Fix**:
- Check Railway dashboard - is service deployed?
- Verify service URL is correct
- Check Railway service logs

## Monitoring

### Check Railway Logs

1. Railway Dashboard → Your Service → **Deployments** → **View Logs**
2. Look for:
   - `Email sent via SMTP to ...` (success)
   - `SMTP authentication failed` (error)
   - `SMTP error: ...` (error)

### Check Django Logs

1. Render Dashboard → Your Service → **Logs**
2. Look for:
   - `Email sent via Railway service to ...` (using Railway)
   - `Railway email service failed, falling back to SMTP` (fallback)
   - `Email sent via SMTP to ...` (using local SMTP)

## Automated Testing Script

Create a test script:

```bash
#!/bin/bash
# test-email-service.sh

SERVICE_URL="https://your-email-service.railway.app"
API_KEY="your_api_key_here"
TEST_EMAIL="your_email@example.com"

echo "Testing Email Service..."
echo ""

# Health check
echo "1. Health Check:"
curl -s "$SERVICE_URL/health" | jq .
echo ""

# Send test email
echo "2. Sending Test Email:"
curl -s -X POST "$SERVICE_URL/send" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"to\": \"$TEST_EMAIL\",
    \"subject\": \"Automated Test\",
    \"html\": \"<h1>Test</h1><p>Automated test email.</p>\",
    \"text\": \"Test\n\nAutomated test email.\"
  }" | jq .

echo ""
echo "Check $TEST_EMAIL for the test email!"
```

Save as `test-email-service.sh`, make executable:
```bash
chmod +x test-email-service.sh
./test-email-service.sh
```

## Success Criteria

✅ Health check returns 200
✅ Test emails arrive in inbox
✅ No errors in Railway logs
✅ Django logs show Railway service usage
✅ All email types work (verification, password reset, alerts)

