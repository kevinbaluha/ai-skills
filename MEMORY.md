# MEMORY.md - ai-skills

## Purpose
Custom AI tool integrations built from scratch for security. No third-party skill services — direct API access with credentials that never leave the machine.

## Components

### google-tool (planned)
- **Status:** Scaffolding
- **Features:** Gmail + Google Calendar unified CLI
- **Auth:** OAuth 2.0 desktop app flow, local token storage

## Decisions

- **2026-02-07:** Created repo. Building Google tools first (calendar + email) using official Google APIs. Avoiding external skill integration services as attack vector.

## TODO

- [ ] Scaffold google-tool Python CLI
- [ ] Implement OAuth flow
- [ ] Calendar: list, add, free/busy
- [ ] Email: unread, read, send, search
- [ ] Create OpenClaw skill wrapper

---

*Last updated: Feb 7, 2026*
