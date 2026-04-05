import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_classroom_service():
    """Returns a mock Google Classroom API service."""
    service = MagicMock()
    return service


@pytest.fixture
def mock_drive_service():
    """Returns a mock Google Drive API service."""
    service = MagicMock()
    return service


@pytest.fixture
def mock_credentials():
    creds = MagicMock()
    creds.valid = True
    return creds
