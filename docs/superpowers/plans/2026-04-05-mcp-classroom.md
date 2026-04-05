# MCP Google Classroom Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an MCP server that exposes 16 Google Classroom + Drive tools for a student user via OAuth2.

**Architecture:** Python MCP server using the `mcp` SDK with two tool modules (classroom, drive) and a shared auth module that handles OAuth2 token persistence. Tools are registered in a central server entry point.

**Tech Stack:** Python 3.11+, `mcp[cli]`, `google-api-python-client`, `google-auth-oauthlib`, `pytest`, `pytest-mock`

---

## File Structure

```
mcp-classroom/
├── src/
│   ├── __init__.py
│   ├── server.py          # MCP server entry point, registers all tools
│   ├── auth.py            # OAuth2 flow + token cache
│   ├── classroom.py       # 14 Classroom API tools
│   └── drive.py           # 2 Drive API tools
├── tests/
│   ├── conftest.py        # Shared fixtures (mock credentials, mock services)
│   ├── test_auth.py
│   ├── test_classroom.py
│   └── test_drive.py
├── client_secret_*.json   # Already exists
├── .gitignore
├── requirements.txt
└── pyproject.toml
```

---

### Task 1: Project scaffold & dependencies

**Files:**
- Create: `mcp-classroom/requirements.txt`
- Create: `mcp-classroom/pyproject.toml`
- Create: `mcp-classroom/.gitignore`
- Create: `mcp-classroom/src/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```text
mcp[cli]>=1.0.0
google-api-python-client>=2.100.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.2.0
pytest>=7.4.0
pytest-mock>=3.12.0
```

- [ ] **Step 2: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "mcp-classroom"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "mcp[cli]>=1.0.0",
    "google-api-python-client>=2.100.0",
    "google-auth-oauthlib>=1.1.0",
    "google-auth-httplib2>=0.2.0",
]

[project.scripts]
mcp-classroom = "src.server:main"
```

- [ ] **Step 3: Create .gitignore**

```gitignore
__pycache__/
*.pyc
*.pyo
.env
token.json
*.egg-info/
dist/
.pytest_cache/
```

- [ ] **Step 4: Create src/__init__.py**

```python
```
(empty file)

- [ ] **Step 5: Install dependencies**

```bash
cd C:/Users/Isaac/Desktop/utez/mcp-classroom
pip install -r requirements.txt
```

Expected: All packages install without errors.

- [ ] **Step 6: Commit**

```bash
git init
git add requirements.txt pyproject.toml .gitignore src/__init__.py
git commit -m "feat: scaffold mcp-classroom project"
```

---

### Task 2: OAuth2 authentication module

**Files:**
- Create: `src/auth.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_auth.py`

- [ ] **Step 1: Write failing tests for auth**

Create `tests/__init__.py` (empty), then `tests/test_auth.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/Users/Isaac/Desktop/utez/mcp-classroom
pytest tests/test_auth.py -v
```

Expected: `ImportError: cannot import name 'get_credentials' from 'src.auth'`

- [ ] **Step 3: Implement src/auth.py**

```python
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me",
    "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
    "https://www.googleapis.com/auth/classroom.rosters.readonly",
    "https://www.googleapis.com/auth/classroom.announcements.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
]

TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "token.json")
CLIENT_SECRET_GLOB = os.path.join(
    os.path.dirname(__file__),
    "..",
    "client_secret_*.json",
)


def _find_client_secret() -> str:
    import glob
    matches = glob.glob(CLIENT_SECRET_GLOB)
    if not matches:
        raise FileNotFoundError("No client_secret_*.json found in project root")
    return matches[0]


def get_credentials() -> Credentials:
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                _find_client_secret(), SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return creds
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_auth.py -v
```

Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/auth.py tests/__init__.py tests/test_auth.py
git commit -m "feat: add OAuth2 auth module with token caching"
```

---

### Task 3: Shared test fixtures

**Files:**
- Create: `tests/conftest.py`

- [ ] **Step 1: Create conftest.py with shared mock services**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add tests/conftest.py
git commit -m "test: add shared fixtures for Google API mocks"
```

---

### Task 4: Classroom tools — Courses & People

**Files:**
- Create: `src/classroom.py` (initial: 4 tools)
- Create: `tests/test_classroom.py` (initial tests)

- [ ] **Step 1: Write failing tests for list_courses, get_course, list_students, list_teachers**

Create `tests/test_classroom.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_classroom.py -v
```

Expected: `ImportError: cannot import name 'list_courses' from 'src.classroom'`

- [ ] **Step 3: Implement src/classroom.py — Courses & People tools**

