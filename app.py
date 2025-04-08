from flask import Flask, request, jsonify
import json
import csv

app = Flask(__name__)

# Load token data
def load_tokens():
    tokens = {}
    with open("tokens.csv", newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            tokens[row[0]] = row[2]  # roll_no -> token
    return tokens

@app.route("/validate", methods=["POST"])
def validate():
    qr_data = request.json.get("data")
    try:
        parsed = json.loads(qr_data)
        roll_no = parsed["roll_no"]
        token = parsed["token"]
    except:
        return jsonify({"status": "invalid", "reason": "Malformed QR"})

    tokens = load_tokens()
    if tokens.get(roll_no) == token:
        return jsonify({"status": "valid", "roll_no": roll_no})
    return jsonify({"status": "invalid", "reason": "Invalid token or roll no"})

app.run(host="0.0.0.0", port=5000, debug=True)
