#!/usr/bin/env python3
"""Set up a new email/calendar profile."""

import argparse
import shutil
import sys
from pathlib import Path

# Import from local module
sys.path.insert(0, str(Path(__file__).parent))
from auth_common import (
    get_profile_dir, list_profiles, get_profile_info, save_profile_info,
    get_credentials, GMAIL_READONLY, CALENDAR_READONLY, CONFIG_DIR
)

try:
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Google API libraries not installed.")
    print("Run: pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)


def setup_profile(profile: str, credentials_path: str = None):
    """Set up a new profile with credentials."""
    profile_dir = get_profile_dir(profile)
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    creds_dest = profile_dir / 'credentials.json'
    
    if credentials_path:
        src = Path(credentials_path)
        if not src.exists():
            print(f"ERROR: Credentials file not found: {credentials_path}")
            sys.exit(1)
        shutil.copy(src, creds_dest)
        print(f"✅ Copied credentials to {creds_dest}")
    elif not creds_dest.exists():
        print(f"Profile directory: {profile_dir}")
        print(f"\nTo complete setup:")
        print(f"  1. Download OAuth credentials from Google Cloud Console")
        print(f"  2. Save to: {creds_dest}")
        print(f"  3. Re-run this script")
        return
    
    # Authenticate and get email address
    print(f"\nAuthenticating profile '{profile}'...")
    print("A browser window will open for OAuth consent.\n")
    
    try:
        creds = get_credentials(profile, GMAIL_READONLY)
        service = build('gmail', 'v1', credentials=creds)
        profile_data = service.users().getProfile(userId='me').execute()
        email = profile_data['emailAddress']
        
        save_profile_info(profile, email, profile)
        print(f"✅ Profile '{profile}' configured for: {email}")
        
        # Also auth calendar scope
        print("\nAuthenticating calendar access...")
        get_credentials(profile, CALENDAR_READONLY)
        print("✅ Calendar access configured")
        
    except Exception as e:
        print(f"ERROR: Authentication failed: {e}")
        sys.exit(1)


def delete_profile(profile: str):
    """Delete a profile."""
    profile_dir = get_profile_dir(profile)
    if not profile_dir.exists():
        print(f"Profile '{profile}' does not exist.")
        return
    
    shutil.rmtree(profile_dir)
    print(f"✅ Profile '{profile}' deleted")


def main():
    parser = argparse.ArgumentParser(description='Set up email/calendar profiles')
    parser.add_argument('--profile', '-p', default='default', help='Profile name')
    parser.add_argument('--credentials', '-c', help='Path to credentials.json')
    parser.add_argument('--list', action='store_true', help='List profiles')
    parser.add_argument('--delete', action='store_true', help='Delete profile')
    parser.add_argument('--config-dir', action='store_true', help='Show config directory')
    args = parser.parse_args()
    
    if args.config_dir:
        print(f"Config directory: {CONFIG_DIR}")
        print(f"Profiles stored in: {CONFIG_DIR / 'profiles'}")
        return
    
    if args.list:
        profiles = list_profiles()
        if not profiles:
            print("No profiles configured.")
        else:
            print("Configured profiles:")
            for p in profiles:
                info = get_profile_info(p)
                marker = '→' if p == 'default' else ' '
                print(f"  {marker} {p}: {info.get('email', 'not authenticated')}")
        return
    
    if args.delete:
        delete_profile(args.profile)
        return
    
    setup_profile(args.profile, args.credentials)


if __name__ == '__main__':
    main()
