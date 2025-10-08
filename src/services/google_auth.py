import datetime

from src.config import GOOGLE_TOKEN_PATH, CALENDAR_SCOPES
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from pathlib import Path

def get_google_auth():
    token_path = Path(GOOGLE_TOKEN_PATH)
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, CALENDAR_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                "credentials.json", scopes=CALENDAR_SCOPES
            )
            flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
            auth_url, _ = flow.authorization_url(prompt='consent')
            print("Please go to this URL and authorize the application:")
            print(auth_url)
            code = input("Enter the authorization code: ")
            flow.fetch_token(code=code)
            creds = flow.credentials
        with open(GOOGLE_TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return creds

if __name__ == "__main__":
    google_service = get_google_auth()
