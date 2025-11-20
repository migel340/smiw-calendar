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

def get_list_events(max_results: int = 10, time_min: datetime.datetime | str | None = None, time_max: datetime.datetime | str | None = None) -> List[Event] | None:
    try:

        service = build_service("calendar", "v3")

        params = {
            "calendarId": "primary",
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime",
        }
        
        if time_min is not None:
            if isinstance(time_min, datetime.datetime):
                params["timeMin"] = time_min.isoformat()
            else:
                params["timeMin"] = str(time_min)
        else:
            params["timeMin"] = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        
        if time_max is not None:
            if isinstance(time_max, datetime.datetime):
                params["timeMax"] = time_max.isoformat()
            else:
                params["timeMax"] = str(time_max)
        
        logger.debug("Calling Google Calendar API with params: %s", params)
        events_result = service.events().list(**params).execute()
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
