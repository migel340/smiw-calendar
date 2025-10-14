from googleapiclient.errors import HttpError
from src.services.google_calendar import list_events
from src.services.google_tasks import list_tasks
from typing import List, Dict, Any
import datetime
import logging
from src.utils.tz import parse_event_datetime, format_datetime

logger = logging.getLogger(__name__)

def get_structured_tasks() -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    logger.info("Starting fetch of tasks from service")
    try:
        tasks = list_tasks()
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
        events = list_events()
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

        title = None
        start_dt = None
        end_dt = None
        is_all_day = False

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

        event_dict = {
            "title": title,
            "start": start_str,
            "end": end_str,
        }

        result.append(event_dict)
    logger.info("Finished parsing event for event: %r", len(result))
    return result


if __name__ == "__main__":
    tasks2 = get_structured_tasks()
    print(tasks2)
    for task in tasks2:
        print(task)
    events = get_structured_events()
    print(events)
    for event in events:
        print(event)
