from .adyen import AdyenV4_4_1
from .utils import get_current_timestamp
import base64

def format_card_number(card):
    return ' '.join(card[i:i+4] for i in range(0, len(card), 4))

def encrypt_card_data_441(card, month, year, cvc, adyen_key, stripe_key=None):
    if not all([card, month, year, cvc, adyen_key]):
        raise ValueError("Missing card details or Adyen key")

    if not stripe_key:
        stripe_key = "live_2WKDYLJCMBFC5CFHBXY2CHZF4MUUJ7QU"
    
    card_number = format_card_number(card)
    
    domain_b64 = base64.b64encode(b"https://www.mytheresa.com").decode('utf-8')
    referrer = f"https://checkoutshopper-live.adyen.com/checkoutshopper/securedfields/{stripe_key}/4.4.1/securedFields.html?type=card&d={domain_b64}"

    card_detail = {
        "encryptedCardNumber": {"number": card_number, "generationtime": get_current_timestamp(), "numberBind": "1", "activate": "3", "referrer": referrer, "numberFieldFocusCount": "3", "numberFieldLog": "fo@44070,cl@44071,KN@44082,fo@44324,cl@44325,cl@44333,KN@44346,KN@44347,KN@44348,KN@44350,KN@44351,KN@44353,KN@44354,KN@44355,KN@44356,KN@44358,fo@44431,cl@44432,KN@44434,KN@44436,KN@44438,KN@44440,KN@44440", "numberFieldClickCount": "4", "numberFieldKeyCount": "16"},
        "encryptedExpiryMonth": {"expiryMonth": month, "generationtime": get_current_timestamp()},
        "encryptedExpiryYear": {"expiryYear": year, "generationtime": get_current_timestamp()},
        "encryptedSecurityCode": {"cvc": cvc, "generationtime": get_current_timestamp(), "cvcBind": "1", "activate": "4", "referrer": referrer, "cvcFieldFocusCount": "4", "cvcFieldLog": "fo@122,cl@123,KN@136,KN@138,KN@140,fo@11204,cl@11205,ch@11221,bl@11221,fo@33384,bl@33384,fo@50318,cl@50319,cl@50321,KN@50334,KN@50336,KN@50336", "cvcFieldClickCount": "4", "cvcFieldKeyCount": "6", "cvcFieldChangeCount": "1", "cvcFieldBlurCount": "2", "deactivate": "2"}
    }

    adyen_encryptor = AdyenV4_4_1(adyen_key)
    adyen_encryptor.generate_key()

    encrypted_details = {}
    for key, value in card_detail.items():
        encrypted_details[key] = adyen_encryptor.encrypt_data(value)
        
    return encrypted_details