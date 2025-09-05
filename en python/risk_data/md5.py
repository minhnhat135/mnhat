import hashlib
import base64

def calculate_md5_b64(b):
    if isinstance(b, str):
        b = b.encode('utf-8')
    md5_hash = hashlib.md5(b).digest()
    return base64.b64encode(md5_hash).decode('utf-8')