from src.services.google_auth import get_google_auth
import datetime
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

def build_service():
    try:
        creds = get_google_auth()
        service = build("calendar", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"An error occurred while building the service: {e}")
        return None

def list_upcoming_events(service, max_results=3):
    try:
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        print(f"Getting the upcoming {max_results} events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        if not events:
            print("No upcoming events found.")
            return
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    service = build_service()
    if service:
        list_upcoming_events(service)