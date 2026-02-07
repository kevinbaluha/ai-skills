# google-tool

Unified CLI for Google Calendar and Gmail. No third-party services — direct API access with local credential storage.

## Setup

### 1. Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable APIs:
   - Google Calendar API
   - Gmail API
4. Create OAuth 2.0 credentials:
   - Application type: **Desktop app**
   - Download the JSON file
5. Rename to `credentials.json` and place in this directory

### 2. Install Dependencies

```bash
cd google-tool
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Authenticate

```bash
./google_tool.py auth
```

This opens a browser for Google OAuth. After approval, token is saved locally.

## Usage

### Calendar

```bash
# List next 7 days of events
./google_tool.py cal list

# List next 14 days
./google_tool.py cal list --days 14

# Add an event
./google_tool.py cal add "Meeting with Bob" --at "2026-02-10 14:00" --duration 1h

# Check free/busy for a date
./google_tool.py cal free --date 2026-02-10
```

### Email

```bash
# List unread emails
./google_tool.py mail unread

# List more
./google_tool.py mail unread --limit 20

# Read specific email (use ID from unread list)
./google_tool.py mail read abc12345

# Send email
./google_tool.py mail send --to "someone@example.com" --subject "Hello" --body "Hi there!"

# Search
./google_tool.py mail search "from:important@example.com is:unread"
```

## Security

- `credentials.json` — OAuth client secret (do NOT commit)
- `token.json` — Your access/refresh token (do NOT commit)
- Both are in `.gitignore`
- Token file is created with `0600` permissions

## Scopes

The tool requests these permissions:

- `calendar` — Full calendar access (read/write)
- `gmail.readonly` — Read emails
- `gmail.send` — Send emails
- `gmail.modify` — Mark as read, archive, etc.
