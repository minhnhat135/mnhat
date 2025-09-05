from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import os

def pkcs1pad2(s, n):
    if n < len(s) + 11:
        raise ValueError("Message too long for RSA")
    
    ba = bytearray(s.encode('utf-8'))
    
    padded = bytearray(n)
    padded[n - len(ba) - 1] = 0x00
    padded[n - len(ba):] = ba
    
    ps = os.urandom(n - len(ba) - 3)
    
    # Ensure no zero bytes in padding
    ps = ps.replace(b'\x00', b'\x01')

    padded[1] = 0x02
    padded[2:len(ps)+2] = ps
    
    return int.from_bytes(padded, 'big')

class RSAKey:
    def __init__(self):
        self.n = None
        self.e = None
        self._key = None

    def set_public(self, n_hex, e_hex):
        self.n = int(n_hex, 16)
        self.e = int(e_hex, 16)
        self._key = RSA.construct((self.n, self.e))

    def encrypt_b64(self, data_bytes):
        cipher = PKCS1_v1_5.new(self._key)
        encrypted = cipher.encrypt(data_bytes)
        return base64.b64encode(encrypted).decode('utf-8')