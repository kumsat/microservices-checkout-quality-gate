import requests

class InventoryAPI:
    def __init__(self, base_url: str = "http://localhost:5002"):
        self.base_url = base_url

    def set_stock(self, product_id: str, stock: int):
        resp = requests.post(
            f"{self.base_url}/inventory/set",
            json={"product_id": product_id, "stock": stock},
        )
        resp.raise_for_status()
        return resp.json()

    def get_stock(self, product_id: str) -> int:
        resp = requests.get(f"{self.base_url}/inventory/{product_id}")
        resp.raise_for_status()
        data = resp.json()
        return data["stock"]

    def reserve(self, product_id: str, quantity: int):
        """
        Try to reserve stock for checkout.
        Returns the raw response so the caller can inspect status code and body.
        """
        resp = requests.post(
            f"{self.base_url}/inventory/reserve",
            json={"product_id": product_id, "quantity": quantity},
        )
        return resp

    def release(self, product_id: str, quantity: int):
        """
        Release previously reserved stock (used when payment fails).
        """
        resp = requests.post(
            f"{self.base_url}/inventory/release",
            json={"product_id": product_id, "quantity": quantity},
        )
        resp.raise_for_status()
        return resp.json()

