import json
import requests
import os
from flask import Blueprint, request, redirect, render_template, jsonify, session
from urllib.parse import urlencode
from src.db.core import db

paystack_bp = Blueprint('paystack', __name__, url_prefix='/paystack')

# Product configuration
PRO_FEATURE = {
    'name': 'Quiz App Pro',
    # ₦1050 in kobo (Paystack uses kobo)
    'price': 1050,
    'description': 'Access to full Quiz and Study features'
}

# Get Paystack secret key from environment variable
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')

def mark_user_as_pro(email):
    """Mark user as pro in the database"""
    try:
        from src.db.models.users import User
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_pro = True
            db.session.commit()
        else:
            new_user = User(email=email, is_pro=True)
            db.session.add(new_user)
            db.session.commit()
    except Exception as e:
        print(f"Error marking user as pro: {e}")
        # Fallback to session-based storage
        session['user_pro_status'] = True

def is_user_pro(email):
    """Check if user is pro from the database"""
    try:
        from src.db.models.users import User
        user = User.query.filter_by(email=email).first()
        is_pro = user.is_pro if user else False
        print(f"Database pro status for {email}: {is_pro}")  # Debug log
        return is_pro or session.get('user_pro_status', False)
    except Exception as e:
        print(f"Error checking user pro status: {e}")
        return session.get('user_pro_status', False)

@paystack_bp.route('/initialize', methods=['POST'])
def initialize_payment():
    if not PAYSTACK_SECRET_KEY:
        return jsonify({'error': 'Paystack API key not configured'}), 500
    
    try:
        # Get the JSON data from the request
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        # Set up the Paystack API request
        auth_headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
        # Prepare the payment data
        payment_data = {
            "email": data['email'],
            "amount": str(PRO_FEATURE['price']),
            "callback_url": request.host_url.rstrip('/') + "/paystack/callback",
            "metadata": {
                "product_name": PRO_FEATURE['name'],
                "custom_fields": [
                    {
                        "display_name": "Product",
                        "variable_name": "product",
                        "value": PRO_FEATURE['name']
                    }
                ]
            }
        }
        
        # Initialize the transaction
        req = requests.post(
            'https://api.paystack.co/transaction/initialize', 
            headers=auth_headers, 
            data=json.dumps(payment_data)
        )
        
        response_data = req.json()
        
        if req.status_code != 200 or not response_data.get('status'):
            return jsonify({
                'status': False,
                'message': response_data.get('message', 'Payment initialization failed')
            }), 400
        
        # Return the authorization URL
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@paystack_bp.route('/callback')
def payment_callback():
    # Get the reference from the URL
    reference = request.args.get('reference', '')
    if not reference:
        return render_template('payment_failed.html', message="No reference supplied")
    
    # Verify the transaction
    auth_headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        req = requests.get(
            f'https://api.paystack.co/transaction/verify/{reference}', 
            headers=auth_headers
        )
        
        response_data = req.json()
        
        if req.status_code != 200 or not response_data.get('status'):
            return render_template('payment_failed.html', 
                                  message=response_data.get('message', 'Payment verification failed'))
        
        # Check if the transaction was successful
        if response_data['data']['status'] == 'success':
            email = response_data['data']['customer']['email']
            mark_user_as_pro(email)  # Mark the user as pro in the database
            
            # Update session with complete user data
            user_data = {
                'email': email,
                'pro': True,
            }
            session['user'] = user_data
            session['user_pro_status'] = True
            
            print(f"Payment successful for {email}, pro status set")  # Debug log
            
            amount = response_data['data']['amount'] / 100  # Convert from kobo to naira
            formatted_amount = f"₦{amount:.2f}"
            
            return render_template('payment_success.html', 
                                  transaction_id=response_data['data']['id'],
                                  amount=formatted_amount,
                                  product_name=PRO_FEATURE['name'])
        else:
            return render_template('payment_failed.html', 
                                  message="Transaction was not successful: " + response_data['data']['gateway_response'])
    
    except Exception as e:
        return render_template('payment_failed.html', message=f"An error occurred: {str(e)}")
