#!/usr/bin/env python3
"""Create Google Calendar event."""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from auth_common import get_credentials, add_profile_args, handle_profile_args, CALENDAR_FULL

try:
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Run: pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)


def parse_datetime(dt_str):
    """Parse datetime string."""
    formats = [
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d %I:%M %p',
        '%Y-%m-%dT%H:%M',
        '%Y-%m-%d',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Could not parse: {dt_str}")


def create_event(profile='default', title=None, start=None, end=None, 
                 location=None, description=None, attendees=None, 
                 calendar_id='primary', timezone='America/Denver'):
    """Create a calendar event."""
    creds = get_credentials(profile, CALENDAR_FULL)
    service = build('calendar', 'v3', credentials=creds)
    
    start_dt = parse_datetime(start)
    end_dt = parse_datetime(end) if end else start_dt + timedelta(hours=1)
    
    event = {
        'summary': title,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': timezone},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': timezone},
    }
    
    if location:
        event['location'] = location
    if description:
        event['description'] = description
    if attendees:
        event['attendees'] = [{'email': e.strip()} for e in attendees.split(',')]
    
    result = service.events().insert(calendarId=calendar_id, body=event).execute()
    
    print(f"✅ Event created!")
    print(f"   Title: {title}")
    print(f"   Start: {start_dt.strftime('%Y-%m-%d %I:%M %p')}")
    print(f"   End: {end_dt.strftime('%Y-%m-%d %I:%M %p')}")
    if location:
        print(f"   Location: {location}")
    print(f"   ID: {result['id']}")
    print(f"   Link: {result.get('htmlLink', 'N/A')}")
    return result


def main():
    parser = argparse.ArgumentParser(description='Create calendar event')
    add_profile_args(parser)
    parser.add_argument('--title', required=True, help='Event title')
    parser.add_argument('--start', required=True, help='Start (YYYY-MM-DD HH:MM)')
    parser.add_argument('--end', help='End time')
    parser.add_argument('--location', help='Location')
    parser.add_argument('--description', help='Description')
    parser.add_argument('--attendees', help='Emails (comma-sep)')
    parser.add_argument('--calendar', default='primary', help='Calendar ID')
    parser.add_argument('--timezone', default='America/Denver', help='Timezone')
    args = parser.parse_args()
    
    handle_profile_args(args)
    create_event(profile=args.profile, title=args.title, start=args.start,
                 end=args.end, location=args.location, description=args.description,
                 attendees=args.attendees, calendar_id=args.calendar, 
                 timezone=args.timezone)


if __name__ == '__main__':
    main()
