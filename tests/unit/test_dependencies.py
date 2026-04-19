"""Unit tests for app/dependencies.py using Mock objects."""
from unittest.mock import MagicMock, patch
from app.dependencies import get_current_user


def test_returns_none_when_no_cookie():
    request = MagicMock()
    request.cookies.get.return_value = None
    db = MagicMock()

    result = get_current_user(request, db)

    assert result is None


def test_returns_none_when_token_invalid():
    request = MagicMock()
    request.cookies.get.return_value = "bad_token"
    db = MagicMock()

    with patch("app.dependencies.decode_access_token", return_value=None):
        result = get_current_user(request, db)

    assert result is None


def test_returns_user_when_token_valid():
    request = MagicMock()
    request.cookies.get.return_value = "valid_token"

    mock_user = MagicMock()
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = mock_user

    with patch("app.dependencies.decode_access_token", return_value=1):
        result = get_current_user(request, db)

    assert result == mock_user


def test_queries_correct_user_id():
    request = MagicMock()
    request.cookies.get.return_value = "valid_token"

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    with patch("app.dependencies.decode_access_token", return_value=99):
        get_current_user(request, db)

    db.query.assert_called_once()
