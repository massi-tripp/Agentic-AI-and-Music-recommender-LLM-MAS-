from src.protocol import ACLMessage, Performative
from src.security import sign, verify

# compat: usa json std se orjson manca
try:
    import orjson as _jsonlib
    def _dumps(x): return _jsonlib.dumps(x)
except Exception:
    import json as _jsonlib
    def _dumps(x): return _jsonlib.dumps(x).encode()

def test_aclmessage_schema_ok():
    payload = {"song_id": 133, "mode": "COOP"}
    sig = sign(b"key-1", _dumps(payload))
    msg = ACLMessage(
        sender="u1",
        receiver="u2",
        performative=Performative.PROPOSE,
        conv_id="c-123",
        content=payload,
        nonce="n-1",
        sig=sig
    )
    assert msg.sender == "u1"
    assert msg.performative == Performative.PROPOSE
    assert isinstance(msg.content, dict)

def test_signature_verify_roundtrip():
    payload = {"x": 1}
    key = b"secret"
    sig = sign(key, _dumps(payload))
    assert verify(key, _dumps(payload), sig) is True
    assert verify(key, _dumps({"x": 2}), sig) is False

def test_invalid_performative_raises():
    from pydantic import ValidationError
    import pytest
    with pytest.raises(ValidationError):
        ACLMessage(sender="u1", receiver="u2", performative="TALK",
                   conv_id="c", content={}, nonce="n", sig="s")
