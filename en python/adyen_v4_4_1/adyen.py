import os
import json
from base64 import b64decode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Hash import SHA512
from Crypto.Util.Padding import pad, unpad
from jose import jwk
from .utils import _, k

class AdyenV4_4_1:
    def __init__(self, site_key):
        self.site_key = site_key
        self.key_object = None

    def generate_key(self):
        parts = self.site_key.split("|")
        if len(parts) != 2:
            raise ValueError("Malformed public key: incorrect split parts")
        
        part1 = parts[0]
        part2 = parts[1]
        
        decoded_part1 = k(part1)
        decoded_part2 = k(part2)

        encoded_part1 = _(decoded_part1)
        encoded_part2 = _(decoded_part2)

        self.key_object = {
            "kty": "RSA",
            "kid": "asf-key",
            "e": encoded_part1,
            "n": encoded_part2,
            "alg": "RSA-OAEP",
        }
        return self.key_object

    def encrypt_data(self, plain_text):
        public_key = jwk.construct(self.key_object)
        pem = public_key.to_pem().decode('utf-8')
        rsa_key = RSA.import_key(pem)
        
        random_bytes = os.urandom(64)
        
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        encrypted_key = cipher_rsa.encrypt(random_bytes)
        
        cek = random_bytes
        
        protected_header = {"alg": "RSA-OAEP", "enc": "A256CBC-HS512", "version": "1"}
        protected_header_b64 = _(json.dumps(protected_header).encode('utf-8'))
        
        _iv = os.urandom(16)
        _plaintext = json.dumps(plain_text).encode('utf-8')
        
        aes_key = cek[32:]
        hmac_key = cek[:32]
        
        cipher_aes = AES.new(aes_key, AES.MODE_CBC, _iv)
        padded_plaintext = pad(_plaintext, AES.block_size)
        ciphertext = cipher_aes.encrypt(padded_plaintext)
        
        protected_header2_bytes = protected_header_b64.encode('utf-8')
        
        hmac = SHA512.new(hmac_key)
        hmac.update(protected_header2_bytes + _iv + ciphertext + str(len(protected_header2_bytes) * 8).encode())
        
        tag = hmac.digest()[:32]

        return f"{protected_header_b64}.{_(encrypted_key)}.{_(_iv)}.{_(ciphertext)}.{_(tag)}"