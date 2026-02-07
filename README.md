# ai-skills

Custom AI tool integrations — calendar, email, and more. Built from scratch for security and control.

## Tools

### google-tool

Unified CLI for Google Calendar and Gmail access.

```bash
# Calendar
./google-tool cal list --days 7
./google-tool cal add "Meeting" --at "2026-02-10 14:00" --duration 1h

# Email
./google-tool mail unread --limit 10
./google-tool mail read <message-id>
./google-tool mail send --to "someone@example.com" --subject "Hi" --body "Hello!"
./google-tool mail search "is:unread from:important@example.com"
```

## Setup

1. Create a Google Cloud project
2. Enable Gmail API and Calendar API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download `credentials.json` to `google-tool/`
5. Run `./google-tool auth` to complete OAuth flow
6. Token stored locally in `google-tool/token.json`

## Security

- No third-party services
- Credentials never leave your machine
- Minimal scopes requested
- Token stored locally with restricted permissions
