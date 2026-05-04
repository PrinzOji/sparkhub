import requests
import base64
from datetime import datetime
from django.conf import settings

def get_access_token():
    consumer_key = "YOUR_CONSUMER_KEY"
    consumer_secret = "YOUR_CONSUMER_SECRET"
    
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    return response.json()['access_token']

def stk_push(phone_number, amount, account_ref, description):
    access_token = get_access_token()
    
    shortcode = "174379"  # sandbox shortcode
    passkey = "YOUR_PASSKEY"
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        f"{shortcode}{passkey}{timestamp}".encode()
    ).decode()
    
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/mpesa/callback/",
        "AccountReference": account_ref,
        "TransactionDesc": description
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()