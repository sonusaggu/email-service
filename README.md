# Email Service Microservice

A standalone email microservice that can be deployed on Railway (or any platform) to handle all email sending operations using Google SMTP (Gmail).

## Features

- ✅ Google SMTP (Gmail) integration
- ✅ RESTful API endpoints
- ✅ API key authentication
- ✅ Ready for Railway deployment
- ✅ Health check endpoint
- ✅ Specialized endpoints for common email types
- ✅ HTML and plain text email support
- ✅ Simple and lightweight

## Quick Setup on Railway

1. **Create a new Railway project**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo" or "Empty Project"

2. **Set up Google SMTP (Gmail)**
   
   **Step 1: Get Gmail App Password**
   - Go to https://myaccount.google.com/
   - Security → 2-Step Verification (enable if not enabled)
   - Security → App passwords
   - Generate app password for "Mail"
   - Copy the 16-character password

   **Step 2: Add Environment Variables in Railway**
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USE_TLS=true
   SMTP_USER=your_gmail@gmail.com
   SMTP_PASSWORD=your_16_char_app_password
   SMTP_FROM_EMAIL=your_gmail@gmail.com
   SMTP_FROM_NAME=StockFolio
   EMAIL_SERVICE_API_KEY=your_secret_api_key_here
   REQUIRE_AUTH=true
   ```

3. **Deploy**
   - Railway will automatically detect the `Procfile` and deploy
   - Or use: `railway up`

## API Endpoints

### Health Check
```
GET /health
```
Returns service status.

### Send Generic Email
```
POST /send
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "to": "user@example.com",
  "subject": "Test Email",
  "html": "<h1>Hello</h1><p>This is a test email.</p>",
  "text": "Hello\n\nThis is a test email."
}
```

### Send Verification Email
```
POST /send-verification
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "to": "user@example.com",
  "verification_url": "https://yourdomain.com/verify-email/token123",
  "username": "John Doe"
}
```

### Send Password Reset
```
POST /send-password-reset
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "to": "user@example.com",
  "reset_url": "https://yourdomain.com/password-reset/token123",
  "username": "John Doe"
}
```

### Send Dividend Alert
```
POST /send-dividend-alert
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "to": "user@example.com",
  "stock_symbol": "AAPL",
  "dividend_date": "2025-12-01",
  "dividend_amount": "0.24",
  "days_advance": 7
}
```

## Email Service Configuration

### Google SMTP (Gmail) - The Only Method ✅
- **Free**: Unlimited (Gmail account limits apply)
- **Setup**: Use Gmail App Password
- **Required Variables**:
  ```
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USE_TLS=true
  SMTP_USER=your_gmail@gmail.com
  SMTP_PASSWORD=your_16_char_app_password
  SMTP_FROM_EMAIL=your_gmail@gmail.com
  SMTP_FROM_NAME=StockFolio
  ```
- **How to get Gmail App Password**:
  1. Go to https://myaccount.google.com/security
  2. Enable 2-Step Verification (if not already enabled)
  3. Go to App passwords
  4. Select "Mail" and your device
  5. Generate and copy the 16-character password
  6. Use this password (NOT your regular Gmail password) in `SMTP_PASSWORD`

## Integration with Django

Update your Django app to use this service:

1. **Add to Render Dashboard environment variables**:
   ```
   EMAIL_SERVICE_URL=https://your-email-service.railway.app
   EMAIL_SERVICE_API_KEY=your_secret_key_here
   ```

2. **Update your Django email utilities** to use the service:
   ```python
   from portfolio.utils.email_service_client import send_email_via_service
   
   # Use service if configured, otherwise use local
   if USE_EMAIL_SERVICE:
       return send_email_via_service(...)
   else:
       # Use local email service
   ```

3. **Example usage in Django**:
   ```python
   import requests
   
   EMAIL_SERVICE_URL = "https://your-email-service.railway.app"
   EMAIL_SERVICE_API_KEY = "your_secret_api_key"
   
   def send_email_via_service(to_email, subject, html_content, text_content=None):
       response = requests.post(
           f"{EMAIL_SERVICE_URL}/send",
           headers={
               "Authorization": f"Bearer {EMAIL_SERVICE_API_KEY}",
               "Content-Type": "application/json"
           },
           json={
               "to": to_email,
               "subject": subject,
               "html": html_content,
               "text": text_content
           },
           timeout=10
       )
       return response.status_code == 200
   ```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables for Google SMTP
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USE_TLS=true
export SMTP_USER=your_gmail@gmail.com
export SMTP_PASSWORD=your_16_char_app_password
export SMTP_FROM_EMAIL=your_gmail@gmail.com
export SMTP_FROM_NAME=StockFolio
export EMAIL_SERVICE_API_KEY=test_key
export REQUIRE_AUTH=false

# Run locally
python app.py
# or
gunicorn app:app
```

### Test Email Sending

```bash
# Test the health endpoint
curl http://localhost:5000/health

# Test sending an email
curl -X POST http://localhost:5000/send \
  -H "Authorization: Bearer test_key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "test@example.com",
    "subject": "Test Email",
    "html": "<h1>Hello</h1><p>This is a test email.</p>",
    "text": "Hello\n\nThis is a test email."
  }'
```

## Benefits

1. **Separation of Concerns**: Email logic separate from main app
2. **Scalability**: Can scale email service independently
3. **Reliability**: Google SMTP is highly reliable
4. **Reusability**: Can be used by multiple applications
5. **Easy Updates**: Update email templates without redeploying main app
6. **Cost Effective**: Free with Gmail account
7. **Simple**: No complex API integrations, just SMTP

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Email sent successfully",
  "service_used": "smtp",
  "to": "user@example.com"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message here",
  "to": "user@example.com"
}
```

## Troubleshooting

### SMTP Authentication Failed
- Make sure you're using an App Password, not your regular Gmail password
- Verify 2-Step Verification is enabled
- Check that the App Password is correct (16 characters, no spaces)

### Connection Timeout
- Verify `SMTP_HOST` is set to `smtp.gmail.com`
- Check `SMTP_PORT` is `587` (for TLS) or `465` (for SSL)
- Ensure `SMTP_USE_TLS` is `true` for port 587

### Emails Not Sending
- Check Railway logs for detailed error messages
- Verify all environment variables are set correctly
- Test with the health endpoint first
- Try sending a test email using curl

## Security Notes

- Always use `REQUIRE_AUTH=true` in production
- Use a strong `EMAIL_SERVICE_API_KEY`
- Never commit API keys or passwords to version control
- Use Railway's environment variable encryption
- Consider rate limiting for production use

## License

This service is part of the StockFolio project.
