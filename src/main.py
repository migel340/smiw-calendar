from src.utils.logger import setup_logger

setup_logger()

from src.app.screens import get_tasks
from hardware.epd_mock import display

if __name__ == "__main__":
    pass