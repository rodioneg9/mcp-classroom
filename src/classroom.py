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
