import datetime
from dataclasses import dataclass
from typing import List, Optional
from googleapiclient.errors import HttpError
from src.services.build_service import build_service

@dataclass
class Task:
    title: str
    due: Optional[datetime.datetime]
    notes: Optional[str]

def parse_due_date(due_str: str) -> Optional[datetime.datetime]:
    try:
        if '.' in due_str:
            due_str = due_str.split('.')[0]
        if due_str.endswith('Z'):
            due_str = due_str[:-1]
        return datetime.datetime.fromisoformat(due_str)
    except ValueError:
        print(f"Warning: Could not parse due date: {due_str}")
        return None

def parse_title(title: str) -> str:
    if title == "" or title is None:
        return "Titleless"
    return title


def get_list_tasks(max_results: int = 5) -> List[Task]:
    try:

        service = build_service("tasks", "v1")

        task_results = (
            service.tasks()
            .list(
                tasklist="@default",
                maxResults=max_results,
                showCompleted=False,
            )
            .execute()
        )

        items = task_results.get("items", [])
        task_list = []

        for item in items:
            due_str = item.get("due")
            parsed_due = parse_due_date(due_str) if due_str else None
            parsed_title = parse_title(item.get("title"))
            task = Task(
                title=parsed_title,
                due=parsed_due,
                notes=item.get("notes", "")
            )
            task_list.append(task)

        return task_list

    except HttpError as e:
        print(f"An error occurred: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

if __name__ == "__main__":

        tasks = get_list_tasks(max_results=5)
        for task in tasks:
            print(f"Task: {task.title}, Due: {task.due}, Notes: {task.notes}")