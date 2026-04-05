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
