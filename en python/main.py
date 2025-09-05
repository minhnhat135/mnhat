import json
from adyen_v4_4_1.encrypt import encrypt_card_data_441
from adyen_v4_5_0.encrypt import encrypt_card_data_450
from adyen_v5_11_0.encryption import encrypt_card_data_511
from risk_data.risk import generate_risk_data # <-- DÒNG MỚI: Import hàm tạo riskData

def adyen_encrypt(adyenkey, card, month, year, cvv, version, ppkey=None, domain=None):
    """
    Hàm chính để mã hóa dữ liệu thẻ Adyen dựa trên phiên bản được chỉ định.
    """
    if not adyenkey:
        return {"error": "Missing required `PUBLIC ADYEN KEY`."}

    try:
        if version == "25": # Adyen v5.11.0
            encrypted_data = encrypt_card_data_511(card, month, year, cvv, adyenkey)
        elif version == "v4": # Adyen v4.4.1
            encrypted_data = encrypt_card_data_441(card, month, year, cvv, adyenkey, stripe_key=ppkey)
        elif version == "v2": # Adyen v4.5.0
            encrypted_data = encrypt_card_data_450(card, month, year, cvv, adyenkey, stripe_key=ppkey, domain=domain)
        else:
            return {"error": "Invalid version specified in payload"}
            
        return {"encryptedData": encrypted_data}

    except Exception as e:
        return {"status": False, "error_message": str(e)}

if __name__ == '__main__':
    # ===================================================================
    # === BẠN CHỈ CẦN CHỈNH SỬA CÁC THÔNG SỐ TRONG PHẦN NÀY ===
    # ===================================================================

    # 1. Thông tin thẻ bạn muốn mã hóa
    card_number = '5168155124645796'
    card_month = '12'
    card_year = '2028'
    card_cvv = '123'

    # 2. Dữ liệu lấy từ trang web mục tiêu
    data_for_website = {
        # Dán Adyen Public Key của trang web vào đây
        "adyenkey": "10001|BCBF82C45F5C64A6572CF862AFF9FF4345F4C285EF1290434BADFA04FB3C2E9C3211890915BFB6BD7EB10450F3153AF3FA066F3C41DD7B52188F0C7687473801CD66EFF913FA553ACCFA509F6ECACCAE8BE5AC908158D942145DE62D02E23A26F5151633CDD98F82433CAE5D67AB10D0E36A3E8FF0500F83BFF7D08029DD4AE5CE37F42BC675C1BB90FFC5CEF882830A53BB2F5792AF2FBA95B118DAFDF52C2B801C3774F483828DD24A76019A922FBC81981DF81882D7D79EBDF1B409ADD75CDF5B6DD2D9FEF1D08C8BC49B478A87411347E0C468FFF6BF460B1BB894442A1EE13CFAAD2F526602587AFA1E5EF9DAF4C04022AA843A3B4C03E52BAFE5F1AEE5",
        
        "card": card_number,
        "month": card_month,
        "year": card_year,
        "cvv": card_cvv,
        
        "version": 'v2', # Phiên bản 4.5.0
        
        "ppkey": "live_EOAGXY2IS5H4NND7AXE2IQKPW4VCMU2D",
        
        "domain": "https://abo.mediapart.fr/"
    }
    
    # 3. Thực thi mã hóa và tạo riskData
    encryption_result = adyen_encrypt(**data_for_website)
    
    # --- PHẦN MỚI ĐƯỢC THÊM VÀO ---
    if "error" not in encryption_result:
        # Tạo riskData
        risk_data = generate_risk_data()
        
        # Kết hợp kết quả mã hóa và riskData
        final_payload = {
            "encryptedData": encryption_result["encryptedData"],
            "riskData": risk_data
        }
    else:
        final_payload = encryption_result

    # 4. In kết quả cuối cùng
    print(json.dumps(final_payload, indent=4))