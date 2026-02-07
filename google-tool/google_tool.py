#!/usr/bin/env python3
"""
google-tool: Unified CLI for Google Calendar and Gmail.

Usage:
    google-tool auth                     # Run OAuth flow
    google-tool cal list [--days N]      # List upcoming events
    google-tool cal add "title" --at "datetime" [--duration Xh]
    google-tool cal free --date YYYY-MM-DD
    google-tool mail unread [--limit N]  # List unread emails
    google-tool mail read <message-id>   # Read specific email
    google-tool mail send --to X --subject Y --body Z
    google-tool mail search "query"      # Search emails
"""

import os
import sys
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta

import click
from dateutil import parser as dateparser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes for Gmail and Calendar
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
]

# Paths relative to this script
SCRIPT_DIR = Path(__file__).parent
CREDENTIALS_FILE = SCRIPT_DIR / 'credentials.json'
TOKEN_FILE = SCRIPT_DIR / 'token.json'


def get_credentials():
    """Get valid credentials, refreshing or running OAuth flow as needed."""
    creds = None
    
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                click.echo(f"Error: {CREDENTIALS_FILE} not found.", err=True)
                click.echo("Download OAuth credentials from Google Cloud Console.", err=True)
                sys.exit(1)
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
        
        # Restrict permissions
        os.chmod(TOKEN_FILE, 0o600)
    
    return creds


def get_calendar_service():
    """Get Google Calendar API service."""
    creds = get_credentials()
    return build('calendar', 'v3', credentials=creds)


def get_gmail_service():
    """Get Gmail API service."""
    creds = get_credentials()
    return build('gmail', 'v1', credentials=creds)


# ============================================================
# CLI Structure
# ============================================================

@click.group()
def cli():
    """Google Calendar and Gmail CLI tool."""
    pass


@cli.command()
def auth():
    """Run OAuth authentication flow."""
    click.echo("Starting OAuth flow...")
    creds = get_credentials()
    click.echo(f"✓ Authenticated successfully. Token saved to {TOKEN_FILE}")


# ============================================================
# Calendar Commands
# ============================================================

@cli.group()
def cal():
    """Calendar commands."""
    pass


@cal.command('list')
@click.option('--days', default=7, help='Number of days to look ahead')
def cal_list(days):
    """List upcoming calendar events."""
    try:
        service = get_calendar_service()
        
        now = datetime.utcnow().isoformat() + 'Z'
        end = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end,
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            click.echo('No upcoming events.')
            return
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_dt = dateparser.parse(start)
            formatted = start_dt.strftime('%a %b %d %I:%M %p')
            click.echo(f"{formatted} — {event['summary']}")
            
    except HttpError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cal.command('add')
@click.argument('title')
@click.option('--at', 'start_time', required=True, help='Start time (e.g., "2026-02-10 14:00")')
@click.option('--duration', default='1h', help='Duration (e.g., "1h", "30m")')
def cal_add(title, start_time, duration):
    """Add a calendar event."""
    try:
        service = get_calendar_service()
        
        # Parse start time
        start_dt = dateparser.parse(start_time)
        if not start_dt:
            click.echo(f"Error: Could not parse time '{start_time}'", err=True)
            sys.exit(1)
        
        # Parse duration
        if duration.endswith('h'):
            delta = timedelta(hours=float(duration[:-1]))
        elif duration.endswith('m'):
            delta = timedelta(minutes=float(duration[:-1]))
        else:
            delta = timedelta(hours=1)
        
        end_dt = start_dt + delta
        
        event = {
            'summary': title,
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'America/Denver'},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'America/Denver'},
        }
        
        created = service.events().insert(calendarId='primary', body=event).execute()
        click.echo(f"✓ Created: {created['summary']} at {start_dt.strftime('%a %b %d %I:%M %p')}")
        click.echo(f"  Link: {created.get('htmlLink')}")
        
    except HttpError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cal.command('free')
