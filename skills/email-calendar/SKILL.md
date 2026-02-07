---
name: email-calendar
description: Read, send, and manage emails via Gmail; check, create, and update calendar events via Google Calendar. Use when the user asks to check email, send an email, look at their calendar, schedule meetings, check upcoming events, or manage their inbox.
---

# Email & Calendar

Manage Gmail and Google Calendar via Google APIs. Supports multiple accounts.

## Setup

### 1. Install dependencies
```bash
# Debian/Ubuntu (apt-managed Python)
sudo apt install python3-google-auth-oauthlib python3-google-api-python-client

# Or with pip (if not externally managed)
pip install google-auth-oauthlib google-api-python-client
```

### 2. Set up a profile
```bash
# Set up default profile (opens browser for OAuth)
python scripts/profile_setup.py --credentials /path/to/credentials.json

# Set up additional profiles
python scripts/profile_setup.py --profile work --credentials /path/to/work-credentials.json
python scripts/profile_setup.py --profile personal --credentials /path/to/personal-credentials.json

# List profiles
python scripts/profile_setup.py --list
```

See `references/setup.md` for Google Cloud Console setup.

## Usage

All scripts support `--profile` (`-p`) to switch accounts:

```bash
# Default profile
python scripts/gmail_check.py

# Specific profile  
python scripts/gmail_check.py -p work
python scripts/gcal_list.py -p personal
```

## Email (Gmail)

### Check Inbox
```bash
python scripts/gmail_check.py --count 10 --unread-only
python scripts/gmail_check.py -p work --json
```

### Read Email
```bash
python scripts/gmail_read.py --id <message_id>
```

### Send Email
```bash
python scripts/gmail_send.py --to "user@example.com" --subject "Hi" --body "Message"
python scripts/gmail_send.py -p work --to "team@company.com" --subject "Update" --body "..." --cc "boss@company.com"
```

Options: `--cc`, `--bcc`, `--html`, `--attach <file>`, `--reply-to <msg_id>`

### Search
```bash
python scripts/gmail_search.py --query "from:someone@example.com is:unread"
```

Search operators: `from:`, `to:`, `subject:`, `after:2024/01/01`, `before:`, `has:attachment`, `is:unread`, `is:starred`

## Calendar

### List Events
```bash
python scripts/gcal_list.py --days 7
python scripts/gcal_list.py -p work --days 1 --json
```

### Create Event
```bash
python scripts/gcal_create.py --title "Meeting" --start "2024-02-15 14:00"
python scripts/gcal_create.py -p work --title "1:1" --start "2024-02-15 14:00" --end "2024-02-15 14:30" --attendees "bob@company.com"
```

Options: `--end`, `--location`, `--description`, `--attendees`, `--calendar`, `--timezone`

## Multi-Account Patterns

**Morning briefing across accounts:**
```bash
echo "=== Work ===" && python scripts/gmail_check.py -p work --unread-only
echo "=== Personal ===" && python scripts/gmail_check.py -p personal --unread-only
```

**Check all calendars:**
```bash
python scripts/gcal_list.py -p work --days 1
python scripts/gcal_list.py -p personal --days 1
```

## Config Location

Profiles stored in: `~/.config/openclaw-email/profiles/<name>/`

Each profile contains:
- `credentials.json` — OAuth client credentials
- `token_*.json` — Auth tokens (auto-generated)
- `profile.json` — Profile metadata
