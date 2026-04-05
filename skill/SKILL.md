---
name: google-classroom
description: Manage Google Classroom assignments using the MCP server and Playwright for browser automation. Use this skill whenever the user mentions homework, assignments, classroom, submitting work, grades, turning in, marking as done, or any Google Classroom task. Invoke BEFORE calling any google-classroom MCP tool or playwright-cli command.
---

# Google Classroom — MCP + Playwright Skill

## Architecture: MCP + Playwright
Google Workspace for Education institutions often block write operations via the API (403 ProjectPermissionDenied). This skill uses two tools:

| Operation | Tool |
|---|---|
| Read courses, assignments, submissions | MCP |
| View already-attached files | MCP (`list_submission_attachments`) |
| Upload file to Drive | MCP (`upload_file_to_drive`) |
| Attach file to submission | **Playwright** |
| Turn in / Mark as done | **Playwright** |
| Unsubmit (reclaim) | **Playwright** |
| Add private comment | **Playwright** |

---

## Setup: populate your course & assignment IDs

Run `list_courses` once to get your course IDs, then `list_coursework` for each course you use frequently. Store them here so Claude never has to re-fetch them.

## My courses (fill in your IDs)

| Course | ID |
|---|---|
| [Course name] | `COURSE_ID` |

## My assignments (fill in your IDs)

| Assignment | Course ID | Assignment ID |
|---|---|---|
| [Assignment name] | `COURSE_ID` | `ASSIGNMENT_ID` |

---

## Workflow: upload file and submit

### Step 1 — Prepare (MCP)
```
upload_file_to_drive   → upload PDF/image to Drive → get driveFileId
list_my_submissions    → get submission ID and current state
```

### Step 2 — Attach and submit (Playwright)
```bash
playwright-cli open --browser=chrome
playwright-cli state-load "/path/to/classroom-auth.json"

playwright-cli goto "https://classroom.google.com/c/{courseId}/a/{assignmentId}/details"

# Click Add or Create → Google Drive
playwright-cli click [button "Add or create"]
playwright-cli click [menuitem "Google Drive"]
# File appears in "Recent" — select it
playwright-cli click [option matching filename]
playwright-cli click [button "Add N item(s)"]

# Submit
playwright-cli click [button "Turn in" or "Mark as done"]
playwright-cli click [button "Turn in" in confirmation dialog]
playwright-cli close
```

### Step 3 — Private comment (Playwright)
```bash
playwright-cli open --browser=chrome
playwright-cli state-load "/path/to/classroom-auth.json"
playwright-cli goto "https://classroom.google.com/c/{courseId}/a/{assignmentId}/details"
playwright-cli click [button "Add private comment"]
playwright-cli fill [textarea] "your comment here"
playwright-cli click [send button]
playwright-cli close
```

---

## Auth state
- Save after first login: `playwright-cli state-save /path/to/classroom-auth.json`
- Load on every subsequent use: `playwright-cli state-load /path/to/classroom-auth.json`
- If state expires, re-authenticate and save again.

## First login (one time)
```bash
playwright-cli open --browser=chrome https://accounts.google.com/signin
# fill in email, click next, fill password, click next
playwright-cli state-save /path/to/classroom-auth.json
playwright-cli close
```

## Context efficiency
- Never call `list_coursework` if IDs are already in this skill.
- Call `get_coursework` only when you need the full assignment description.
- Call `list_my_submissions` to get submission ID and state.

## Dependencies
- `playwright-cli` — `npm install -g playwright-cli`
- Chromium — `npx playwright install chromium`
