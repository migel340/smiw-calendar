"""
Tests for individual screen implementations.
"""
import pytest
from unittest.mock import MagicMock, patch
from PIL import Image


class TestEventsTodayScreen:
    """Tests for EventsTodayScreen."""
    
    @patch('src.app.screens.events_today_screen.get_epd')
    @patch('src.app.screens.events_today_screen.get_events_today')
    def test_get_data(self, mock_get_events, mock_get_epd):
        """Test fetching today's events."""
        from src.app.screens.events_today_screen import EventsTodayScreen
        
        mock_events = [
            {"title": "Meeting", "start": "10:00", "end": "11:00", "is_all_day": False},
        ]
        mock_get_events.return_value = mock_events
        
        screen = EventsTodayScreen()
        data = screen.get_data()
        
        assert data["events"] == mock_events
        mock_get_events.assert_called_once()
    
    @patch('src.app.screens.events_today_screen.get_epd')
    @patch('src.app.screens.events_today_screen.get_events_today')
    def test_get_events(self, mock_get_events, mock_get_epd):
        """Test get_events returns cached events."""
        from src.app.screens.events_today_screen import EventsTodayScreen
        
        mock_events = [{"title": "Test"}]
        mock_get_events.return_value = mock_events
        
        screen = EventsTodayScreen()
        screen.get_data()
        
        assert screen.get_events() == mock_events
    
    @patch('src.app.screens.events_today_screen.get_epd')
    def test_render_no_events(self, mock_get_epd):
        """Test rendering with no events."""
        from src.app.screens.events_today_screen import EventsTodayScreen
        
        mock_epd = MagicMock()
        mock_epd.width = 122
        mock_epd.height = 250
        mock_get_epd.return_value = mock_epd
        
        screen = EventsTodayScreen()
        screen._events = []
        
        image = screen.render()
        
        assert isinstance(image, Image.Image)
        assert image.size == (122, 250)
    
    @patch('src.app.screens.events_today_screen.get_epd')
    def test_render_with_events(self, mock_get_epd):
        """Test rendering with events."""
        from src.app.screens.events_today_screen import EventsTodayScreen
        
        mock_epd = MagicMock()
        mock_epd.width = 122
        mock_epd.height = 250
        mock_get_epd.return_value = mock_epd
        
        screen = EventsTodayScreen()
        screen._events = [
            {"title": "All Day Event", "start": None, "is_all_day": True},
            {"title": "Meeting", "start": "10:00", "end": "11:00", "is_all_day": False},
        ]
        
        image = screen.render()
        
        assert isinstance(image, Image.Image)


class TestEventsTomorrowScreen:
    """Tests for EventsTomorrowScreen."""
    
    @patch('src.app.screens.events_tomorrow_screen.get_epd')
    @patch('src.app.screens.events_tomorrow_screen.get_events_tomorrow')
    def test_get_data(self, mock_get_events, mock_get_epd):
        """Test fetching tomorrow's events."""
        from src.app.screens.events_tomorrow_screen import EventsTomorrowScreen
        
        mock_events = [{"title": "Tomorrow Meeting"}]
        mock_get_events.return_value = mock_events
        
        screen = EventsTomorrowScreen()
        data = screen.get_data()
        
        assert data["events"] == mock_events


class TestTasksScreen:
    """Tests for TasksScreen."""
    
    @patch('src.app.screens.tasks_screen.get_epd')
    @patch('src.app.screens.tasks_screen.get_structured_tasks')
    def test_get_data(self, mock_get_tasks, mock_get_epd):
        """Test fetching tasks."""
        from src.app.screens.tasks_screen import TasksScreen
        
        mock_tasks = [{"title": "Task 1", "due": "2025-12-10"}]
        mock_get_tasks.return_value = mock_tasks
        
        screen = TasksScreen()
        data = screen.get_data()
        
        assert data["tasks"] == mock_tasks
    
    @patch('src.app.screens.tasks_screen.get_epd')
    def test_render_with_tasks(self, mock_get_epd):
        """Test rendering with tasks."""
        from src.app.screens.tasks_screen import TasksScreen
        
        mock_epd = MagicMock()
        mock_epd.width = 122
        mock_epd.height = 250
        mock_get_epd.return_value = mock_epd
        
        screen = TasksScreen()
        screen._tasks = [
            {"title": "Task without due", "due": None},
            {"title": "Task with due", "due": "2025-12-10"},
        ]
        
        image = screen.render()
        
        assert isinstance(image, Image.Image)


class TestDHT11Screen:
    """Tests for DHT11Screen."""
    
    @patch('src.app.screens.dht11_screen.get_epd')
    @patch('src.app.screens.dht11_screen.get_dht11_reading')
    def test_get_data_success(self, mock_get_reading, mock_get_epd):
        """Test fetching DHT11 data."""
        from src.app.screens.dht11_screen import DHT11Screen
        from src.hardware.dht11_driver import DHTReading
        
        mock_reading = DHTReading(temperature=22.5, humidity=55.0)
        mock_get_reading.return_value = mock_reading
        
        screen = DHT11Screen()
        data = screen.get_data()
        
        assert data["temperature"] == 22.5
        assert data["humidity"] == 55.0
    
    @patch('src.app.screens.dht11_screen.get_epd')
    @patch('src.app.screens.dht11_screen.get_dht11_reading')
    def test_get_data_failure(self, mock_get_reading, mock_get_epd):
        """Test handling DHT11 read failure."""
        from src.app.screens.dht11_screen import DHT11Screen
        
        mock_get_reading.return_value = None
        
        screen = DHT11Screen()
        data = screen.get_data()
        
        assert data["temperature"] is None
        assert data["humidity"] is None
    
    @patch('src.app.screens.dht11_screen.get_epd')
    def test_render_no_reading(self, mock_get_epd):
        """Test rendering when sensor unavailable."""
        from src.app.screens.dht11_screen import DHT11Screen
        
        mock_epd = MagicMock()
        mock_epd.width = 122
        mock_epd.height = 250
        mock_get_epd.return_value = mock_epd
        
        screen = DHT11Screen()
        screen._reading = None
        
        image = screen.render()
        
        assert isinstance(image, Image.Image)