@click.option('--date', 'target_date', required=True, help='Date to check (YYYY-MM-DD)')
def cal_free(target_date):
    """Check free/busy for a specific date."""
    try:
        service = get_calendar_service()
        
        date_dt = dateparser.parse(target_date)
        start = date_dt.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
        end = date_dt.replace(hour=23, minute=59, second=59).isoformat() + 'Z'
        
        body = {
            'timeMin': start,
            'timeMax': end,
            'items': [{'id': 'primary'}]
        }
        
        result = service.freebusy().query(body=body).execute()
        busy = result['calendars']['primary']['busy']
        
        if not busy:
            click.echo(f"✓ {target_date}: Completely free!")
        else:
            click.echo(f"{target_date} busy times:")
            for slot in busy:
                s = dateparser.parse(slot['start']).strftime('%I:%M %p')
                e = dateparser.parse(slot['end']).strftime('%I:%M %p')
                click.echo(f"  {s} - {e}")
                
    except HttpError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ============================================================
# Gmail Commands
# ============================================================

@cli.group()
def mail():
    """Gmail commands."""
    pass


@mail.command('unread')
@click.option('--limit', default=10, help='Maximum emails to show')
def mail_unread(limit):
    """List unread emails."""
    try:
        service = get_gmail_service()
        
        results = service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=limit
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            click.echo('No unread messages.')
            return
        
        for msg in messages:
            msg_data = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            
            headers = {h['name']: h['value'] for h in msg_data['payload']['headers']}
            
            from_addr = headers.get('From', 'Unknown')
            subject = headers.get('Subject', '(no subject)')
            date = headers.get('Date', '')
            
            # Truncate for display
            if len(from_addr) > 30:
                from_addr = from_addr[:27] + '...'
            if len(subject) > 50:
                subject = subject[:47] + '...'
            
            click.echo(f"[{msg['id'][:8]}] {from_addr}")
            click.echo(f"         {subject}")
            
    except HttpError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@mail.command('read')
@click.argument('message_id')
def mail_read(message_id):
    """Read a specific email by ID."""
    try:
        service = get_gmail_service()
        
        # Handle partial IDs
        if len(message_id) < 16:
            results = service.users().messages().list(userId='me', maxResults=100).execute()
            for msg in results.get('messages', []):
                if msg['id'].startswith(message_id):
                    message_id = msg['id']
                    break
        
        msg = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        
        click.echo(f"From: {headers.get('From', 'Unknown')}")
        click.echo(f"To: {headers.get('To', 'Unknown')}")
        click.echo(f"Subject: {headers.get('Subject', '(no subject)')}")
        click.echo(f"Date: {headers.get('Date', '')}")
        click.echo("-" * 60)
        
        # Extract body
        body = ""
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    import base64
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
            import base64
            body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
        
        click.echo(body or "(no text body)")
        
    except HttpError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@mail.command('send')
@click.option('--to', required=True, help='Recipient email')
@click.option('--subject', required=True, help='Email subject')
@click.option('--body', required=True, help='Email body')
def mail_send(to, subject, body):
    """Send an email."""
    try:
        import base64
        from email.mime.text import MIMEText
        
        service = get_gmail_service()
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        sent = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()
        
        click.echo(f"✓ Sent to {to}")
        click.echo(f"  Message ID: {sent['id']}")
        
    except HttpError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@mail.command('search')
@click.argument('query')
@click.option('--limit', default=10, help='Maximum results')
def mail_search(query, limit):
    """Search emails."""
    try:
        service = get_gmail_service()
        
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=limit
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            click.echo('No messages found.')
            return
        
        click.echo(f"Found {len(messages)} message(s):")
        
        for msg in messages:
            msg_data = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            
            headers = {h['name']: h['value'] for h in msg_data['payload']['headers']}
            subject = headers.get('Subject', '(no subject)')
            if len(subject) > 60:
                subject = subject[:57] + '...'
            
            click.echo(f"[{msg['id'][:8]}] {subject}")
            
    except HttpError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
