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


def list_tasks(service_name, max_results: int) -> List[Task]:
    try:
        print(f"Getting {max_results} tasks")
        task_results = (
            service_name.tasks()
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
                notes=item.get("notes", None))
            task_list.append(task)
        return task_list

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

if __name__ == "__main__":
    tasks_service = build_service("tasks", "v1")
    if tasks_service:
        tasks = list_tasks(service_name=tasks_service, max_results=3)
        for task in tasks:
            print(f"Task: {task.title}, Due: {task.due}, Notes: {task.notes}")