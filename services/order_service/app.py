from flask import Flask, request, jsonify

app = Flask(__name__)

ORDERS = []

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    ORDERS.append(data)
    return jsonify({"status": "OK", "order": data})

@app.route("/orders/<user_id>", methods=["GET"])
def get_orders(user_id):
    return jsonify([o for o in ORDERS if o["user_id"] == user_id])

@app.route("/orders/latest/<user_id>", methods=["GET"])
def get_latest_order(user_id):
    user_orders = [o for o in ORDERS if o["user_id"] == user_id]
    if not user_orders:
        return jsonify({"error": "NOT_FOUND"}), 404
    return jsonify(user_orders[-1])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)

