import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.students",
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
