#!/usr/bin/env python3
"""Read a specific Gmail message by ID."""

import argparse
import base64
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from auth_common import get_credentials, add_profile_args, handle_profile_args, GMAIL_READONLY

try:
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Run: pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)


def get_body(payload):
    """Extract email body from payload."""
    body = ""
    
    if 'body' in payload and payload['body'].get('data'):
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='replace')
    
    if 'parts' in payload:
        for part in payload['parts']:
            mime_type = part.get('mimeType', '')
            if mime_type == 'text/plain':
                if part['body'].get('data'):
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
                    break
            elif mime_type == 'text/html' and not body:
                if part['body'].get('data'):
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
            elif 'parts' in part:
                body = get_body(part) or body
    
    return body


def read_message(profile='default', message_id=None):
    """Read a specific email message."""
    creds = get_credentials(profile, GMAIL_READONLY)
    service = build('gmail', 'v1', credentials=creds)
    
    message = service.users().messages().get(
        userId='me', id=message_id, format='full'
    ).execute()
    
    headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
    
    print("=" * 60)
    print(f"From: {headers.get('From', 'Unknown')}")
    print(f"To: {headers.get('To', 'Unknown')}")
    print(f"Date: {headers.get('Date', 'Unknown')}")
    print(f"Subject: {headers.get('Subject', '(no subject)')}")
    print("=" * 60)
    
    body = get_body(message.get('payload', {}))
    
    # Strip HTML
    if '<html' in body.lower() or '<div' in body.lower():
        body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL | re.IGNORECASE)
        body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL | re.IGNORECASE)
        body = re.sub(r'<[^>]+>', ' ', body)
        body = re.sub(r'\s+', ' ', body).strip()
    
    print(f"\n{body}\n")
    
    # Attachments
    attachments = []
    if 'parts' in message.get('payload', {}):
        for part in message['payload']['parts']:
            if part.get('filename'):
                attachments.append({
                    'filename': part['filename'],
                    'mimeType': part.get('mimeType'),
                })
    
    if attachments:
        print("=" * 60)
        print("Attachments:")
        for att in attachments:
            print(f"  📎 {att['filename']} ({att['mimeType']})")
    
    print("=" * 60)
    print(f"Message ID: {message_id}")
    print(f"Thread ID: {message.get('threadId')}")


def main():
    parser = argparse.ArgumentParser(description='Read Gmail message')
    add_profile_args(parser)
    parser.add_argument('--id', required=True, help='Message ID')
    args = parser.parse_args()
    
    handle_profile_args(args)
    read_message(profile=args.profile, message_id=args.id)


if __name__ == '__main__':
    main()
