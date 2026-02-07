#!/usr/bin/env python3
"""Check Gmail inbox for recent messages."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from auth_common import get_credentials, add_profile_args, handle_profile_args, GMAIL_READONLY

try:
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Run: pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)


def check_inbox(profile='default', count=10, unread_only=False, output_json=False):
    """Fetch recent emails from inbox."""
    creds = get_credentials(profile, GMAIL_READONLY)
    service = build('gmail', 'v1', credentials=creds)
    
    query = 'in:inbox'
    if unread_only:
        query += ' is:unread'
    
    results = service.users().messages().list(
        userId='me', q=query, maxResults=count
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("No messages found.")
        return []
    
    emails = []
    for msg in messages:
        detail = service.users().messages().get(
            userId='me', id=msg['id'], format='metadata',
            metadataHeaders=['From', 'Subject', 'Date']
        ).execute()
        
        headers = {h['name']: h['value'] for h in detail.get('payload', {}).get('headers', [])}
        
        emails.append({
            'id': msg['id'],
            'from': headers.get('From', 'Unknown'),
            'subject': headers.get('Subject', '(no subject)'),
            'date': headers.get('Date', 'Unknown'),
            'snippet': detail.get('snippet', '')[:100],
            'unread': 'UNREAD' in detail.get('labelIds', [])
        })
    
    if output_json:
        import json
        print(json.dumps(emails, indent=2))
    else:
        for email in emails:
            unread_marker = '📬' if email['unread'] else '📭'
            print(f"{unread_marker} {email['date']}")
            print(f"   From: {email['from']}")
            print(f"   Subject: {email['subject']}")
            print(f"   ID: {email['id']}")
            print(f"   {email['snippet']}...")
            print()
    
    return emails


def main():
    parser = argparse.ArgumentParser(description='Check Gmail inbox')
    add_profile_args(parser)
    parser.add_argument('--count', type=int, default=10, help='Number of messages')
    parser.add_argument('--unread-only', action='store_true', help='Only unread')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    handle_profile_args(args)
    check_inbox(profile=args.profile, count=args.count, 
                unread_only=args.unread_only, output_json=args.json)


if __name__ == '__main__':
    main()
