from flask import Flask, request, jsonify

app = Flask(__name__)

INVENTORY = {
    "Laptop-X": 5,
    "Mouse-Z": 1,
}

@app.route("/inventory/<product_id>", methods=["GET"])
def get_stock(product_id):
    stock = INVENTORY.get(product_id)
    if stock is None:
        return jsonify({"error": "NOT_FOUND"}), 404
    return jsonify({"product_id": product_id, "stock": stock})

@app.route("/inventory/set", methods=["POST"])
def set_stock():
    data = request.get_json()
    INVENTORY[data["product_id"]] = data["stock"]
    return jsonify({"status": "OK"})

@app.route("/inventory/reserve", methods=["POST"])
def reserve_stock():
    data = request.get_json()
    product_id = data["product_id"]
    qty = data["quantity"]

    if INVENTORY.get(product_id, 0) < qty:
        return jsonify({"status": "INSUFFICIENT_STOCK"}), 400

    INVENTORY[product_id] -= qty
    return jsonify({"status": "OK", "remaining": INVENTORY[product_id]})

@app.route("/inventory/release", methods=["POST"])
def release_stock():
    data = request.get_json()
    INVENTORY[data["product_id"]] += data["quantity"]
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)

