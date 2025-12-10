from flask import Flask, request, jsonify

app = Flask(__name__)

CARTS = {}  # user_id -> {product_id: quantity}

@app.route("/cart/<user_id>", methods=["GET"])
def get_cart(user_id):
    return jsonify(CARTS.get(user_id, {}))

@app.route("/cart/<user_id>/items", methods=["POST"])
def add_item(user_id):
    data = request.get_json()
    product_id = data["product_id"]
    quantity = data["quantity"]

    cart = CARTS.setdefault(user_id, {})
    cart[product_id] = cart.get(product_id, 0) + quantity

    return jsonify({"status": "OK", "cart": cart})

@app.route("/cart/<user_id>/items/<product_id>", methods=["DELETE"])
def delete_item(user_id, product_id):
    cart = CARTS.get(user_id, {})
    cart.pop(product_id, None)
    return jsonify({"status": "OK", "cart": cart})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)