```python
from typing import Any


def list_courses(service) -> list[dict]:
    result = service.courses().list().execute()
    return result.get("courses", [])


def get_course(service, course_id: str) -> dict:
    return service.courses().get(id=course_id).execute()


def list_students(service, course_id: str) -> list[dict]:
    result = service.courses().students().list(courseId=course_id).execute()
    return result.get("students", [])


def list_teachers(service, course_id: str) -> list[dict]:
    result = service.courses().teachers().list(courseId=course_id).execute()
    return result.get("teachers", [])
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_classroom.py -v
```

Expected: 5 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/classroom.py tests/test_classroom.py
git commit -m "feat: add list_courses, get_course, list_students, list_teachers tools"
```

---

### Task 5: Classroom tools — Coursework & Announcements

**Files:**
- Modify: `src/classroom.py` (add 3 tools)
- Modify: `tests/test_classroom.py` (add tests)

- [ ] **Step 1: Add failing tests for list_coursework, get_coursework, list_announcements**

Append to `tests/test_classroom.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_classroom.py::test_list_coursework_returns_assignments -v
```

Expected: `ImportError: cannot import name 'list_coursework'`

- [ ] **Step 3: Add to src/classroom.py**

```python
def list_coursework(service, course_id: str) -> list[dict]:
    result = service.courses().courseWork().list(courseId=course_id).execute()
    return result.get("courseWork", [])


def get_coursework(service, course_id: str, coursework_id: str) -> dict:
    return service.courses().courseWork().get(
        courseId=course_id, id=coursework_id
    ).execute()


def list_announcements(service, course_id: str) -> list[dict]:
    result = service.courses().announcements().list(courseId=course_id).execute()
    return result.get("announcements", [])
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_classroom.py -v
```

Expected: All PASSED (9 total)

- [ ] **Step 5: Commit**

```bash
git add src/classroom.py tests/test_classroom.py
git commit -m "feat: add list_coursework, get_coursework, list_announcements tools"
```

---

### Task 6: Classroom tools — Submissions

**Files:**
- Modify: `src/classroom.py` (add 5 tools)
- Modify: `tests/test_classroom.py` (add tests)

- [ ] **Step 1: Add failing tests for submissions**

Append to `tests/test_classroom.py`:

```python
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
    mock_classroom_service.courses().courseWork().studentSubmissions().modifyAttachments().execute.return_value = {}
    result = add_drive_attachment(
        mock_classroom_service,
        course_id="123",
        coursework_id="cw1",
        submission_id="sub1",
        drive_file_id="file123",
    )
    mock_classroom_service.courses().courseWork().studentSubmissions().modifyAttachments.assert_called_once()


def test_add_link_attachment_calls_modify(mock_classroom_service):
    mock_classroom_service.courses().courseWork().studentSubmissions().modifyAttachments().execute.return_value = {}
    result = add_link_attachment(
        mock_classroom_service,
        course_id="123",
        coursework_id="cw1",
        submission_id="sub1",
        url="https://example.com",
        title="Mi referencia",
    )
    mock_classroom_service.courses().courseWork().studentSubmissions().modifyAttachments.assert_called_once()


def test_turn_in_submission_calls_turnIn(mock_classroom_service):
    mock_classroom_service.courses().courseWork().studentSubmissions().turnIn().execute.return_value = {}
    turn_in_submission(mock_classroom_service, course_id="123", coursework_id="cw1", submission_id="sub1")
    mock_classroom_service.courses().courseWork().studentSubmissions().turnIn.assert_called_once()


def test_reclaim_submission_calls_reclaim(mock_classroom_service):
    mock_classroom_service.courses().courseWork().studentSubmissions().reclaim().execute.return_value = {}
    reclaim_submission(mock_classroom_service, course_id="123", coursework_id="cw1", submission_id="sub1")
    mock_classroom_service.courses().courseWork().studentSubmissions().reclaim.assert_called_once()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_classroom.py::test_list_my_submissions_returns_list -v
```

Expected: `ImportError: cannot import name 'list_my_submissions'`

- [ ] **Step 3: Add submission tools to src/classroom.py**

```python
def list_my_submissions(service, course_id: str, coursework_id: str) -> list[dict]:
    result = service.courses().courseWork().studentSubmissions().list(
        courseId=course_id, courseWorkId=coursework_id, userId="me"
    ).execute()
    return result.get("studentSubmissions", [])


def get_my_submission(service, course_id: str, coursework_id: str, submission_id: str) -> dict:
    return service.courses().courseWork().studentSubmissions().get(
        courseId=course_id, courseWorkId=coursework_id, id=submission_id
    ).execute()


def add_drive_attachment(service, course_id: str, coursework_id: str, submission_id: str, drive_file_id: str) -> dict:
    body = {
        "addAttachments": [{"driveFile": {"id": drive_file_id}}]
    }
    return service.courses().courseWork().studentSubmissions().modifyAttachments(
        courseId=course_id, courseWorkId=coursework_id, id=submission_id, body=body
    ).execute()


