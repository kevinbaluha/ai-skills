#!/usr/bin/env python3
"""List upcoming Google Calendar events."""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from auth_common import get_credentials, add_profile_args, handle_profile_args, CALENDAR_READONLY

try:
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Run: pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)


def list_events(profile='default', days=7, calendar_id='primary', output_json=False):
    """List upcoming calendar events."""
    creds = get_credentials(profile, CALENDAR_READONLY)
    service = build('calendar', 'v3', credentials=creds)
    
    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=days)).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        maxResults=50,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    if output_json:
        import json
        print(json.dumps(events, indent=2))
        return events
    
    if not events:
        print(f"No events in the next {days} days.")
        return []
    
    print(f"📅 Upcoming events (next {days} days):\n")
    
    current_date = None
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        
        if 'T' in start:
            event_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            event_date = event_dt.strftime('%A, %B %d')
            event_time = event_dt.strftime('%I:%M %p')
        else:
            event_date = datetime.fromisoformat(start).strftime('%A, %B %d')
            event_time = 'All day'
        
        if event_date != current_date:
            current_date = event_date
            print(f"── {event_date} ──")
        
        summary = event.get('summary', '(No title)')
        location = event.get('location', '')
        
        print(f"  {event_time}: {summary}")
        if location:
            print(f"    📍 {location}")
        print(f"    ID: {event['id']}")
        
        attendees = event.get('attendees', [])
        if attendees:
            names = [a.get('email', 'Unknown') for a in attendees[:3]]
            more = len(attendees) - 3
            att_str = ', '.join(names)
            if more > 0:
                att_str += f' (+{more})'
            print(f"    👥 {att_str}")
        print()
    
    return events


def main():
    parser = argparse.ArgumentParser(description='List calendar events')
    add_profile_args(parser)
    parser.add_argument('--days', type=int, default=7, help='Days ahead')
    parser.add_argument('--calendar', default='primary', help='Calendar ID')
    parser.add_argument('--json', action='store_true', help='JSON output')
    args = parser.parse_args()
    
    handle_profile_args(args)
    list_events(profile=args.profile, days=args.days, 
                calendar_id=args.calendar, output_json=args.json)


if __name__ == '__main__':
    main()
