import requests
from django.conf import settings

def get_paypal_access_token():
    url = f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token"

    response = requests.post(
        url,
        headers={
            "Accept":"application/json",
            "Accept-Language":"en-US"
        },
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET_KEY),
        data={"grant_type":"client_credentials"},
    )

    return response.json().get("access_token")

def create_paypal_order(order):
    access_token = get_paypal_access_token()

    total_amount = order.order_total + order.tax
    
    url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders"

    headers = {
        "Content-Type":"application/json",
        "Authorization": f"Bearer {access_token}",
    }

    data = {
        "intent":"CAPTURE",
        "purchase_units":[
            {
                "reference_id": str(order.id),
                "amount":{
                    "currency_code": "USD",
                    "value": str(total_amount),
                },
            },
        ],
        "application_context":{
            "return_url": "http://localhost:3000/payment-success",
            "cancel_url": "http://localhost:3000/payment-cancel",
        },
    }

    response = requests.post(url=url, json=data, headers=headers)
    
    return response.json()