import requests

class CartAPI:
    def __init__(self, base_url: str = "http://localhost:5003"):
        self.base_url = base_url

    def add_item(self, user_id: str, product_id: str, quantity: int):
        """
        Add an item to the user's cart.
        """
        resp = requests.post(
            f"{self.base_url}/cart/{user_id}/items",
            json={"product_id": product_id, "quantity": quantity},
        )
        resp.raise_for_status()
        return resp.json()

    def get_cart(self, user_id: str):
        """
        Get current cart content for given user.
        """
        resp = requests.get(f"{self.base_url}/cart/{user_id}")
        resp.raise_for_status()
        return resp.json()

