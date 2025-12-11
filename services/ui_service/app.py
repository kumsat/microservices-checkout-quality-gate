from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# URLs to other microservices (inside Docker network)
PRODUCT_SERVICE_URL = "http://product-service:5001"
INVENTORY_SERVICE_URL = "http://inventory-service:5002"
CART_SERVICE_URL = "http://cart-service:5003"
PAYMENT_SERVICE_URL = "http://payment-service:5004"
ORDER_SERVICE_URL = "http://order-service:5005"


@app.route("/", methods=["GET"])
def index():
    """
    Home page: list products and show a simple checkout form.
    """
    try:
        resp = requests.get(f"{PRODUCT_SERVICE_URL}/products", timeout=3)
        resp.raise_for_status()
        products = resp.json()
    except Exception as e:
        products = []
        print("Error fetching products:", e)

    # For simplicity, we will have default user_id = selenium-user
    return render_template("index.html", products=products, default_user_id="selenium-user")


@app.route("/checkout", methods=["POST"])
def checkout():
    """
    Perform a very simple checkout:
    - get product price
    - add to cart
    - reserve inventory
    - charge payment
    - create order
    """
    user_id = request.form.get("user_id", "selenium-user")
    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", "1"))
    card_number = request.form.get("card_number")

    message = ""
    success = False

    try:
        # 1) Get product info
        product_resp = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}", timeout=3)
        product_resp.raise_for_status()
        product = product_resp.json()
        price = product["price"]

        # 2) Add to cart
        cart_resp = requests.post(
            f"{CART_SERVICE_URL}/cart/{user_id}/items",
            json={"product_id": product_id, "quantity": quantity},
            timeout=3,
        )
        cart_resp.raise_for_status()

        # 3) Reserve inventory
        inv_reserve = requests.post(
            f"{INVENTORY_SERVICE_URL}/inventory/reserve",
            json={"product_id": product_id, "quantity": quantity},
            timeout=3,
        )
        if inv_reserve.status_code != 200:
            message = "Checkout failed: insufficient stock."
            return render_template("result.html", message=message, success=False)

        # 4) Charge payment
        total_amount = price * quantity
        pay_resp = requests.post(
            f"{PAYMENT_SERVICE_URL}/payment/charge",
            json={"card_number": card_number, "amount": total_amount},
            timeout=3,
        )
        try:
            pay_data = pay_resp.json()
        except ValueError:
            pay_data = {}

        if pay_resp.status_code != 200 or pay_data.get("status") != "SUCCESS":
            # release inventory again
            requests.post(
                f"{INVENTORY_SERVICE_URL}/inventory/release",
                json={"product_id": product_id, "quantity": quantity},
                timeout=3,
            )
            message = "Checkout failed: payment declined."
            return render_template("result.html", message=message, success=False)

        # 5) Create order
        order_resp = requests.post(
            f"{ORDER_SERVICE_URL}/orders",
            json={"user_id": user_id, "items": {product_id: quantity}, "total": total_amount},
            timeout=3,
        )
        order_resp.raise_for_status()

        success = True
        message = "Order created successfully!"

    except Exception as e:
        print("Error during checkout:", e)
        message = "Checkout failed due to a technical error."

    return render_template("result.html", message=message, success=success)


if __name__ == "__main__":
    # Important: host=0.0.0.0 and port 5000 for Docker
    app.run(host="0.0.0.0", port=5000)

