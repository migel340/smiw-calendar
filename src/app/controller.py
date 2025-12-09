"""
Application Controller - Main application orchestrator.

Combines State Pattern (ScreenManager) with Observer Pattern (EventNotifier)
to create the complete e-ink display application.
"""
from typing import Optional
from threading import Thread, Event, Lock
from time import sleep
import logging

from src.app.screens import (
    ScreenManager,
    EventsTodayScreen,
    EventsTomorrowScreen,
    TasksScreen,
    DHT11Screen,
    JokeScreen,
)
from src.app.event_notifier import EventNotifier, get_notifier
from src.app.screens.base_screen import BaseScreen
from src.hardware import get_epd
from src.hardware.button_driver import button_was_pressed
from src.hardware import led_driver

logger = logging.getLogger(__name__)

# Data refresh interval in seconds (5 minutes)
DATA_REFRESH_INTERVAL = 300

# DHT11 refresh interval in seconds
DHT11_REFRESH_INTERVAL = 60
# Joke refresh interval in seconds
JOKE_REFRESH_INTERVAL = 30


class AppController:
    """
    Main application controller.
    
    Orchestrates:
    - Screen management (State Pattern)
    - LED notifications (Observer Pattern)
    - Button input handling
    - Display updates
    """
    
    def __init__(self):
        # Initialize screen manager
        self._screen_manager = ScreenManager()
        
        # Initialize screens
        self._events_today_screen = EventsTodayScreen()
        self._events_tomorrow_screen = EventsTomorrowScreen()
        self._tasks_screen = TasksScreen()
        self._dht11_screen = DHT11Screen()
        self._joke_screen = JokeScreen()
        
        # Register all screens
        self._screen_manager.register_screens([
            self._events_today_screen,
            self._events_tomorrow_screen,
            self._tasks_screen,
            self._dht11_screen,
            self._joke_screen,
        ])
        
        # Initialize event notifier
        self._notifier = get_notifier()
        
        # E-ink display
        self._epd = None
        
        # Control flags
        self._running = False
        self._stop_event = Event()
        self._display_lock = Lock()  # Prevent concurrent display updates
        self._refresh_thread: Optional[Thread] = None
        self._dht11_thread: Optional[Thread] = None
        self._joke_thread: Optional[Thread] = None
    
    @property
    def screen_manager(self) -> ScreenManager:
        """Get the screen manager instance."""
        return self._screen_manager
    
    @property
    def notifier(self) -> EventNotifier:
        """Get the event notifier instance."""
        return self._notifier
    
    def _init_display(self) -> None:
        """Initialize the e-ink display."""
        try:
            # Ensure LED is OFF at startup
            led_driver.turn_off()
            
            self._epd = get_epd()
            self._epd.init()
            self._epd.Clear()
            logger.info("E-ink display initialized")
        except Exception as e:
            logger.exception("Failed to initialize display: %s", e)
            raise
    def _update_display(self, use_partial: bool = False, expected_screen: Optional[BaseScreen] = None) -> None:
        """Render current screen to the e-ink display.
        
        Args:
            use_partial: Use partial refresh (less flashing) if True.
                         Default is False (full refresh) to avoid ghosting.
            expected_screen: If provided, only update if current screen matches.
                            Used to prevent race conditions with background threads.
        """
        if self._epd is None:
            logger.warning("Display not initialized")
            return
        
        with self._display_lock:
            # Check if screen changed while waiting for lock
            if expected_screen is not None and self._screen_manager.current_screen != expected_screen:
                logger.debug("Screen changed, skipping update for %s", expected_screen.name if expected_screen else "None")
                return
            
            try:
                image = self._screen_manager.render_current()
                if image:
                    if use_partial and hasattr(self._epd, 'display_partial'):
                        self._epd.display_partial(image)
                    else:
                        self._epd.display(image)
                    logger.debug("Display updated with screen: %s (partial=%s)", 
                               self._screen_manager.current_screen.name if self._screen_manager.current_screen else "None",
                               use_partial)
            except Exception as e:
                logger.exception("Failed to update display: %s", e)
    
    def _sync_notifier(self) -> None:
        """Sync today's events with the notifier."""
        try:
            events = self._events_today_screen.get_events()
            self._notifier.update_events(events)
            logger.debug("Notifier synced with %d events", len(events))
        except Exception as e:
            logger.exception("Failed to sync notifier: %s", e)
    
    def _refresh_data_loop(self) -> None:
        """Background thread for periodic data refresh."""
        logger.info("Data refresh thread started")
        
        while not self._stop_event.is_set():
            try:
                # Refresh events today (for notifier)
                self._events_today_screen.get_data()
                self._sync_notifier()
                
                logger.info("Periodic data refresh completed")
            except Exception as e:
                logger.exception("Error in data refresh: %s", e)
            
            # Wait for refresh interval
            self._stop_event.wait(timeout=DATA_REFRESH_INTERVAL)
        
        logger.info("Data refresh thread stopped")
    
    def _dht11_refresh_loop(self) -> None:
        """Background thread for DHT11 display refresh with partial update."""
        logger.info("DHT11 refresh thread started")
        
        while not self._stop_event.is_set():
            try:
                # Only refresh if we're on the DHT11 screen
                current = self._screen_manager.current_screen
                if current == self._dht11_screen:
                    # Force refresh of DHT11 data
                    self._dht11_screen.get_data()
                    # Use partial refresh for DHT11, pass expected_screen to prevent race
                    self._update_display(use_partial=True, expected_screen=self._dht11_screen)
                    logger.debug("DHT11 display refreshed (partial)")
            except Exception as e:
                logger.exception("Error in DHT11 refresh: %s", e)
            
            # Wait for DHT11 refresh interval
            self._stop_event.wait(timeout=DHT11_REFRESH_INTERVAL)
        
        logger.info("DHT11 refresh thread stopped")

    def _joke_refresh_loop(self) -> None:
        """Background thread for Joke screen refresh."""
        logger.info("Joke refresh thread started")

        while not self._stop_event.is_set():
            try:
                # Only refresh if we're on the Joke screen
                if self._screen_manager.current_screen == self._joke_screen:
                    self._joke_screen.get_data()
                    # Use full refresh to avoid ghosting on text changes
                    self._update_display(use_partial=False, expected_screen=self._joke_screen)
                    logger.debug("Joke screen refreshed")
            except Exception as e:
                logger.exception("Error in Joke refresh: %s", e)

            self._stop_event.wait(timeout=JOKE_REFRESH_INTERVAL)

        logger.info("Joke refresh thread stopped")

    def handle_button_press(self) -> None:
        """Handle button press - switch to next screen."""
        logger.info("Button pressed - switching screen")
        
        # Switch to next screen
        self._screen_manager.next_screen()
        
        # Update display
        self._update_display()
        
        # If we switched to events today, sync notifier
        if self._screen_manager.current_screen == self._events_today_screen:
            self._sync_notifier()
    
    def run(self) -> None:
        """
        Main application loop.
        
        Initializes display, starts notifier, and handles button input.
        """
        logger.info("Starting application...")
        
        try:
            # Initialize display
            self._init_display()
            
            # Initialize screen manager (enters first screen)
            self._screen_manager.initialize()
            
            # Initial display update - use FULL refresh for first render
            self._update_display(use_partial=False)
            
            # Sync notifier with initial events
            self._sync_notifier()
            
            # Start event notifier
            self._notifier.start()
            
            # Start data refresh thread
            self._running = True
            self._stop_event.clear()
            self._refresh_thread = Thread(target=self._refresh_data_loop, daemon=True)
            self._refresh_thread.start()
            
            # Start DHT11 refresh thread
            self._dht11_thread = Thread(target=self._dht11_refresh_loop, daemon=True)
            self._dht11_thread.start()
            
            # Start Joke refresh thread
            self._joke_thread = Thread(target=self._joke_refresh_loop, daemon=True)
            self._joke_thread.start()
            
            logger.info("Application running. Press button to switch screens.")
            
            # Main loop - handle button presses
            while self._running:
                if button_was_pressed():
                    self.handle_button_press()
                
                sleep(0.1)  # Small delay to prevent CPU spinning
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.exception("Application error: %s", e)
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Clean shutdown of the application."""
        logger.info("Shutting down application...")
        
        # Stop main loop
        self._running = False
        self._stop_event.set()
        
        # Stop notifier
        self._notifier.stop()
        
        # Wait for refresh thread
        if self._refresh_thread:
            self._refresh_thread.join(timeout=5)
            self._refresh_thread = None
        
        # Wait for DHT11 thread
        if self._dht11_thread:
            self._dht11_thread.join(timeout=5)
            self._dht11_thread = None
        
        # Wait for Joke thread
        if self._joke_thread:
            self._joke_thread.join(timeout=5)
            self._joke_thread = None
        
        # Clear display
        if self._epd:
            try:
                self._epd.Clear()
                self._epd.sleep()
            except Exception as e:
                logger.warning("Error clearing display: %s", e)
        
        logger.info("Application shutdown complete")


def create_app() -> AppController:
    """Create and return the application controller."""
    return AppController()
