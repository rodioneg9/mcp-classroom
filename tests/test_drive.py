import pytest
from unittest.mock import MagicMock, patch
from src.drive import upload_file_to_drive, list_drive_files


def test_upload_file_to_drive_returns_file_id(mock_drive_service):
    mock_drive_service.files().create().execute.return_value = {
        "id": "newfile123", "name": "tarea.pdf"
    }
    with patch("src.drive.MediaFileUpload"):
        result = upload_file_to_drive(
            mock_drive_service,
            file_path="/tmp/tarea.pdf",
            mime_type="application/pdf",
        )
    assert result["id"] == "newfile123"
    assert result["name"] == "tarea.pdf"


def test_upload_file_to_drive_uses_filename_as_name(mock_drive_service):
    mock_drive_service.files().create().execute.return_value = {
        "id": "newfile456", "name": "reporte.docx"
    }
    with patch("src.drive.MediaFileUpload"):
        result = upload_file_to_drive(
            mock_drive_service,
            file_path="/home/isaac/reporte.docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    mock_drive_service.files().create.assert_called()
    call_kwargs = mock_drive_service.files().create.call_args
    assert call_kwargs.kwargs["body"]["name"] == "reporte.docx"


def test_list_drive_files_returns_files(mock_drive_service):
    mock_drive_service.files().list().execute.return_value = {
        "files": [
            {"id": "f1", "name": "apuntes.pdf", "mimeType": "application/pdf"},
            {"id": "f2", "name": "foto.png", "mimeType": "image/png"},
        ]
    }
    result = list_drive_files(mock_drive_service)
    assert len(result) == 2
    assert result[0]["name"] == "apuntes.pdf"


def test_list_drive_files_accepts_query(mock_drive_service):
    mock_drive_service.files().list().execute.return_value = {"files": []}
    list_drive_files(mock_drive_service, query="name contains 'tarea'")
    call_kwargs = mock_drive_service.files().list.call_args
    assert call_kwargs.kwargs["q"] == "name contains 'tarea'"
