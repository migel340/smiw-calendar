import datetime
from dataclasses import dataclass
from typing import List
from googleapiclient.errors import HttpError
from src.services.build_service import build_service

@dataclass
class Event:
    summary: str
    start: datetime.datetime
    end: datetime.datetime
    is_all_day: bool

def list_upcoming_events(service_name, max_results: int) -> List[Event]:
    try:
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        print(f"Getting the upcoming {max_results} events")
        events_result = (
            service_name.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        items = events_result.get("items", [])

        upcoming_events = []

        if not items:
            print("No upcoming events found.")
            return []

        for item in items:
            if 'dateTime' in item['start']:
                start_time = datetime.datetime.fromisoformat(item['start']['dateTime'])
                end_time = datetime.datetime.fromisoformat(item['end']['dateTime'])
                is_all_day = False
            else:
                start_time = datetime.datetime.fromisoformat(item['start']['date'])
                end_time = datetime.datetime.fromisoformat(item['end']['date'])
                is_all_day = True

            event = Event(
                summary=item['summary'],
                start=start_time,
                end=end_time,
                is_all_day=is_all_day
            )
            upcoming_events.append(event)
        return upcoming_events

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

if __name__ == "__main__":
    calendar_service = build_service("calendar", "v3")
    if calendar_service:
        events = list_upcoming_events(service_name=calendar_service, max_results=3)
        for event in events:
            print(f" {event.start.strftime('%Y-%m-%d %H:%M')} - {event.summary}")
