# api.py
from flask import Flask, request, jsonify
import json
import urllib.parse

# Import các hàm mã hóa của bạn
from adyen_v4_4_1.encrypt import encrypt_card_data_441
from adyen_v4_5_0.encrypt import encrypt_card_data_450
from adyen_v5_11_0.encryption import encrypt_card_data_511
from risk_data.risk import generate_risk_data

app = Flask(__name__)

def perform_adyen_encryption(adyenkey, card, month, year, cvv, version, ppkey=None, domain=None):
    """
    Hàm logic chính để thực hiện mã hóa.
    """
    if not adyenkey:
        return {"error": "Missing required `PUBLIC ADYEN KEY`."}

    try:
        if version == "25":  # Adyen v5.11.0
            encrypted_data = encrypt_card_data_511(card, month, year, cvv, adyenkey)
        elif version == "v4":  # Adyen v4.4.1
            encrypted_data = encrypt_card_data_441(card, month, year, cvv, adyenkey, stripe_key=ppkey)
        elif version == "v2":  # Adyen v4.5.0
            encrypted_data = encrypt_card_data_450(card, month, year, cvv, adyenkey, stripe_key=ppkey, domain=domain)
        else:
            return {"error": "Invalid version specified in payload"}

        return {"encryptedData": encrypted_data}

    except Exception as e:
        return {"status": False, "error_message": str(e)}

# ===================================================================
# === PHƯƠNG THỨC POST (AN TOÀN - KHUYÊN DÙNG) ===
# ===================================================================
@app.route('/encrypt', methods=['POST'])
def handle_encryption_post():
    """
    Endpoint an toàn sử dụng POST.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    required_params = ["adyenkey", "card", "month", "year", "cvv", "version"]
    for param in required_params:
        if param not in data:
            return jsonify({"error": f"Missing required parameter: {param}"}), 400

    ppkey = data.get("ppkey")
    domain = data.get("domain")

    encryption_result = perform_adyen_encryption(
        adyenkey=data["adyenkey"], card=data["card"], month=data["month"],
        year=data["year"], cvv=data["cvv"], version=data["version"],
        ppkey=ppkey, domain=domain
    )

    if "error" in encryption_result or encryption_result.get("status") is False:
        return jsonify(encryption_result), 500

    risk_data = generate_risk_data()
    final_payload = {
        "encryptedData": encryption_result["encryptedData"],
        "riskData": risk_data
    }
    return jsonify(final_payload)

# ===================================================================
# === PHƯƠNG THỨC GET (KHÔNG AN TOÀN - THEO YÊU CẦU CỦA BẠN) ===
# ===================================================================
@app.route('/encrypt_get', methods=['GET'])
def handle_encryption_get():
    """
    Endpoint không an toàn sử dụng GET, lấy tất cả tham số từ URL.
    """
    # Lấy các tham số từ query string của URL (ví dụ: ?key=value&key2=value2)
    args = request.args
    
    required_params = ["adyenkey", "card", "month", "year", "cvv", "version"]
    for param in required_params:
        if param not in args:
            return jsonify({"error": f"Missing required URL parameter: {param}"}), 400

    ppkey = args.get("ppkey")
    domain = args.get("domain")

    encryption_result = perform_adyen_encryption(
        adyenkey=args.get("adyenkey"), card=args.get("card"), month=args.get("month"),
        year=args.get("year"), cvv=args.get("cvv"), version=args.get("version"),
        ppkey=ppkey, domain=domain
    )
    
    if "error" in encryption_result or encryption_result.get("status") is False:
        return jsonify(encryption_result), 500

    risk_data = generate_risk_data()
    final_payload = {
        "encryptedData": encryption_result["encryptedData"],
        "riskData": risk_data
    }
    return jsonify(final_payload)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
