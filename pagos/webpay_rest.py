import requests
from decouple import config

WEBPAY_BASE_URL = config("WEBPAY_BASE_URL")
COMMERCE_CODE = config("WEBPAY_COMMERCE_CODE")
API_KEY = config("WEBPAY_API_KEY")

HEADERS = {
    "Tbk-Api-Key-Id": COMMERCE_CODE,
    "Tbk-Api-Key-Secret": API_KEY,
    "Content-Type": "application/json",
}


def crear_transaccion(buy_order, session_id, amount, return_url):
    url = f"{WEBPAY_BASE_URL}/transactions"
    data = {
        "buy_order": buy_order,
        "session_id": session_id,
        "amount": int(amount),  # Webpay espera un entero
        "return_url": return_url,
    }
    response = requests.post(url, json=data, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def confirmar_transaccion(token):
    url = f"{WEBPAY_BASE_URL}/transactions/{token}"
    response = requests.put(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()
