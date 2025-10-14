import os
from dotenv import load_dotenv

load_dotenv()

EPD_WIDTH = int(os.getenv("EPD_WIDTH"))
EPD_HEIGHT = int(os.getenv("EPD_HEIGHT"))

OUTDIR = os.getenv("OUTDIR")

GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

CALENDAR_SCOPES = os.getenv("CALENDAR_SCOPES")
TASKS_SCOPES = os.getenv("TASKS_SCOPES")

GOOGLE_API_SCOPES = [TASKS_SCOPES, CALENDAR_SCOPES]

TIMEZONE = os.getenv("TIMEZONE", "UTC")