import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


# ── Courses ───────────────────────────────────────────────────────────────────

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
def list_submission_attachments(course_id: str, coursework_id: str, submission_id: str) -> list[dict]:
    """List titles and IDs of files already attached to a submission (drive files and links)."""
    return classroom.list_submission_attachments(_classroom_service(), course_id, coursework_id, submission_id)


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
