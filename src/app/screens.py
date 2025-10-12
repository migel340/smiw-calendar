from os import remove
from tkinter.font import names

from googleapiclient.errors import HttpError

from src.services.google_calendar import list_events, Event
from src.services.google_tasks import list_tasks, Task
from logging import getLogger
from typing import List, Dict, Any
import datetime
import logging

logger = logging.getLogger(__name__)

def get_structured_tasks() -> List[Dict[str, Any]] | None:
    try:
        tasks = list_tasks()
        result = []
        for task in tasks:
            if task.title is None:
                continue

            task_dict = {
                "title": task.title,
                "due": None if task.due is None else datetime.datetime.fromisoformat(str(task.due)),
                "notes": task.notes if task.notes and task.notes.strip() else None
            }
            result.append(task_dict)

    except HttpError as e:
        logger.error(f"An error occurred: {e}")

    finally:
        return result

if __name__ == "__main__":
    tasks2 = get_structured_tasks()
    print(tasks2)
    for task in tasks2:
        print(task)