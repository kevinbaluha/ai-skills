# Google API Setup Guide

## 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project (one per account/org, or shared)
3. Enable APIs:
   - **Gmail API**
   - **Google Calendar API**

## 2. Create OAuth Credentials

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Select **Desktop app** as application type
4. Name it (e.g., "OpenClaw Email")
5. Download JSON file

**For multiple accounts:** You can use the same credentials.json for multiple Google accounts, or create separate OAuth clients per account.

## 3. Configure OAuth Consent Screen

1. Go to **APIs & Services > OAuth consent screen**
2. Choose **External** (or Internal for Workspace)
3. Fill required fields:
   - App name: "OpenClaw Email/Calendar"
   - User support email
   - Developer contact email
4. Add scopes (or skip — will be requested at auth time):
   - `gmail.readonly`, `gmail.send`, `gmail.modify`
   - `calendar`, `calendar.readonly`
5. Add test users (your email addresses)

## 4. Set Up Profiles

```bash
# Install dependencies (Debian/Ubuntu)
sudo apt install python3-google-auth-oauthlib python3-google-api-python-client

# Or with pip (if not externally managed)
pip install google-auth-oauthlib google-api-python-client

# Set up first profile (default)
python3 scripts/profile_setup.py --credentials ~/Downloads/credentials.json

# Set up additional profiles
python3 scripts/profile_setup.py --profile work --credentials ~/Downloads/credentials.json
python3 scripts/profile_setup.py --profile personal --credentials ~/Downloads/credentials.json

# Each profile auth opens browser — sign in with different Google accounts
```

## 5. Directory Structure

```
~/.config/openclaw-email/
└── profiles/
    ├── default/
    │   ├── credentials.json
    │   ├── profile.json          # {"name": "default", "email": "you@gmail.com"}
    │   ├── token_gmail.readonly.json
    │   ├── token_gmail.send.json
    │   └── token_calendar.json
    ├── work/
    │   ├── credentials.json
    │   ├── profile.json
    │   └── token_*.json
    └── personal/
        └── ...
```

## Troubleshooting

### "Access blocked" error
- Add your email to **Test users** in OAuth consent screen
- Or publish the app (requires Google verification for sensitive scopes)

### Token expired / invalid
```bash
# Delete tokens for a profile and re-authenticate
rm ~/.config/openclaw-email/profiles/<profile>/token_*.json
python3 scripts/gmail_check.py -p <profile>  # triggers re-auth
```

### "Credentials not found"
```bash
# Check profile setup
python3 scripts/profile_setup.py --list
python3 scripts/profile_setup.py --config-dir
```

### Rate limits
Gmail quotas: ~250 units/second per user
- messages.list: 5 units
- messages.get: 5 units  
- messages.send: 100 units

## Multiple Google Accounts

Each profile = one Google account. The same OAuth credentials (client ID) can be used for multiple profiles — just sign into different accounts during the browser auth flow.

**Tip:** Name profiles by purpose: `work`, `personal`, `client-acme`, etc.
