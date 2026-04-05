import pytest
from unittest.mock import patch, MagicMock
from src.auth import get_credentials, SCOPES


def test_scopes_include_classroom_and_drive():
    assert "https://www.googleapis.com/auth/classroom.courses.readonly" in SCOPES
    assert "https://www.googleapis.com/auth/classroom.coursework.me" in SCOPES
    assert "https://www.googleapis.com/auth/drive.file" in SCOPES


def test_get_credentials_loads_existing_token(tmp_path):
    """If token.json exists and is valid, returns credentials without browser flow."""
    token_file = tmp_path / "token.json"
    mock_creds = MagicMock()
    mock_creds.valid = True

    with patch("src.auth.TOKEN_PATH", str(token_file)), \
         patch("src.auth.Credentials.from_authorized_user_file", return_value=mock_creds) as mock_load:
        token_file.write_text("{}")
        result = get_credentials()
        mock_load.assert_called_once()
        assert result == mock_creds


def test_get_credentials_refreshes_expired_token(tmp_path):
    """If token exists but is expired, refreshes it."""
    token_file = tmp_path / "token.json"
    token_file.write_text("{}")

    mock_creds = MagicMock()
    mock_creds.valid = False
    mock_creds.expired = True
    mock_creds.refresh_token = "refresh_token_value"

    with patch("src.auth.TOKEN_PATH", str(token_file)), \
         patch("src.auth.Credentials.from_authorized_user_file", return_value=mock_creds), \
         patch("src.auth.Request") as mock_request:
        mock_creds.to_json.return_value = "{}"
        result = get_credentials()
        mock_creds.refresh.assert_called_once()
        assert result == mock_creds


def test_get_credentials_runs_oauth_flow_when_no_token(tmp_path):
    """If no token exists, runs InstalledAppFlow."""
    token_file = tmp_path / "no_token.json"  # does not exist

    mock_creds = MagicMock()
    mock_flow = MagicMock()
    mock_flow.run_local_server.return_value = mock_creds

    with patch("src.auth.TOKEN_PATH", str(token_file)), \
         patch("src.auth.InstalledAppFlow.from_client_secrets_file", return_value=mock_flow), \
         patch("builtins.open", create=True):
        result = get_credentials()
        mock_flow.run_local_server.assert_called_once_with(port=0)
        assert result == mock_creds
