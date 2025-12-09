"""
Tests for Event Notifier (Observer Pattern).
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from zoneinfo import ZoneInfo

from src.app.event_notifier import EventNotifier


class TestEventNotifier:
    """Tests for EventNotifier class."""
    
    @pytest.fixture
    def notifier(self):
        """Create a fresh notifier for each test."""
        with patch('src.app.event_notifier.TIMEZONE', 'UTC'):
            notifier = EventNotifier(minutes_before=10)
            yield notifier
            notifier.stop()
    
    def test_update_events(self, notifier):
        """Test updating events filters out all-day events."""
        events = [
            {"title": "Meeting", "start": "10:00", "is_all_day": False},
            {"title": "Holiday", "start": None, "is_all_day": True},
            {"title": "Call", "start": "14:30", "is_all_day": False},
        ]
        
        notifier.update_events(events)
        
        # Should only have timed events
        assert len(notifier._events) == 2
    
    def test_parse_event_time_hhmm(self, notifier):
        """Test parsing HH:MM format."""
        result = notifier._parse_event_time("14:30")
        
        assert result is not None
        assert result.hour == 14
        assert result.minute == 30
    
    def test_parse_event_time_full_datetime(self, notifier):
        """Test parsing full datetime format."""
        result = notifier._parse_event_time("2025-12-09 15:00")
        
        assert result is not None
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 9
        assert result.hour == 15
    
    def test_parse_event_time_invalid(self, notifier):
        """Test that invalid time returns None."""
        result = notifier._parse_event_time("invalid")
        
        assert result is None
    
    def test_parse_event_time_empty(self, notifier):
        """Test that empty string returns None."""
        result = notifier._parse_event_time("")
        
        assert result is None
    
    @patch('src.app.event_notifier.datetime')
    def test_check_notifications_within_window(self, mock_datetime, notifier):
        """Test that event within window triggers notification."""
        tz = ZoneInfo('UTC')
        now = datetime(2025, 12, 9, 9, 55, tzinfo=tz)  # 5 min before 10:00
        mock_datetime.now.return_value = now
        mock_datetime.fromisoformat = datetime.fromisoformat
        
        notifier._tz = tz
        notifier._events = [
            {"title": "Meeting", "start": "10:00", "is_all_day": False},
        ]
        
        # Manually parse and check (since we're mocking datetime)
        with patch.object(notifier, '_parse_event_time') as mock_parse:
            mock_parse.return_value = datetime(2025, 12, 9, 10, 0, tzinfo=tz)
            
            result = notifier.check_notifications()
            
            assert result is not None
            assert result["title"] == "Meeting"
    
    @patch('src.app.event_notifier.datetime')
    def test_check_notifications_outside_window(self, mock_datetime, notifier):
        """Test that event outside window doesn't trigger."""
        tz = ZoneInfo('UTC')
        now = datetime(2025, 12, 9, 8, 0, tzinfo=tz)  # 2 hours before 10:00
        mock_datetime.now.return_value = now
        
        notifier._tz = tz
        notifier._events = [
            {"title": "Meeting", "start": "10:00", "is_all_day": False},
        ]
        
        with patch.object(notifier, '_parse_event_time') as mock_parse:
            mock_parse.return_value = datetime(2025, 12, 9, 10, 0, tzinfo=tz)
            
            result = notifier.check_notifications()
            
            assert result is None
    
    @patch('src.app.event_notifier.led_driver')
    def test_notify_turns_on_led(self, mock_led, notifier):
        """Test that notification turns on LED."""
        event = {"title": "Meeting"}
        
        notifier._notify(event)
        
        mock_led.turn_on.assert_called_once()
        assert notifier._led_on is True
    
    @patch('src.app.event_notifier.led_driver')
    def test_notify_only_once(self, mock_led, notifier):
        """Test that LED is only turned on once."""
        event = {"title": "Meeting"}
        
        notifier._notify(event)
        notifier._notify(event)  # Second call
        
        # Should only be called once
        mock_led.turn_on.assert_called_once()
    
    @patch('src.app.event_notifier.led_driver')
    def test_clear_notification(self, mock_led, notifier):
        """Test clearing notification turns off LED."""
        notifier._led_on = True
        
        notifier._clear_notification()
        
        mock_led.turn_off.assert_called_once()
        assert notifier._led_on is False
    
    def test_notification_callback(self, notifier):
        """Test that callbacks are called on notification."""
        callback = MagicMock()
        notifier.add_notification_callback(callback)
        
        event = {"title": "Test Event"}
        with patch('src.app.event_notifier.led_driver'):
            notifier._notify(event)
        
        callback.assert_called_once_with(event)
    
    def test_start_stop(self, notifier):
        """Test starting and stopping notifier."""
        assert not notifier.is_running()
        
        notifier.start()
        assert notifier.is_running()
        
        notifier.stop()
        assert not notifier.is_running()
    
    @patch('src.app.event_notifier.led_driver')
    def test_force_led_on(self, mock_led, notifier):
        """Test manually turning on LED."""
        notifier.force_led_on()
        
        mock_led.turn_on.assert_called_once()
        assert notifier._led_on is True
    
    @patch('src.app.event_notifier.led_driver')
    def test_force_led_off(self, mock_led, notifier):
        """Test manually turning off LED."""
        notifier.force_led_off()
        
        mock_led.turn_off.assert_called_once()
        assert notifier._led_on is False
