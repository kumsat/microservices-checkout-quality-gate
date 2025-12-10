import requests

class OrderAPI:
    def __init__(self, base_url: str = "http://localhost:5005"):
        self.base_url = base_url

    def create_order(self, user_id: str, items: dict, total: float):
        """
        Create an order for a user with items and total price.
        """
        resp = requests.post(
            f"{self.base_url}/orders",
            json={"user_id": user_id, "items": items, "total": total},
        )
        resp.raise_for_status()
        return resp.json()["order"]

    def get_latest_order(self, user_id: str):
        """
        Get the latest order for a user.
        """
        resp = requests.get(f"{self.base_url}/orders/latest/{user_id}")
        return resp

