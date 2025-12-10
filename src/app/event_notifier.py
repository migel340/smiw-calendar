"""
Event Notifier - Observer Pattern implementation for LED notifications.

Monitors upcoming events and turns on LED 10 minutes before event starts.
"""
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from threading import Thread, Event
from zoneinfo import ZoneInfo
import logging
import re

from src.hardware import led_driver
from src.config import TIMEZONE

logger = logging.getLogger(__name__)

# Notification time before event (in minutes)
NOTIFICATION_MINUTES_BEFORE = 10


class EventNotifier:
    """
    Observer that monitors events and triggers LED notifications.
    
    Implements Observer Pattern - observes event data and notifies
    via LED when an event is approaching.
    """
    
    def __init__(self, minutes_before: int = NOTIFICATION_MINUTES_BEFORE):
        self._minutes_before = minutes_before
        self._events: List[Dict[str, Any]] = []
        self._running = False
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        self._led_on = False
        self._tz = ZoneInfo(TIMEZONE)
        self._on_notification_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        # Keep track of events already notified (simple key: title|start)
        self._notified_keys: set[str] = set()
    
    def update_events(self, events: List[Dict[str, Any]]) -> None:
        """
        Update the list of events to monitor (Observer update method).
        
        Args:
            events: List of today's events from EventsTodayScreen.
        """
        # Filter only timed events (not all-day)
        self._events = [e for e in events if not e.get("is_all_day", False)]
        logger.debug("EventNotifier updated with %d timed events", len(self._events))
    
    def add_notification_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add callback to be called when notification is triggered."""
        self._on_notification_callbacks.append(callback)
    
    def _parse_event_time(self, time_str: str) -> Optional[datetime]:
        """
        Parse event time string to datetime object.
        
        Args:
            time_str: Time string in format "HH:MM" or "YYYY-MM-DD HH:MM".
            
        Returns:
            Datetime object or None if parsing fails.
        """
        if not time_str:
            return None
        
        now = datetime.now(self._tz)
        
        try:
            # Try "HH:MM" format
            time_match = re.match(r'^(\d{1,2}):(\d{2})$', time_str.strip())
            if time_match:
                hour, minute = int(time_match.group(1)), int(time_match.group(2))
                return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Try "YYYY-MM-DD HH:MM" format
            dt_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})\s+(\d{1,2}):(\d{2})$', time_str.strip())
            if dt_match:
                year, month, day = int(dt_match.group(1)), int(dt_match.group(2)), int(dt_match.group(3))
                hour, minute = int(dt_match.group(4)), int(dt_match.group(5))
                return datetime(year, month, day, hour, minute, tzinfo=self._tz)
            
            # Try ISO format
            return datetime.fromisoformat(time_str).replace(tzinfo=self._tz)
        except Exception as e:
            logger.warning("Failed to parse time '%s': %s", time_str, e)
            return None
    
    def check_notifications(self) -> Optional[Dict[str, Any]]:
        """
        Check if any event is starting within notification window.
        
        Returns:
            Event dict if notification should be triggered, None otherwise.
        """
        now = datetime.now(self._tz)
        notification_window = timedelta(minutes=self._minutes_before)
        
        for event in self._events:
            start_str = event.get("start")
            if not start_str:
                continue
            
            start_time = self._parse_event_time(start_str)
            if not start_time:
                continue
            
            time_until_event = start_time - now
            
            # Build simple key to prevent duplicate notifications
            key = f"{event.get('title','')}|{start_str}"

            # Check if event is within notification window and hasn't started yet
            if timedelta(0) < time_until_event <= notification_window:
                # Skip if LED is already on for this event
                if key in self._notified_keys and self._led_on:
                    continue
                
                # First notification or re-notification (LED was turned off)
                if key not in self._notified_keys:
                    logger.info("Event '%s' starts in %s", event.get("title"), time_until_event)
                    self._notified_keys.add(key)
                else:
                    logger.debug("Re-notifying '%s' (LED was off)", key)
                
                return event
            # If the event has passed, ensure we clear any notified marker
            if time_until_event <= timedelta(0) and key in self._notified_keys:
                self._notified_keys.discard(key)
        
        return None
    
    def _notify(self, event: Dict[str, Any]) -> None:
        """Trigger LED notification for an event."""
        if not self._led_on:
            led_driver.turn_on()
            self._led_on = True
            logger.info("LED ON - Event '%s' starting soon!", event.get("title"))
            
            # Call registered callbacks
            for callback in self._on_notification_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.exception("Notification callback error: %s", e)
    
    def _clear_notification(self) -> None:
        """Turn off LED notification."""
        if self._led_on:
            led_driver.turn_off()
            self._led_on = False
            logger.info("LED OFF - Notification cleared")
    
    def _monitor_loop(self) -> None:
        """Background thread loop for monitoring events."""
        logger.info("EventNotifier monitor started")
        
        while not self._stop_event.is_set():
            try:
                upcoming_event = self.check_notifications()
                
                if upcoming_event:
                    self._notify(upcoming_event)
                else:
                    self._clear_notification()
                
            except Exception as e:
                logger.exception("Error in notification monitor: %s", e)
            
            # Check every 30 seconds
            self._stop_event.wait(timeout=30)
        
        # Cleanup on stop
        self._clear_notification()
        logger.info("EventNotifier monitor stopped")
    
    def start(self) -> None:
        """Start the background notification monitor."""
        if self._running:
            logger.warning("EventNotifier already running")
            return
        
        self._running = True
        self._stop_event.clear()
        self._thread = Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("EventNotifier started")
    
    def stop(self) -> None:
        """Stop the background notification monitor."""
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        
        self._clear_notification()
        logger.info("EventNotifier stopped")
    
    def is_running(self) -> bool:
        """Check if notifier is running."""
        return self._running
    
    def force_led_on(self) -> None:
        """Manually turn on LED (for testing)."""
        led_driver.turn_on()
        self._led_on = True
    
    def force_led_off(self) -> None:
        """Manually turn off LED (for testing)."""
        led_driver.turn_off()
        self._led_on = False


# Singleton instance
_notifier: Optional[EventNotifier] = None


def get_notifier() -> EventNotifier:
    """Get the singleton EventNotifier instance."""
    global _notifier
    if _notifier is None:
        _notifier = EventNotifier()
    return _notifier
