# mcp-classroom

MCP server for Google Classroom — read assignments, check submission states, upload files to Drive, and view attached files. Pairs with a Claude Code skill + Playwright for browser automation to work around Google Workspace write restrictions.

## What it can do

| Feature | How |
|---|---|
| List courses | MCP |
| List & get assignments | MCP (slim response — no heavy file metadata) |
| Check submission state & grade | MCP |
| List files attached to a submission | MCP |
| Upload file to Google Drive | MCP |
| Attach file to submission | Playwright (API blocked by Workspace admins) |
| Turn in / Mark as done | Playwright (API blocked by Workspace admins) |
| Unsubmit (reclaim) | Playwright (API blocked by Workspace admins) |

> **Why Playwright?** Google Workspace for Education admins can restrict third-party apps from modifying student submissions via the API (`@ProjectPermissionDenied`). Playwright automates the browser instead, bypassing that restriction entirely.

---

## Requirements

- Python 3.11+
- Node.js (for `playwright-cli`)
- A Google Cloud project with the Classroom API and Drive API enabled

---

## 1. Google Cloud Console setup

### 1.1 Create a project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g. `mcp-classroom`)

### 1.2 Enable APIs
In **APIs & Services → Library**, enable:
- **Google Classroom API**
- **Google Drive API**

### 1.3 Configure OAuth consent screen
1. Go to **APIs & Services → OAuth consent screen**
2. User type: **External**
3. Fill in app name, support email, developer email
4. Add scopes:
   ```
   https://www.googleapis.com/auth/classroom.courses.readonly
   https://www.googleapis.com/auth/classroom.coursework.me
   https://www.googleapis.com/auth/classroom.coursework.students
   https://www.googleapis.com/auth/classroom.student-submissions.me.readonly
   https://www.googleapis.com/auth/classroom.rosters.readonly
   https://www.googleapis.com/auth/classroom.announcements.readonly
   https://www.googleapis.com/auth/drive.file
   https://www.googleapis.com/auth/drive.readonly
   ```
5. Add your Google account as a **test user**
6. Publishing status: you can leave it in **Testing** while developing, or publish to **Production** to avoid the unverified app warning

### 1.4 Create OAuth credentials
1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. Application type: **Desktop app**
4. Download the JSON file
5. Rename it to `client_secret_<...>.json` and place it in the project root (next to `pyproject.toml`)

---

## 2. Install the MCP server

```bash
# Clone the repo
git clone https://github.com/your-username/mcp-classroom.git
cd mcp-classroom

# Install Python dependencies
pip install -e .
```

### First run — authenticate
```bash
mcp-classroom
```
A browser window will open asking you to authorize the app with your Google account. After approval, a `token.json` is saved locally (gitignored).

---

## 3. Register with Claude Code

Add the server to your Claude Code MCP config (`~/.claude/claude.json` or via `claude mcp add`):

```json
{
  "mcpServers": {
    "google-classroom": {
      "command": "mcp-classroom",
      "args": []
    }
  }
}
```

Or if running from source:
```json
{
  "mcpServers": {
    "google-classroom": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/absolute/path/to/mcp-classroom"
    }
  }
}
```

---

## 4. Install Playwright (for browser automation)

```bash
npm install -g playwright-cli
npx playwright install chromium
```

### Save your Google session (one time)
```bash
playwright-cli open --browser=chrome https://accounts.google.com/signin
# Log in manually in the browser window
playwright-cli state-save ~/classroom-auth.json
playwright-cli close
```

---

## 5. Install the Claude Code skill (optional but recommended)

The skill tells Claude how to use the MCP + Playwright together without you having to explain the workflow every time.

1. Copy `skill/SKILL.md` to your Claude skills directory:
   ```
   ~/.claude/skills/google-classroom/SKILL.md
   ```
2. Edit the skill file and fill in your own course IDs and assignment IDs (run `list_courses` and `list_coursework` once to get them).
3. Update the auth state path inside the skill to match where you saved `classroom-auth.json`.
4. Reload plugins in Claude Code: `/reload-plugins`

---

## Available MCP tools

| Tool | Description |
|---|---|
| `list_courses` | List active courses (slim: id, name, section, state) |
| `get_course` | Get full details of a course |
| `list_coursework` | List assignments (slim: id, title, state, dueDate) |
| `get_coursework` | Get assignment details + description (no teacher file attachments) |
| `list_my_submissions` | List your submissions — state, grade, attachment count |
| `get_my_submission` | Get one submission's details |
| `list_submission_attachments` | List titles and Drive IDs of files you've attached |
| `upload_file_to_drive` | Upload a local file to Google Drive |
| `list_drive_files` | Search files in your Drive |
| `add_drive_attachment` | Attach a Drive file to a submission (may be blocked by Workspace) |
| `add_link_attachment` | Attach a URL to a submission (may be blocked by Workspace) |
| `remove_attachment` | Remove an attachment (may be blocked by Workspace) |
| `turn_in_submission` | Turn in a submission (may be blocked by Workspace) |
| `reclaim_submission` | Unsubmit a submission (may be blocked by Workspace) |
| `list_announcements` | List course announcements |
| `list_students` | List students in a course |
| `list_teachers` | List teachers in a course |

> Tools marked "may be blocked by Workspace" return `403 @ProjectPermissionDenied` on institutional Google Workspace accounts. Use Playwright automation instead for those operations.

---

## File structure

```
mcp-classroom/
├── src/
│   ├── server.py      # MCP tool definitions
│   ├── classroom.py   # Classroom API calls
│   ├── drive.py       # Drive API calls
│   └── auth.py        # OAuth flow + scopes
├── skill/
│   └── SKILL.md       # Claude Code skill template
├── tests/
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Gitignored (never commit these)

- `token.json` — your OAuth token
- `client_secret_*.json` — your OAuth client credentials
