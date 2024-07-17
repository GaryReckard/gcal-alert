import datetime
import os
import pickle
import re
import sys
from dateutil.parser import isoparse
from dateutil import tz
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_google_calendar():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def extract_zoom_link(text):
    # Basic pattern to match Zoom links
    zoom_pattern = r"https://[\w.-]+\.zoom\.us/[^\s]+"
    match = re.search(zoom_pattern, text)
    if match:
        return match.group(0)
    return None

def check_for_events(service):
    now = datetime.datetime.now(tz.UTC).isoformat()  # Use timezone-aware datetime
    calendar_id = 'primary'  # Change this to the ID of the calendar you want to check
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print("No events found.")
        return

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_name = event.get('summary', 'No Title')
        description = event.get('description', '')
        location = event.get('location', '')


        # Skip all-day events
        if 'date' in event['start']:
            continue



        try:
            start_time = isoparse(start)
        except ValueError:
            print(f"Invalid isoformat string: {start}")
            continue

        if start_time <= datetime.datetime.now(tz.UTC) < start_time + datetime.timedelta(minutes=1):

            # Debugging output
            print(f"Event: {event_name}")
            print(f"Description: {description}")
            print(f"Location: {location}")
            print(f"Raw start time: {start}")
            print(f"Full event details: {event}")  # Print all details of the event

            print(f"Parsed start time: {start_time}, Current time: {datetime.datetime.now(tz.UTC)}")  # Debugging line
            zoom_link = extract_zoom_link(description) or extract_zoom_link(location)
            if zoom_link:
                print(f"Zoom link: {zoom_link}")
                notification_message = f'{event_name}\n{zoom_link}'
                os.system(f'osascript -e \'display notification "{notification_message}" with title "Event Alert"\'')
            else:
                print("No Zoom link found.")
                os.system(f'say \"{event_name}\"')

def main():
    service = authenticate_google_calendar()
    check_for_events(service)

if __name__ == '__main__':
    main()
