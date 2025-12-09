"""
E-ink Calendar Display Application

Main entry point for the Raspberry Pi Zero e-ink display application.
Displays 4 screens in rotation:
1. Today's Events
2. Tomorrow's Events  
3. Tasks
4. DHT11 Temperature/Humidity

Button press rotates between screens.
LED lights up 10 minutes before an event starts.

Design Patterns Used:
- State Pattern: Each screen is a state managed by ScreenManager
- Observer Pattern: EventNotifier observes events and triggers LED
"""
import sys
import logging

from src.utils.logger import setup_logger

# Setup logging first
setup_logger()

logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point for the application."""
    from src.app import create_app
    
    logger.info("=" * 50)
    logger.info("E-ink Calendar Display Starting")
    logger.info("=" * 50)
    
    try:
        app = create_app()
        app.run()
        return 0
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
