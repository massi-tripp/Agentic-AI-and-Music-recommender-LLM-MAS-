import hmac, hashlib
def sign(key: bytes, payload: bytes) -> str:
    return hmac.new(key, payload, hashlib.sha256).hexdigest()
def verify(key: bytes, payload: bytes, sig: str) -> bool:
    return hmac.new(key, payload, hashlib.sha256).hexdigest() == sig
