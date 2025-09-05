import json
from datetime import datetime
from .rsa import RSAKey
from .aes import AESKey

class Encryption:
    def __init__(self, key, options=None):
        self.key = key
        self.options = options or {}

    def create_rsa_key(self):
        k = self.key.split("|")
        if len(k) != 2:
            raise ValueError("Malformed public key")
        exp, mod = k[0], k[1]
        rsa = RSAKey()
        rsa.set_public(mod, exp)
        return rsa

    def create_aes_key(self):
        return AESKey()

    def encrypt(self, original_data):
        data = original_data.copy()
        
        rsa = self.create_rsa_key()
        aes = self.create_aes_key()
        
        # The JS implementation seems to use AES-CCM, but the way it's used
        # (encrypting JSON) needs careful replication.
        # Here we're simply encrypting the JSON string representation
        cipher = aes.encrypt(json.dumps(data))
        
        key_bytes = aes.key
        encrypted_aes_key = rsa.encrypt_b64(key_bytes)
        
        prefix = "adyenjs_0_1_25$"
        return f"{prefix}{encrypted_aes_key}${cipher}"

def get_current_timestamp():
    return datetime.utcnow().isoformat() + "Z"

def format_card_number(card):
    return ' '.join(card[i:i+4] for i in range(0, len(card), 4))

def encrypt_card_data_511(card, month, year, cvc, adyen_key):
    if not all([card, month, year, cvc, adyen_key]):
        raise ValueError('Missing card details or Adyen key')

    if len(year) != 4:
        raise ValueError('Invalid year')
        
    encryptor = Encryption(adyen_key)
    card_number = format_card_number(card)
    
    return {
        "encryptedCardNumber": encryptor.encrypt({
            "number": card_number,
            "generationtime": get_current_timestamp(),
        }),
        "encryptedExpiryMonth": encryptor.encrypt({
            "expiryMonth": month,
            "generationtime": get_current_timestamp(),
        }),
        "encryptedExpiryYear": encryptor.encrypt({
            "expiryYear": year,
            "generationtime": get_current_timestamp(),
        }),
        "encryptedSecurityCode": encryptor.encrypt({
            "cvc": cvc,
            "generationtime": get_current_timestamp(),
        }),
    }