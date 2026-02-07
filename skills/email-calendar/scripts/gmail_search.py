#!/usr/bin/env python3
"""Search Gmail messages."""

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


def search_messages(profile='default', query=None, max_results=20):
    """Search Gmail messages."""
    creds = get_credentials(profile, GMAIL_READONLY)
    service = build('gmail', 'v1', credentials=creds)
    
    results = service.users().messages().list(
        userId='me', q=query, maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print(f"No messages found for: {query}")
        return []
    
    print(f"🔍 Found {len(messages)} messages for: {query}\n")
    
    for msg in messages:
        detail = service.users().messages().get(
            userId='me', id=msg['id'], format='metadata',
            metadataHeaders=['From', 'Subject', 'Date']
        ).execute()
        
        headers = {h['name']: h['value'] for h in detail.get('payload', {}).get('headers', [])}
        unread = 'UNREAD' in detail.get('labelIds', [])
        marker = '📬' if unread else '📭'
        
        print(f"{marker} {headers.get('Date', 'Unknown')}")
        print(f"   From: {headers.get('From', 'Unknown')}")
        print(f"   Subject: {headers.get('Subject', '(no subject)')}")
        print(f"   ID: {msg['id']}")
        print()
    
    return messages


def main():
    parser = argparse.ArgumentParser(description='Search Gmail')
    add_profile_args(parser)
    parser.add_argument('--query', '-q', required=True, help='Search query')
    parser.add_argument('--max', type=int, default=20, help='Max results')
    args = parser.parse_args()
    
    handle_profile_args(args)
    search_messages(profile=args.profile, query=args.query, max_results=args.max)


if __name__ == '__main__':
    main()
