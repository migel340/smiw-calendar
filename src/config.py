import os
from dotenv import load_dotenv

load_dotenv()

EPD_WIDTH = int(os.getenv("EPD_WIDTH"))
EPD_HEIGHT = int(os.getenv("EPD_HEIGHT"))
OUTDIR = os.getenv("OUTDIR")
GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH")