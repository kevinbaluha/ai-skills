#!/usr/bin/env python3
"""Send email via Gmail."""

import argparse
import base64
import mimetypes
import sys
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from auth_common import get_credentials, add_profile_args, handle_profile_args, GMAIL_SEND

try:
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Run: pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)


def create_message(to, subject, body, cc=None, bcc=None, html=False, attachments=None, reply_to=None):
    """Create email message."""
    if attachments:
        message = MIMEMultipart()
        message.attach(MIMEText(body, 'html' if html else 'plain'))
        
        for filepath in attachments:
            path = Path(filepath)
            if not path.exists():
                print(f"Warning: Attachment not found: {filepath}")
                continue
            
            content_type, _ = mimetypes.guess_type(str(path))
            if content_type is None:
                content_type = 'application/octet-stream'
            main_type, sub_type = content_type.split('/', 1)
            
            with open(path, 'rb') as f:
                attachment = MIMEBase(main_type, sub_type)
                attachment.set_payload(f.read())
            
            from email import encoders
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment', filename=path.name)
            message.attach(attachment)
    else:
        message = MIMEText(body, 'html' if html else 'plain')
    
    message['To'] = to
    message['Subject'] = subject
    if cc:
        message['Cc'] = cc
    if bcc:
        message['Bcc'] = bcc
    if reply_to:
        message['In-Reply-To'] = reply_to
        message['References'] = reply_to
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}


def send_email(profile='default', to=None, subject=None, body=None, **kwargs):
    """Send email via Gmail API."""
    creds = get_credentials(profile, GMAIL_SEND)
    service = build('gmail', 'v1', credentials=creds)
    
    message = create_message(to, subject, body, **kwargs)
    result = service.users().messages().send(userId='me', body=message).execute()
    
    print(f"✅ Email sent!")
    print(f"   To: {to}")
    print(f"   Subject: {subject}")
    print(f"   ID: {result['id']}")
    return result


def main():
    parser = argparse.ArgumentParser(description='Send email via Gmail')
    add_profile_args(parser)
    parser.add_argument('--to', required=True, help='Recipient')
    parser.add_argument('--subject', required=True, help='Subject')
    parser.add_argument('--body', required=True, help='Body')
    parser.add_argument('--cc', help='CC recipients')
    parser.add_argument('--bcc', help='BCC recipients')
    parser.add_argument('--html', action='store_true', help='HTML body')
    parser.add_argument('--attach', action='append', help='Attachment')
    parser.add_argument('--reply-to', help='Reply to message ID')
    args = parser.parse_args()
    
    handle_profile_args(args)
    send_email(profile=args.profile, to=args.to, subject=args.subject, body=args.body,
               cc=args.cc, bcc=args.bcc, html=args.html, attachments=args.attach,
               reply_to=args.reply_to)


if __name__ == '__main__':
    main()
