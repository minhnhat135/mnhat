import os
import json
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class AESKey:
    def __init__(self):
        self._key = get_random_bytes(32) # AES-256

    @property
    def key(self):
        return self._key

    def encrypt(self, text):
        iv = get_random_bytes(12) # 96 bits for CCM
        return self.encrypt_with_iv(text, iv)

    def encrypt_with_iv(self, text, iv):
        cipher = AES.new(self.key, AES.MODE_CCM, nonce=iv)
        data = text.encode('utf-8')
        ciphertext, tag = cipher.encrypt_and_digest(data)
        
        # sjcl format appears to concat iv and ciphertext for base64 encoding
        # In CCM, the tag is separate. We need to decide how to handle this.
        # A common approach is to return iv + ciphertext + tag
        # For sjcl compatibility, it seems to be iv + ciphertext, then base64
        cipher_iv = iv + ciphertext 
        return base64.b64encode(cipher_iv).decode('utf-8')