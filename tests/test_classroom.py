import pytest
from unittest.mock import MagicMock, patch
from src.classroom import (
    list_courses,
    get_course,
    list_students,
    list_teachers,
)


def test_list_courses_returns_course_names(mock_classroom_service):
    mock_classroom_service.courses().list().execute.return_value = {
        "courses": [
            {"id": "123", "name": "Matemáticas", "section": "A"},
            {"id": "456", "name": "Física", "section": "B"},
        ]
    }
    result = list_courses(mock_classroom_service)
    assert len(result) == 2
    assert result[0]["name"] == "Matemáticas"
    assert result[1]["id"] == "456"


def test_list_courses_returns_empty_when_none(mock_classroom_service):
    mock_classroom_service.courses().list().execute.return_value = {}
    result = list_courses(mock_classroom_service)
    assert result == []


def test_get_course_returns_course_detail(mock_classroom_service):
    mock_classroom_service.courses().get().execute.return_value = {
        "id": "123", "name": "Matemáticas", "descriptionHeading": "Intro"
    }
    result = get_course(mock_classroom_service, course_id="123")
    assert result["name"] == "Matemáticas"


def test_list_students_returns_list(mock_classroom_service):
    mock_classroom_service.courses().students().list().execute.return_value = {
        "students": [
            {"userId": "u1", "profile": {"name": {"fullName": "Ana López"}}},
            {"userId": "u2", "profile": {"name": {"fullName": "Carlos Ruiz"}}},
        ]
    }
    result = list_students(mock_classroom_service, course_id="123")
    assert len(result) == 2
    assert result[0]["profile"]["name"]["fullName"] == "Ana López"


def test_list_teachers_returns_list(mock_classroom_service):
    mock_classroom_service.courses().teachers().list().execute.return_value = {
        "teachers": [
            {"userId": "t1", "profile": {"name": {"fullName": "Dr. Martínez"}}},
        ]
    }
    result = list_teachers(mock_classroom_service, course_id="123")
    assert len(result) == 1
    assert result[0]["profile"]["name"]["fullName"] == "Dr. Martínez"


# ── Coursework & Announcements ────────────────────────────────────────────────

from src.classroom import list_coursework, get_coursework, list_announcements


def test_list_coursework_returns_assignments(mock_classroom_service):
    mock_classroom_service.courses().courseWork().list().execute.return_value = {
        "courseWork": [
            {"id": "cw1", "title": "Tarea 1", "dueDate": {"year": 2026, "month": 4, "day": 10}},
            {"id": "cw2", "title": "Tarea 2"},
        ]
    }
    result = list_coursework(mock_classroom_service, course_id="123")
    assert len(result) == 2
    assert result[0]["title"] == "Tarea 1"


def test_list_coursework_returns_empty_when_none(mock_classroom_service):
    mock_classroom_service.courses().courseWork().list().execute.return_value = {}
    result = list_coursework(mock_classroom_service, course_id="123")
    assert result == []


def test_get_coursework_returns_detail(mock_classroom_service):
    mock_classroom_service.courses().courseWork().get().execute.return_value = {
        "id": "cw1", "title": "Tarea 1", "description": "Resolver ejercicios"
    }
    result = get_coursework(mock_classroom_service, course_id="123", coursework_id="cw1")
    assert result["description"] == "Resolver ejercicios"


def test_list_announcements_returns_list(mock_classroom_service):
    mock_classroom_service.courses().announcements().list().execute.return_value = {
        "announcements": [
            {"id": "a1", "text": "No hay clase el lunes"},
        ]
    }
    result = list_announcements(mock_classroom_service, course_id="123")
    assert len(result) == 1
    assert result[0]["text"] == "No hay clase el lunes"


# ── Submissions ───────────────────────────────────────────────────────────────

from src.classroom import (
    list_my_submissions,
    get_my_submission,
    add_drive_attachment,
    add_link_attachment,
    remove_attachment,
    turn_in_submission,
    reclaim_submission,
)


def test_list_my_submissions_returns_list(mock_classroom_service):
    mock_classroom_service.courses().courseWork().studentSubmissions().list().execute.return_value = {
        "studentSubmissions": [
            {"id": "sub1", "state": "TURNED_IN", "assignedGrade": 9.5},
            {"id": "sub2", "state": "NEW"},
        ]
    }
    result = list_my_submissions(mock_classroom_service, course_id="123", coursework_id="cw1")
    assert len(result) == 2
    assert result[0]["state"] == "TURNED_IN"


def test_get_my_submission_returns_detail(mock_classroom_service):
    mock_classroom_service.courses().courseWork().studentSubmissions().get().execute.return_value = {
        "id": "sub1", "assignedGrade": 9.5, "state": "RETURNED"
    }
    result = get_my_submission(mock_classroom_service, course_id="123", coursework_id="cw1", submission_id="sub1")
    assert result["assignedGrade"] == 9.5


def test_add_drive_attachment_calls_modify(mock_classroom_service):
    mock_classroom_service.courses().courseWork().studentSubmissions().modifyAttachments.return_value.execute.return_value = {}
    add_drive_attachment(
        mock_classroom_service,
        course_id="123",
        coursework_id="cw1",
        submission_id="sub1",
        drive_file_id="file123",
    )
    mock_classroom_service.courses().courseWork().studentSubmissions().modifyAttachments.assert_called()


def test_add_link_attachment_calls_modify(mock_classroom_service):
    mock_classroom_service.courses().courseWork().studentSubmissions().modifyAttachments.return_value.execute.return_value = {}
    add_link_attachment(
        mock_classroom_service,
        course_id="123",
        coursework_id="cw1",
        submission_id="sub1",
        url="https://example.com",
        title="Mi referencia",
    )
    mock_classroom_service.courses().courseWork().studentSubmissions().modifyAttachments.assert_called()


def test_turn_in_submission_calls_turnIn(mock_classroom_service):
    mock_classroom_service.courses().courseWork().studentSubmissions().turnIn.return_value.execute.return_value = {}
    turn_in_submission(mock_classroom_service, course_id="123", coursework_id="cw1", submission_id="sub1")
    mock_classroom_service.courses().courseWork().studentSubmissions().turnIn.assert_called()


def test_reclaim_submission_calls_reclaim(mock_classroom_service):
    mock_classroom_service.courses().courseWork().studentSubmissions().reclaim.return_value.execute.return_value = {}
    reclaim_submission(mock_classroom_service, course_id="123", coursework_id="cw1", submission_id="sub1")
    mock_classroom_service.courses().courseWork().studentSubmissions().reclaim.assert_called()