def add_link_attachment(service, course_id: str, coursework_id: str, submission_id: str, url: str, title: str = "") -> dict:
    body = {
        "addAttachments": [{"link": {"url": url, "title": title}}]
    }
    return service.courses().courseWork().studentSubmissions().modifyAttachments(
        courseId=course_id, courseWorkId=coursework_id, id=submission_id, body=body
    ).execute()


def remove_attachment(service, course_id: str, coursework_id: str, submission_id: str, drive_file_id: str) -> dict:
    body = {
        "removeAttachments": [{"driveFile": {"id": drive_file_id}}]
    }
    return service.courses().courseWork().studentSubmissions().modifyAttachments(
        courseId=course_id, courseWorkId=coursework_id, id=submission_id, body=body
    ).execute()


def turn_in_submission(service, course_id: str, coursework_id: str, submission_id: str) -> None:
    service.courses().courseWork().studentSubmissions().turnIn(
        courseId=course_id, courseWorkId=coursework_id, id=submission_id, body={}
    ).execute()


def reclaim_submission(service, course_id: str, coursework_id: str, submission_id: str) -> None:
    service.courses().courseWork().studentSubmissions().reclaim(
        courseId=course_id, courseWorkId=coursework_id, id=submission_id, body={}
    ).execute()
```

- [ ] **Step 4: Run all tests**

```bash
pytest tests/test_classroom.py -v
```

Expected: All PASSED (16 total)

- [ ] **Step 5: Commit**

```bash
git add src/classroom.py tests/test_classroom.py
git commit -m "feat: add submission tools (list, get, attach, turn_in, reclaim)"
```

---

### Task 7: Drive tools

**Files:**
- Create: `src/drive.py`
- Create: `tests/test_drive.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_drive.py`:

```python
import pytest
from unittest.mock import MagicMock, patch, mock_open
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
    mock_drive_service.files().create.assert_called_once()
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_drive.py -v
```

Expected: `ImportError: cannot import name 'upload_file_to_drive' from 'src.drive'`

- [ ] **Step 3: Implement src/drive.py**

```python
import os
from googleapiclient.http import MediaFileUpload


def upload_file_to_drive(service, file_path: str, mime_type: str) -> dict:
    file_name = os.path.basename(file_path)
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    return service.files().create(
        body={"name": file_name},
        media_body=media,
        fields="id,name",
    ).execute()


def list_drive_files(service, query: str = "", page_size: int = 20) -> list[dict]:
    kwargs = {
        "pageSize": page_size,
        "fields": "files(id,name,mimeType,modifiedTime)",
    }
    if query:
        kwargs["q"] = query
    result = service.files().list(**kwargs).execute()
    return result.get("files", [])
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_drive.py -v
```

Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/drive.py tests/test_drive.py
git commit -m "feat: add Drive upload and list tools"
```

---

### Task 8: MCP server entry point

**Files:**
- Create: `src/server.py`

- [ ] **Step 1: Implement src/server.py**

