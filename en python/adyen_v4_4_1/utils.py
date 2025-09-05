import base64

def get_current_timestamp():
    from datetime import datetime
    return datetime.utcnow().isoformat() + 'Z'

def _w(e):
    if isinstance(e, str):
        t = e.encode('utf-8')
    else:
        t = e
    return base64.b64encode(t).decode('utf-8')

def _(e):
    return _w(e).replace('=', '').replace('+', '-').replace('/', '_')

def k(e):
    if not e:
        return bytearray(0)
    if len(e) % 2 == 1:
        e = "0" + e
    t = len(e) // 2
    r = bytearray(t)
    for n in range(t):
        r[n] = int(e[n*2:n*2+2], 16)
    return r