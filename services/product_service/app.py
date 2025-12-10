from flask import Flask, jsonify

app = Flask(__name__)

PRODUCTS = {
    "Laptop-X": {"id": "Laptop-X", "name": "Laptop-X", "price": 999.0},
    "Mouse-Z": {"id": "Mouse-Z", "name": "Mouse-Z", "price": 25.0},
}

@app.route("/products", methods=["GET"])
def list_products():
    return jsonify(list(PRODUCTS.values()))

@app.route("/products/<product_id>", methods=["GET"])
def get_product(product_id):
    product = PRODUCTS.get(product_id)
    if not product:
        return jsonify({"error": "NOT_FOUND"}), 404
    return jsonify(product)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
