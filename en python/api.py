# api.py
from flask import Flask, request, jsonify
import json

# Import hàm mã hóa chính từ file main.py của bạn
# Để làm được điều này, chúng ta cần điều chỉnh file main.py một chút
# để hàm adyen_encrypt có thể được import mà không chạy cả file.
# Tuy nhiên, để đơn giản, tôi sẽ sao chép logic cần thiết vào đây.

from adyen_v4_4_1.encrypt import encrypt_card_data_441
from adyen_v4_5_0.encrypt import encrypt_card_data_450
from adyen_v5_11_0.encryption import encrypt_card_data_511
from risk_data.risk import generate_risk_data

app = Flask(__name__)

def perform_adyen_encryption(adyenkey, card, month, year, cvv, version, ppkey=None, domain=None):
    """
    Hàm này được tách ra từ logic gốc của bạn để tái sử dụng trong API.
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
        # Trong môi trường production, bạn có thể muốn ghi log lỗi thay vì trả về chi tiết
        return {"status": False, "error_message": str(e)}


@app.route('/encrypt', methods=['POST'])
def handle_encryption():
    """
    Endpoint chính của API, nhận dữ liệu qua phương thức POST.
    """
    # Lấy dữ liệu JSON từ body của request
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Lấy các tham số cần thiết từ JSON
    required_params = ["adyenkey", "card", "month", "year", "cvv", "version"]
    for param in required_params:
        if param not in data:
            return jsonify({"error": f"Missing required parameter: {param}"}), 400

    # Lấy các tham số tùy chọn
    ppkey = data.get("ppkey")
    domain = data.get("domain")

    # Gọi hàm mã hóa
    encryption_result = perform_adyen_encryption(
        adyenkey=data["adyenkey"],
        card=data["card"],
        month=data["month"],
        year=data["year"],
        cvv=data["cvv"],
        version=data["version"],
        ppkey=ppkey,
        domain=domain
    )

    if "error" in encryption_result:
        return jsonify(encryption_result), 500

    # Tạo riskData
    risk_data = generate_risk_data()

    # Kết hợp kết quả và trả về
    final_payload = {
        "encryptedData": encryption_result["encryptedData"],
        "riskData": risk_data
    }

    return jsonify(final_payload)

if __name__ == '__main__':
    # Chạy server debug của Flask. Không sử dụng cho production.
    # Để chạy production, chúng ta sẽ dùng Gunicorn.
    app.run(debug=True, host='0.0.0.0', port=5000)
