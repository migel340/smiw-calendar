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