```python
from mcp.server.fastmcp import FastMCP
from googleapiclient.discovery import build
from src.auth import get_credentials
from src import classroom, drive

mcp = FastMCP("google-classroom")


def _classroom_service():
    creds = get_credentials()
    return build("classroom", "v1", credentials=creds)


def _drive_service():
    creds = get_credentials()
    return build("drive", "v3", credentials=creds)


# ── Courses ──────────────────────────────────────────────────────────────────

@mcp.tool()
def list_courses() -> list[dict]:
    """List all active courses for the authenticated student."""
    return classroom.list_courses(_classroom_service())


@mcp.tool()
def get_course(course_id: str) -> dict:
    """Get details of a specific course by its ID."""
    return classroom.get_course(_classroom_service(), course_id)


# ── Coursework ────────────────────────────────────────────────────────────────

@mcp.tool()
def list_coursework(course_id: str) -> list[dict]:
    """List all assignments for a given course."""
    return classroom.list_coursework(_classroom_service(), course_id)


@mcp.tool()
def get_coursework(course_id: str, coursework_id: str) -> dict:
    """Get details of a specific assignment (due date, description, etc.)."""
    return classroom.get_coursework(_classroom_service(), course_id, coursework_id)


# ── Submissions ───────────────────────────────────────────────────────────────

@mcp.tool()
def list_my_submissions(course_id: str, coursework_id: str) -> list[dict]:
    """List your submissions for a specific assignment (state, grade, attachments)."""
    return classroom.list_my_submissions(_classroom_service(), course_id, coursework_id)


@mcp.tool()
def get_my_submission(course_id: str, coursework_id: str, submission_id: str) -> dict:
    """Get full details of one of your submissions including assigned grade."""
    return classroom.get_my_submission(_classroom_service(), course_id, coursework_id, submission_id)


@mcp.tool()
def add_drive_attachment(course_id: str, coursework_id: str, submission_id: str, drive_file_id: str) -> dict:
    """Attach an existing Google Drive file to a submission."""
    return classroom.add_drive_attachment(_classroom_service(), course_id, coursework_id, submission_id, drive_file_id)


@mcp.tool()
def add_link_attachment(course_id: str, coursework_id: str, submission_id: str, url: str, title: str = "") -> dict:
    """Attach a URL link to a submission."""
    return classroom.add_link_attachment(_classroom_service(), course_id, coursework_id, submission_id, url, title)


@mcp.tool()
def remove_attachment(course_id: str, coursework_id: str, submission_id: str, drive_file_id: str) -> dict:
    """Remove an attachment from a submission by Drive file ID."""
    return classroom.remove_attachment(_classroom_service(), course_id, coursework_id, submission_id, drive_file_id)


@mcp.tool()
def turn_in_submission(course_id: str, coursework_id: str, submission_id: str) -> str:
    """Mark a submission as turned in."""
    classroom.turn_in_submission(_classroom_service(), course_id, coursework_id, submission_id)
    return "Submission turned in successfully."


@mcp.tool()
def reclaim_submission(course_id: str, coursework_id: str, submission_id: str) -> str:
    """Unsubmit a submission to make further edits."""
    classroom.reclaim_submission(_classroom_service(), course_id, coursework_id, submission_id)
    return "Submission reclaimed. You can now edit it."


# ── Announcements ─────────────────────────────────────────────────────────────

@mcp.tool()
def list_announcements(course_id: str) -> list[dict]:
    """List announcements for a course."""
    return classroom.list_announcements(_classroom_service(), course_id)


# ── People ────────────────────────────────────────────────────────────────────

@mcp.tool()
def list_students(course_id: str) -> list[dict]:
    """List all students in a course."""
    return classroom.list_students(_classroom_service(), course_id)


@mcp.tool()
def list_teachers(course_id: str) -> list[dict]:
    """List all teachers in a course."""
    return classroom.list_teachers(_classroom_service(), course_id)


# ── Drive ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def upload_file_to_drive(file_path: str, mime_type: str) -> dict:
    """Upload a local file to Google Drive. Returns the Drive file ID to use in attachments."""
    return drive.upload_file_to_drive(_drive_service(), file_path, mime_type)


@mcp.tool()
def list_drive_files(query: str = "", page_size: int = 20) -> list[dict]:
    """List files in your Google Drive. Optionally filter with a query string."""
    return drive.list_drive_files(_drive_service(), query, page_size)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run all tests to confirm nothing broke**

```bash
pytest tests/ -v
```

Expected: All PASSED (20+ tests)

- [ ] **Step 3: Commit**

```bash
git add src/server.py
git commit -m "feat: wire all 16 tools into MCP server entry point"
```

---

### Task 9: Smoke test — first run

**Files:** No code changes, just validation.

- [ ] **Step 1: Run the MCP server in dev mode**

```bash
cd C:/Users/Isaac/Desktop/utez/mcp-classroom
mcp dev src/server.py
```

Expected: Browser opens for Google OAuth consent. After login, terminal shows `MCP server running`.

- [ ] **Step 2: Verify token.json was created**

```bash
ls -la token.json
```

Expected: File exists with recent timestamp.

- [ ] **Step 3: Test a tool via MCP inspector**

In the MCP Inspector UI (opened by `mcp dev`), call `list_courses` with no arguments.

Expected: Returns a JSON array of your Google Classroom courses.

- [ ] **Step 4: Register the server in Claude Code settings**

Add to `~/.claude/settings.json` under `mcpServers`:

```json
"google-classroom": {
  "command": "python",
  "args": ["C:/Users/Isaac/Desktop/utez/mcp-classroom/src/server.py"],
  "cwd": "C:/Users/Isaac/Desktop/utez/mcp-classroom"
}
```

- [ ] **Step 5: Final commit**

```bash
git add .
git commit -m "feat: mcp-classroom v0.1.0 complete — 16 student tools"
```

---

## Self-Review

**Spec coverage:**
- ✅ list_courses, get_course
- ✅ list_coursework, get_coursework
- ✅ list_my_submissions, get_my_submission
- ✅ add_drive_attachment, add_link_attachment, remove_attachment
- ✅ turn_in_submission, reclaim_submission
- ✅ list_announcements
- ✅ list_students, list_teachers
- ✅ upload_file_to_drive, list_drive_files

**No placeholders found.**

**Type consistency:** All function signatures in server.py match the definitions in classroom.py and drive.py.
