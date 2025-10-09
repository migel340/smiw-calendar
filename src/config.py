import os
from dotenv import load_dotenv

load_dotenv()

EPD_WIDTH = int(os.getenv("EPD_WIDTH"))
EPD_HEIGHT = int(os.getenv("EPD_HEIGHT"))

OUTDIR = os.getenv("OUTDIR")

GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TASKS_SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']

GOOGLE_API_SCOPES = CALENDAR_SCOPES + TASKS_SCOPES