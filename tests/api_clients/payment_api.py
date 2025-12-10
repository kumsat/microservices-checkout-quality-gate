import requests

class PaymentAPI:
    def __init__(self, base_url: str = "http://localhost:5004"):
        self.base_url = base_url

    def charge(self, card_number: str, amount: float):
        """
        Call the payment service to charge a card.
        We do NOT raise for non-2xx responses so tests can handle failures.
        Returns: (response, json_data)
        """
        resp = requests.post(
            f"{self.base_url}/payment/charge",
            json={"card_number": card_number, "amount": amount},
        )
        try:
            data = resp.json()
        except ValueError:
            data = {}
        return resp, data

