import requests
import base64
import logging
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)


def get_access_token():
    if not settings.MPESA_CONSUMER_KEY or not settings.MPESA_CONSUMER_SECRET:
        raise ValueError('MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET must be configured in settings or environment variables.')

    try:
        response = requests.get(
            settings.MPESA_OAUTH_URL,
            auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
            timeout=20,
        )
        response.raise_for_status()
        return response.json().get('access_token')
    except requests.RequestException as e:
        logger.error(f"Failed to get MPesa access token: {e} | Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
        raise


def stk_push(phone_number, amount, account_ref, description):
    if not settings.MPESA_PASSKEY or not settings.MPESA_SHORTCODE or not settings.MPESA_CALLBACK_URL:
        raise ValueError('MPESA_PASSKEY, MPESA_SHORTCODE, and MPESA_CALLBACK_URL must be configured in settings or environment variables.')

    try:
        # Validate and format phone number
        phone = str(phone_number).strip()
        if not phone.startswith('254'):
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            else:
                phone = '254' + phone
        
        # Convert amount to integer
        amount = int(float(amount))
        
        access_token = get_access_token()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
        ).decode()

        payload = {
            'BusinessShortCode': str(settings.MPESA_SHORTCODE),
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': phone,
            'PartyB': str(settings.MPESA_SHORTCODE),
            'PhoneNumber': phone,
            'CallBackURL': str(settings.MPESA_CALLBACK_URL),
            'AccountReference': str(account_ref),
            'TransactionDesc': str(description),
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        logger.info(f"Sending MPesa STK Push: Phone={phone}, Amount={amount}, ShortCode={settings.MPESA_SHORTCODE}")
        
        response = requests.post(settings.MPESA_STK_PUSH_URL, json=payload, headers=headers, timeout=20)
        
        if response.status_code != 200:
            error_detail = response.text
            logger.error(f"MPesa API error ({response.status_code}): {error_detail}")
            response.raise_for_status()
        
        result = response.json()
        logger.info(f"MPesa response: {result}")
        return result
        
    except requests.RequestException as e:
        logger.error(f"MPesa request failed: {e} | Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in stk_push: {e}")
        raise
