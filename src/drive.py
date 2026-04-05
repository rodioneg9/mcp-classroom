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
