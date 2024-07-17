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

# Determine the absolute path to the directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def authenticate_google_calendar():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    token_path = os.path.join(BASE_DIR, 'token.json')
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(os.path.join(BASE_DIR, 'credentials.json'), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(os.path.join(BASE_DIR, 'token.json'), 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def extract_zoom_link(text):
    # Parse HTML content using BeautifulSoup
    soup = BeautifulSoup(text, 'html.parser')
    # Find all links in the text
    links = soup.find_all('a', href=True)
    # Basic pattern to match Zoom links
    zoom_pattern = r"https://[\w.-]+\.zoom\.us/[^\s]+"
    for link in links:
        href = link['href']
        if re.match(zoom_pattern, href):
            return href
    # Fallback to plain text match
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
        conference_data = event.get('conferenceData', {})

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
            if not zoom_link and 'entryPoints' in conference_data:
                for entry_point in conference_data['entryPoints']:
                    if entry_point['entryPointType'] == 'video':
                        zoom_link = entry_point['uri']
                        break
            if zoom_link:
                print(f"Zoom link: {zoom_link}")
                notification_message = f'{event_name} Starting NOW!\n{zoom_link}'
                os.system(f'terminal-notifier -title "Event Alert" -message "{notification_message}" -open "{zoom_link}"')
                #os.system(f'osascript -e \'display notification "{notification_message}" with title "Event Alert"\'')
                os.system(f'say \"{event_name} starting NOW!\"')
            else:
                print("No Zoom link found.")
                os.system(f'say \"{event_name}\"')

def main():
    service = authenticate_google_calendar()
    check_for_events(service)

if __name__ == '__main__':
    main()
