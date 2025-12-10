from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/payment/charge", methods=["POST"])
def charge():
    data = request.get_json()
    card = data.get("card_number")

    # "4000" = fail card number
    if card.startswith("4000"):
        return jsonify({"status": "FAILED", "reason": "CARD_DECLINED"}), 402

    return jsonify({"status": "SUCCESS", "amount": data["amount"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)

