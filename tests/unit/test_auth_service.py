"""Unit tests for app/auth.py — full coverage of service functions."""
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)


def test_get_password_hash_returns_string():
    hashed = get_password_hash("mypassword")
    assert isinstance(hashed, str)


def test_get_password_hash_not_plain_text():
    hashed = get_password_hash("mypassword")
    assert hashed != "mypassword"


def test_hash_is_different_each_time():
    hash1 = get_password_hash("same_password")
    hash2 = get_password_hash("same_password")
    assert hash1 != hash2


def test_verify_password_correct():
    hashed = get_password_hash("securepass")
    assert verify_password("securepass", hashed) is True


def test_verify_password_wrong():
    hashed = get_password_hash("securepass")
    assert verify_password("wrongpass", hashed) is False


def test_verify_password_empty():
    hashed = get_password_hash("securepass")
    assert verify_password("", hashed) is False


def test_create_access_token_returns_string():
    token = create_access_token(1)
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_different_users():
    token1 = create_access_token(1)
    token2 = create_access_token(2)
    assert token1 != token2


def test_decode_access_token_returns_correct_id():
    token = create_access_token(42)
    assert decode_access_token(token) == 42


def test_decode_access_token_invalid_returns_none():
    assert decode_access_token("invalid.token.value") is None


def test_decode_access_token_empty_returns_none():
    assert decode_access_token("") is None


def test_decode_access_token_garbage_returns_none():
    assert decode_access_token("not-a-jwt-at-all") is None
