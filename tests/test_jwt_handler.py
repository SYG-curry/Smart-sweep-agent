from utils.jwt_handler import create_access_token, decode_access_token

"""
    测试JWT    
"""

# 签发 -> 解码
def test_jwt_roundtrip():
    token = create_access_token({"sub": "u1", "username": "alice"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "u1"
    assert payload["username"] == "alice"

def test_jwt_invalid_token():
    assert decode_access_token("not.a.valid.token") is None












