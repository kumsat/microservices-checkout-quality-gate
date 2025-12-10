import requests

class ProductAPI:
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url

    def get_product(self, product_id: str):
        """
        Get a single product by ID.
        """
        resp = requests.get(f"{self.base_url}/products/{product_id}")
        resp.raise_for_status()
        return resp.json()

