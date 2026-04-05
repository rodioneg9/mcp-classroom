_COURSE_FIELDS = {"id", "name", "section", "courseState", "alternateLink"}


def list_courses(service) -> list[dict]:
    result = service.courses().list().execute()
    return [{k: v for k, v in c.items() if k in _COURSE_FIELDS} for c in result.get("courses", [])]


def get_course(service, course_id: str) -> dict:
    return service.courses().get(id=course_id).execute()


def list_students(service, course_id: str) -> list[dict]:
    result = service.courses().students().list(courseId=course_id).execute()
    return result.get("students", [])


def list_teachers(service, course_id: str) -> list[dict]:
    result = service.courses().teachers().list(courseId=course_id).execute()
    return result.get("teachers", [])


_SLIM_FIELDS = {"id", "title", "state", "dueDate", "dueTime", "topicId", "maxPoints"}


def list_coursework(service, course_id: str) -> list[dict]:
    result = service.courses().courseWork().list(courseId=course_id).execute()
    items = result.get("courseWork", [])
    return [{k: v for k, v in item.items() if k in _SLIM_FIELDS} for item in items]


def get_coursework(service, course_id: str, coursework_id: str) -> dict:
    item = service.courses().courseWork().get(
        courseId=course_id, id=coursework_id
    ).execute()
    item.pop("materials", None)
    return item


def list_announcements(service, course_id: str) -> list[dict]:
    result = service.courses().announcements().list(courseId=course_id).execute()
    return result.get("announcements", [])


def _strip_attachments(submission: dict) -> dict:
    assignment = submission.get("assignmentSubmission", {})
    if "attachments" in assignment:
        submission = {**submission, "assignmentSubmission": {
            **assignment,
            "attachmentCount": len(assignment["attachments"]),
        }}
        del submission["assignmentSubmission"]["attachments"]
    return submission


def list_my_submissions(service, course_id: str, coursework_id: str) -> list[dict]:
    result = service.courses().courseWork().studentSubmissions().list(
        courseId=course_id, courseWorkId=coursework_id, userId="me"
    ).execute()
    return [_strip_attachments(s) for s in result.get("studentSubmissions", [])]


def get_my_submission(service, course_id: str, coursework_id: str, submission_id: str) -> dict:
    submission = service.courses().courseWork().studentSubmissions().get(
        courseId=course_id, courseWorkId=coursework_id, id=submission_id
    ).execute()
    return _strip_attachments(submission)


def _extract_attachment(a: dict) -> dict:
    if "driveFile" in a:
        raw = a["driveFile"]
        # Teacher materials: {"driveFile": {"driveFile": {...}, "shareMode": ...}}
        # Student submissions: {"driveFile": {"id": ..., "title": ...}}
        f = raw.get("driveFile", raw)
        return {"type": "drive", "title": f.get("title", ""), "driveFileId": f.get("id", ""), "link": f.get("alternateLink", "")}
    if "link" in a:
        return {"type": "link", "title": a["link"].get("title", ""), "url": a["link"].get("url", "")}
    return {"type": "unknown", "raw": str(a)[:100]}


def list_submission_attachments(service, course_id: str, coursework_id: str, submission_id: str) -> list[dict]:
    submission = service.courses().courseWork().studentSubmissions().get(
        courseId=course_id, courseWorkId=coursework_id, id=submission_id
    ).execute()
    attachments = submission.get("assignmentSubmission", {}).get("attachments", [])
    return [_extract_attachment(a) for a in attachments]


def add_drive_attachment(service, course_id: str, coursework_id: str, submission_id: str, drive_file_id: str) -> dict:
    body = {"addAttachments": [{"driveFile": {"id": drive_file_id}}]}
    return service.courses().courseWork().studentSubmissions().modifyAttachments(
        courseId=course_id, courseWorkId=coursework_id, id=submission_id, body=body
    ).execute()


def add_link_attachment(service, course_id: str, coursework_id: str, submission_id: str, url: str, title: str = "") -> dict:
    body = {"addAttachments": [{"link": {"url": url, "title": title}}]}
    return service.courses().courseWork().studentSubmissions().modifyAttachments(
        courseId=course_id, courseWorkId=coursework_id, id=submission_id, body=body
    ).execute()


def remove_attachment(service, course_id: str, coursework_id: str, submission_id: str, drive_file_id: str) -> dict:
    body = {"removeAttachments": [{"driveFile": {"id": drive_file_id}}]}
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
