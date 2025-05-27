import requests

WEBPAY_BASE_URL = "https://webpay3gint.transbank.cl/rswebpaytransaction/api/webpay/v1.2"
COMMERCE_CODE = "597055555532"  # Código de comercio de pruebas oficial
API_KEY = "XqGG7dQfVQZTqdlzJzQz"  # API Key de pruebas oficial

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
