from src.services.google_auth import get_google_auth
from googleapiclient.discovery import build

def build_service(service_name: str, version: str):
    try:
        creds = get_google_auth()
        service = build(service_name, version, credentials=creds)
        return service
    except Exception as e:
        print(f"An error occurred while building the service: {e}")
        return None

if __name__ == "__main__":
    calendar_service = build_service("calendar", "v3")
    if calendar_service:
        print("Calendar service built successfully.")
    else:
        print("Failed to build calendar service.")
    task_service = build_service("tasks", "v1")
    if task_service:
        print("Tasks service built successfully.")
    else:
        print("Failed to build tasks service.")