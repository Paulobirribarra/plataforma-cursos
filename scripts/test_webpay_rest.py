import requests

WEBPAY_BASE_URL = "https://webpay3gint.transbank.cl/rswebpaytransaction/api/webpay/v1.2"
COMMERCE_CODE = "597055555532"
API_KEY = "XqGG7dQfVQZTqdlzJzQz"

HEADERS = {
    "Tbk-Api-Key-Id": COMMERCE_CODE,
    "Tbk-Api-Key-Secret": API_KEY,
    "Content-Type": "application/json",
}


def main():
    url = f"{WEBPAY_BASE_URL}/transactions"
    data = {
        "buy_order": "TESTORDER12345",
        "session_id": "TESTSESSION1",
        "amount": 1000,
        "return_url": "https://www.google.com/",  # Solo para pruebas
    }
    print("Enviando petición a Webpay...")
    response = requests.post(url, json=data, headers=HEADERS)
    print(f"Status: {response.status_code}")
    print(f"Respuesta: {response.text}")


if __name__ == "__main__":
    main()
