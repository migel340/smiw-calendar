from googleapiclient.errors import HttpError
from src.services.google_calendar import get_list_events
from src.services.google_tasks import get_list_tasks
from typing import List, Dict, Any
import datetime
import logging
from src.utils.tz import parse_event_datetime, format_datetime

logger = logging.getLogger(__name__)

def get_structured_tasks() -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    logger.info("Starting fetch of tasks from service")
    try:
        tasks = get_list_tasks()
        if isinstance(tasks, list):
            logger.info("Fetched %d raw tasks from service", len(tasks))
        else:
            logger.debug("Fetched tasks object: %r", tasks)
    except HttpError as e:
        logger.error("An HTTP error occurred while fetching tasks: %s", e)
        return result
    except Exception:
        logger.exception("Unexpected error while fetching tasks")
        return result

    logger.info("Processing fetched tasks")
    for task in tasks or []:
        title = getattr(task, "title", None)
        if title is None:
            logger.debug("Skipping task without title: %r", task)
            continue

        due_val = getattr(task, "due", None)
        if due_val is None:
            due = None
        else:
            try:
                due = datetime.datetime.fromisoformat(str(due_val))
                logger.debug("Parsed due for task %s: %s", title, due)
            except Exception:
                due = str(due_val)
                logger.debug("Failed to parse due for task %s, using raw value: %r", title, due_val)

        notes = getattr(task, "notes", None)
        notes = notes if notes and str(notes).strip() else None

        task_dict: Dict[str, Any] = {
            "title": title,
            "due": due.strftime("%Y-%m-%d") if due else None,
            "notes": notes,
        }
        result.append(task_dict)

    logger.info("Finished processing tasks, returning %d structured tasks", len(result))
    return result

def get_structured_events() -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    logger.info("Starting fetch of events from service")
    try:
        events = get_list_events()
        if isinstance(events, list):
            logger.info("Fetched %d raw events from service", len(events))
        else:
            logger.debug("Fetched events object: %r", events)
    except HttpError as e:
        logger.error("An HTTP error occurred while fetching events: %s", e)
        return result
    except Exception:
        logger.exception("Unexpected error while fetching events")
        return result

    logger.info("Processing fetched events")
    for event in events or []:

        # title = None
        # start_dt = None
        # end_dt = None
        # is_all_day = False

        try:

            title = getattr(event, "summary", None)
            if title is None:
                logger.debug("Skipping event without title: %r", event)
                continue

            start_obj = getattr(event, "start", None)
            end_obj = getattr(event, "end", None)

            is_all_day = bool(getattr(event, "is_all_day", False))

            start_dt = parse_event_datetime(start_obj, is_all_day)
            end_dt = parse_event_datetime(end_obj, is_all_day)

        except HttpError as e:
            logger.error("An HTTP error occurred while parsing event: %s", e)
            continue
        except Exception:
            logger.exception("Unexpected error while parsing event: %r", event)
            continue

        start_str = format_datetime(start_dt, is_all_day)

        if is_all_day:
            end_str = None
        else:
            end_str = format_datetime(end_dt, False) if end_dt is not None else None

        event_dict: Dict[str, Any] = {
            "title": title,
            "start": start_str,
            "end": end_str,
            "is_all_day": is_all_day,
        }

        result.append(event_dict)
    logger.info("Finished parsing event for event: %r", len(result))
    result.sort(key=lambda e: (e["start"] is None, e["start"]))
    return result


def get_events() -> list[Dict[str, Any]]:
    logger.warning("get_events() is deprecated; use get_events_today() or get_events_tomorrow()")
    return get_events_today()


def _fetch_events_in_window(start_dt: datetime.datetime, end_dt: datetime.datetime, max_results: int = 250) -> List[Dict[str, Any]]:
    """Fetch raw events from Google Calendar between start_dt and end_dt (both tz-aware)."""
    try:
        time_min_utc = start_dt.astimezone(datetime.timezone.utc)
        time_max_utc = end_dt.astimezone(datetime.timezone.utc)
        logger.debug("Requesting events: time_min=%s time_max=%s", time_min_utc.isoformat(), time_max_utc.isoformat())
        events = get_list_events(max_results=max_results, time_min=time_min_utc.isoformat(), time_max=time_max_utc.isoformat()) or []
        logger.info("Fetched %d events from API for window %s - %s", len(events), start_dt, end_dt)
        return events
    except Exception:
        logger.exception("Failed to fetch events for window %s - %s", start_dt, end_dt)
        return []


