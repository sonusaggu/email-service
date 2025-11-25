"""
Standalone Email Service for Railway
A microservice that handles all email sending operations
Can be called by any application via REST API
Uses Google SMTP (Gmail) for email delivery
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Authentication
API_KEY = os.environ.get('EMAIL_SERVICE_API_KEY', '')
REQUIRE_AUTH = os.environ.get('REQUIRE_AUTH', 'true').lower() == 'true'

# Google SMTP Configuration
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'true').lower() == 'true'
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL', '')
SMTP_FROM_NAME = os.environ.get('SMTP_FROM_NAME', 'StockFolio')


def require_auth(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if REQUIRE_AUTH:
            auth_header = request.headers.get('Authorization')
            if not auth_header or auth_header != f'Bearer {API_KEY}':
                return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


def send_email_via_smtp(to_email, subject, html_content, text_content=None):
    """Send email via Google SMTP (PRIMARY METHOD)"""
    if not SMTP_USER or not SMTP_PASSWORD or not SMTP_FROM_EMAIL:
        return False, "SMTP not configured"
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        
        # Add text and HTML parts
        if text_content:
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Connect to SMTP server
        if SMTP_USE_TLS:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        
        # Login and send
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent via SMTP to {to_email}")
        return True, "Success"
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        return False, f"SMTP authentication failed: {str(e)}"
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        logger.error(f"SMTP error: {e}")
        return False, str(e)


def send_email(to_email, subject, html_content, text_content=None):
    """Send email via Google SMTP"""
    return send_email_via_smtp(to_email, subject, html_content, text_content)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'email-service',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/send', methods=['POST'])
@require_auth
def send_email_endpoint():
    """Main email sending endpoint"""
    try:
        data = request.json
        
        # Validate required fields
        if not data or 'to' not in data or 'subject' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: to, subject'
            }), 400
        
        to_email = data['to']
        subject = data['subject']
        html_content = data.get('html', '')
        text_content = data.get('text', '')
        
        # Send email
        success, message, service_used = send_email(to_email, subject, html_content, text_content)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Email sent successfully',
                'service_used': 'smtp',
                'to': to_email
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message,
                'to': to_email
            }), 500
            
    except Exception as e:
        logger.error(f"Error in send_email_endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/send-verification', methods=['POST'])
@require_auth
def send_verification_email():
    """Send email verification email"""
    try:
        data = request.json
        
        if not data or 'to' not in data or 'verification_url' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: to, verification_url'
            }), 400
        
        to_email = data['to']
        verification_url = data['verification_url']
        username = data.get('username', 'User')
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Verify Your StockFolio Account</h2>
            <p>Hello {username},</p>
            <p>Thank you for signing up! Please verify your email address by clicking the button below:</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Verify Email Address
                </a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #666;">{verification_url}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create an account, please ignore this email.</p>
            <p>Best regards,<br>StockFolio Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Verify Your StockFolio Account
        
        Hello {username},
        
        Thank you for signing up! Please verify your email address by visiting:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        StockFolio Team
        """
        
        success, message = send_email(
            to_email, 
            'Verify Your StockFolio Account',
            html_content,
            text_content
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Verification email sent',
                'service_used': 'smtp'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 500
            
    except Exception as e:
        logger.error(f"Error in send_verification_email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/send-password-reset', methods=['POST'])
@require_auth
def send_password_reset():
    """Send password reset email"""
    try:
        data = request.json
        
        if not data or 'to' not in data or 'reset_url' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: to, reset_url'
            }), 400
        
        to_email = data['to']
        reset_url = data['reset_url']
        username = data.get('username', 'User')
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Reset Your Password</h2>
            <p>Hello {username},</p>
            <p>You requested to reset your password. Click the button below to create a new password:</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background-color: #2196F3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #666;">{reset_url}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't request this, please ignore this email. Your password will remain unchanged.</p>
            <p>Best regards,<br>StockFolio Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Reset Your Password
        
        Hello {username},
        
        You requested to reset your password. Visit this link to create a new password:
        {reset_url}
        
        This link will expire in 24 hours.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        StockFolio Team
        """
        
        success, message = send_email(
            to_email,
            'Reset Your StockFolio Password',
            html_content,
            text_content
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Password reset email sent',
                'service_used': 'smtp'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 500
            
    except Exception as e:
        logger.error(f"Error in send_password_reset: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/send-dividend-alert', methods=['POST'])
@require_auth
def send_dividend_alert():
    """Send dividend alert email"""
    try:
        data = request.json
        
        if not data or 'to' not in data or 'stock_symbol' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: to, stock_symbol'
            }), 400
        
        to_email = data['to']
        stock_symbol = data['stock_symbol']
        dividend_date = data.get('dividend_date', '')
        dividend_amount = data.get('dividend_amount', '')
        days_advance = data.get('days_advance', 0)
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>💰 Dividend Alert: {stock_symbol}</h2>
            <p><strong>{stock_symbol}</strong> is paying a dividend of <strong>${dividend_amount}</strong> on <strong>{dividend_date}</strong>.</p>
            <p>This alert was sent {days_advance} days in advance.</p>
            <p>Best regards,<br>StockFolio</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Dividend Alert: {stock_symbol}
        
        {stock_symbol} is paying a dividend of ${dividend_amount} on {dividend_date}.
        
        This alert was sent {days_advance} days in advance.
        
        Best regards,
        StockFolio
        """
        
        success, message = send_email(
            to_email,
            f'{stock_symbol} Dividend Alert ({days_advance} days early)',
            html_content,
            text_content
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Dividend alert sent',
                'service_used': 'smtp'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 500
            
    except Exception as e:
        logger.error(f"Error in send_dividend_alert: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

