from googleapiclient.errors import HttpError

from src.services.google_tasks import list_tasks
from typing import List, Dict, Any
import datetime
import logging

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
            "due": due,
            "notes": notes,
        }
        result.append(task_dict)

    logger.info("Finished processing tasks, returning %d structured tasks", len(result))
    return result


if __name__ == "__main__":
    tasks2 = get_structured_tasks()
    print(tasks2)
    for task in tasks2:
        print(task)