def get_events_today() -> List[Dict[str, Any]]:
    """Return structured events that take place (or span) during today in configured timezone."""
    from src.config import TIMEZONE
    from zoneinfo import ZoneInfo
    from datetime import timedelta

    tz = ZoneInfo(TIMEZONE)
    now = datetime.datetime.now(tz)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)

    events = _fetch_events_in_window(today_start, tomorrow_start)

    today_list: List[Dict[str, Any]] = []
    for event in events:
        try:
            title = getattr(event, "summary", None)
            if not title:
                continue

            start_obj = getattr(event, "start", None)
            end_obj = getattr(event, "end", None)
            is_all_day = bool(getattr(event, "is_all_day", False))

            start_dt = parse_event_datetime(start_obj, is_all_day)
            end_dt = parse_event_datetime(end_obj, is_all_day)
            if not start_dt:
                continue

            if today_start <= start_dt < tomorrow_start or (start_dt < today_start and (end_dt is None or end_dt >= today_start)):
                start_str = format_datetime(start_dt, is_all_day)
                end_str = format_datetime(end_dt, is_all_day) if end_dt and not is_all_day else None
                today_list.append({
                    "title": title,
                    "start": start_str,
                    "end": end_str,
                    "is_all_day": is_all_day,
                })
        except Exception:
            logger.exception("Error processing event: %r", event)
            continue

    today_list.sort(key=lambda e: (e["start"] is None, e["start"]))
    logger.info("Returning %d events for today after filtering", len(today_list))
    return today_list


def get_events_tomorrow() -> List[Dict[str, Any]]:
    """Return structured events that take place (or span) tomorrow in configured timezone."""
    from src.config import TIMEZONE
    from zoneinfo import ZoneInfo
    from datetime import timedelta

    tz = ZoneInfo(TIMEZONE)
    now = datetime.datetime.now(tz)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)
    day_after_tomorrow_start = today_start + timedelta(days=2)

    events = _fetch_events_in_window(tomorrow_start, day_after_tomorrow_start)

    tomorrow_list: List[Dict[str, Any]] = []
    for event in events:
        try:
            title = getattr(event, "summary", None)
            if not title:
                continue

            start_obj = getattr(event, "start", None)
            end_obj = getattr(event, "end", None)
            is_all_day = bool(getattr(event, "is_all_day", False))

            start_dt = parse_event_datetime(start_obj, is_all_day)
            end_dt = parse_event_datetime(end_obj, is_all_day)
            if not start_dt:
                continue

            if tomorrow_start <= start_dt < day_after_tomorrow_start or (start_dt < tomorrow_start and (end_dt is None or end_dt >= tomorrow_start)):
                start_str = format_datetime(start_dt, is_all_day)
                end_str = format_datetime(end_dt, is_all_day) if end_dt and not is_all_day else None
                tomorrow_list.append({
                    "title": title,
                    "start": start_str,
                    "end": end_str,
                    "is_all_day": is_all_day,
                })
        except Exception:
            logger.exception("Error processing event: %r", event)
            continue

    tomorrow_list.sort(key=lambda e: (e["start"] is None, e["start"]))
    logger.info("Returning %d events for tomorrow after filtering", len(tomorrow_list))
    return tomorrow_list



if __name__ == "__main__":
    tasks2 = get_structured_tasks()
    print(tasks2)
    for task in tasks2:
        print(task)
    events_today = get_events_today()
    print("Events today:", events_today)
    for event in events_today:
        print(event)

    events_tomorrow = get_events_tomorrow()
    print("Events tomorrow:", events_tomorrow)
    for event in events_tomorrow:
        print(event)
