import datetime
import os
import pickle
import sys

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

def check_for_events(service):
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    calendar_id = 'gary@happycog.com'  # Change this to the ID of the calendar you want to check
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                          maxResults=1, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"Raw start time: {start}")  # Debugging line
        try:
            if 'T' in start:
                start_time = datetime.datetime.fromisoformat(start[:-1])
            else:
                start_time = datetime.datetime.fromisoformat(start)
        except ValueError:
            print(f"Invalid isoformat string: {start}")
            continue
        
        if start_time <= datetime.datetime.utcnow() < start_time + datetime.timedelta(minutes=1):
            event_name = event['summary']
            os.system(f'say "{event_name}"')

def main():
    service = authenticate_google_calendar()
    check_for_events(service)

if __name__ == '__main__':
    main()
