from passlib.context import CryptContext



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def test_password_hash_and_verify():
    hashed = pwd_context.hash("123456")
    assert hashed != "123456"
    assert pwd_context.verify("123456", hashed) is True
    assert pwd_context.verify("wrong", hashed) is False

















