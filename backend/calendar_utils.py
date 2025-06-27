from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# TODO: Replace with your service account credentials file and calendar ID
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = 'primary'  # Or your calendar's ID

def authenticate():
    """Authenticate and return a Google Calendar service client."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    return service

def get_free_slots(start: datetime, end: datetime, duration_minutes=30):
    """Return a list of available time slots between start and end."""
    service = authenticate()
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    # Build a list of busy intervals
    busy = []
    for event in events:
        busy.append((
            datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00')),
            datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
        ))
    # Find free slots
    slots = []
    current = start
    while current + timedelta(minutes=duration_minutes) <= end:
        slot_end = current + timedelta(minutes=duration_minutes)
        if all(not (b[0] < slot_end and current < b[1]) for b in busy):
            slots.append((current, slot_end))
        current += timedelta(minutes=duration_minutes)
    return slots

def book_event(start: datetime, end: datetime, summary: str, description: str):
    """Book an event on the calendar."""
    service = authenticate()
    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': end.isoformat(), 'timeZone': 'UTC'},
    }
    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return {"status": "success", "event_id": created_event['id']}