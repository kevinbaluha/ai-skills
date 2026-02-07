#!/usr/bin/env python3
"""Shared authentication module for multi-account support."""

import json
import sys
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("ERROR: Google API libraries not installed.")
    print("Run: pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)

# Base config directory
CONFIG_DIR = Path.home() / '.config' / 'openclaw-email'
PROFILES_FILE = CONFIG_DIR / 'profiles.json'

# Default scopes
GMAIL_READONLY = ['https://www.googleapis.com/auth/gmail.readonly']
GMAIL_SEND = ['https://www.googleapis.com/auth/gmail.send']
GMAIL_MODIFY = ['https://www.googleapis.com/auth/gmail.modify']
CALENDAR_READONLY = ['https://www.googleapis.com/auth/calendar.readonly']
CALENDAR_FULL = ['https://www.googleapis.com/auth/calendar']


def get_profile_dir(profile: str = 'default') -> Path:
    """Get directory for a specific profile."""
    return CONFIG_DIR / 'profiles' / profile


def list_profiles() -> list:
    """List all configured profiles."""
    profiles_dir = CONFIG_DIR / 'profiles'
    if not profiles_dir.exists():
        return []
    return [p.name for p in profiles_dir.iterdir() if p.is_dir() and (p / 'credentials.json').exists()]


def get_profile_info(profile: str = 'default') -> dict:
    """Get profile metadata."""
    profile_dir = get_profile_dir(profile)
    info_file = profile_dir / 'profile.json'
    if info_file.exists():
        return json.loads(info_file.read_text())
    return {'name': profile, 'email': 'unknown'}


def save_profile_info(profile: str, email: str, name: str = None):
    """Save profile metadata."""
    profile_dir = get_profile_dir(profile)
    profile_dir.mkdir(parents=True, exist_ok=True)
    info = {'name': name or profile, 'email': email}
    (profile_dir / 'profile.json').write_text(json.dumps(info, indent=2))


def get_credentials(profile: str = 'default', scopes: list = None) -> Credentials:
    """Get or refresh OAuth credentials for a profile."""
    if scopes is None:
        scopes = GMAIL_READONLY
    
    profile_dir = get_profile_dir(profile)
    creds_file = profile_dir / 'credentials.json'
    
    # Token file named by scope hash for scope separation
    scope_key = '_'.join(sorted([s.split('/')[-1] for s in scopes]))
    token_file = profile_dir / f'token_{scope_key}.json'
    
    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), scopes)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_file.exists():
                print(f"ERROR: Credentials not found for profile '{profile}'")
                print(f"Expected at: {creds_file}")
                print(f"\nTo set up this profile:")
                print(f"  1. Download OAuth credentials from Google Cloud Console")
                print(f"  2. Save to: {creds_file}")
                print(f"\nOr run: python scripts/profile_setup.py --profile {profile}")
                sys.exit(1)
            
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), scopes)
            creds = flow.run_local_server(port=0)
        
        token_file.write_text(creds.to_json())
    
    return creds


def add_profile_args(parser):
    """Add common profile arguments to argparser."""
    parser.add_argument('--profile', '-p', default='default', 
                        help='Account profile to use (default: default)')
    parser.add_argument('--list-profiles', action='store_true',
                        help='List available profiles and exit')


def handle_profile_args(args):
    """Handle profile listing if requested."""
    if getattr(args, 'list_profiles', False):
        profiles = list_profiles()
        if not profiles:
            print("No profiles configured.")
            print(f"\nRun: python scripts/profile_setup.py --profile <name>")
        else:
            print("Available profiles:")
            for p in profiles:
                info = get_profile_info(p)
                print(f"  {p}: {info.get('email', 'unknown')}")
        sys.exit(0)
