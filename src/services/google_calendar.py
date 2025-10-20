import datetime
from dataclasses import dataclass
from typing import List
from googleapiclient.errors import HttpError
from src.services.build_service import build_service
from logging import getLogger

logger = getLogger(__name__)

@dataclass
class Event:
    summary: str
    start: datetime.datetime
    end: datetime.datetime
    is_all_day: bool

def get_list_events(max_results: int = 10) -> List[Event] | None:
    try:

        service = build_service("calendar", "v3")

        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
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
        items = events_result.get("items", [])

        upcoming_events = []

        if not items:
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

    except HttpError as e:
        logger.error(f"An error occurred: {e}")
        return []
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return []




if __name__ == "__main__":
    events = get_list_events(max_results=3)
    for event in events:
        print(f" {event.start} - {event.end} - {event.is_all_day} - {event.summary}")
