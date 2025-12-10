"""
Tests for Screen Manager and Screen States.
"""
import pytest
from unittest.mock import MagicMock
from PIL import Image

from src.app.screens.base_screen import BaseScreen
from src.app.screens.screen_manager import ScreenManager


class MockScreen(BaseScreen):
    """Mock screen for testing."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.render_called = False
        self.get_data_called = False
        self.on_enter_called = False
        self.on_exit_called = False
    
    def render(self) -> Image.Image:
        self.render_called = True
        return Image.new("1", (100, 100), 1)
    
    def get_data(self) -> dict:
        self.get_data_called = True
        return {"test": "data"}
    
    def on_enter(self) -> None:
        self.on_enter_called = True
    
    def on_exit(self) -> None:
        self.on_exit_called = True


class TestScreenManager:
    """Tests for ScreenManager class."""
    
    def test_register_screen(self):
        """Test registering a screen."""
        manager = ScreenManager()
        screen = MockScreen("Test")
        
        manager.register_screen(screen)
        
        assert manager.screen_count == 1
        assert screen._manager == manager
    
    def test_register_multiple_screens(self):
        """Test registering multiple screens."""
        manager = ScreenManager()
        screens = [MockScreen(f"Screen {i}") for i in range(4)]
        
        manager.register_screens(screens)
        
        assert manager.screen_count == 4
    
    def test_current_screen_initial(self):
        """Test that current screen is first registered screen."""
        manager = ScreenManager()
        screen1 = MockScreen("Screen 1")
        screen2 = MockScreen("Screen 2")
        
        manager.register_screens([screen1, screen2])
        
        assert manager.current_screen == screen1
        assert manager.current_index == 0
    
    def test_next_screen_cycles(self):
        """Test that next_screen cycles through screens."""
        manager = ScreenManager()
        screens = [MockScreen(f"Screen {i}") for i in range(3)]
        manager.register_screens(screens)
        
        # Move through all screens
        assert manager.current_index == 0
        manager.next_screen()
        assert manager.current_index == 1
        manager.next_screen()
        assert manager.current_index == 2
        manager.next_screen()
        assert manager.current_index == 0  # Back to start
    
    def test_next_screen_calls_callbacks(self):
        """Test that next_screen calls on_exit and on_enter."""
        manager = ScreenManager()
        screen1 = MockScreen("Screen 1")
        screen2 = MockScreen("Screen 2")
        manager.register_screens([screen1, screen2])
        
        manager.next_screen()
        
        assert screen1.on_exit_called
        assert screen2.on_enter_called
    
    def test_previous_screen_cycles(self):
        """Test that previous_screen cycles backwards."""
        manager = ScreenManager()
        screens = [MockScreen(f"Screen {i}") for i in range(3)]
        manager.register_screens(screens)
        
        # Go backwards
        manager.previous_screen()
        assert manager.current_index == 2  # Wraps to end
        manager.previous_screen()
        assert manager.current_index == 1
    
    def test_go_to_screen(self):
        """Test going to a specific screen by index."""
        manager = ScreenManager()
        screens = [MockScreen(f"Screen {i}") for i in range(4)]
        manager.register_screens(screens)
        
        manager.go_to_screen(2)
        
        assert manager.current_index == 2
        assert manager.current_screen == screens[2]
    
    def test_go_to_screen_invalid_index(self):
        """Test that invalid index returns None."""
        manager = ScreenManager()
        screens = [MockScreen(f"Screen {i}") for i in range(2)]
        manager.register_screens(screens)
        
        result = manager.go_to_screen(5)
        
        assert result is None
        assert manager.current_index == 0  # Unchanged
    
    def test_render_current(self):
        """Test rendering current screen."""
        manager = ScreenManager()
        screen = MockScreen("Test")
        manager.register_screen(screen)
        
        image = manager.render_current()
        
        assert screen.render_called
        assert image is not None
        assert isinstance(image, Image.Image)
    
    def test_refresh_current(self):
        """Test refresh calls get_data and render."""
        manager = ScreenManager()
        screen = MockScreen("Test")
        manager.register_screen(screen)
        
        manager.refresh_current()
        
        assert screen.get_data_called
        assert screen.render_called
    
    def test_get_screen_by_name(self):
        """Test finding screen by name."""
        manager = ScreenManager()
        screen1 = MockScreen("First")
        screen2 = MockScreen("Second")
        manager.register_screens([screen1, screen2])
        
        found = manager.get_screen_by_name("Second")
        
        assert found == screen2
    
    def test_get_screen_by_name_not_found(self):
        """Test that missing screen returns None."""
        manager = ScreenManager()
        screen = MockScreen("Test")
        manager.register_screen(screen)
        
        found = manager.get_screen_by_name("NotExisting")
        
        assert found is None
    
    def test_initialize(self):
        """Test that initialize enters first screen."""
        manager = ScreenManager()
        screen = MockScreen("Test")
        manager.register_screen(screen)
        
        manager.initialize()
        
        assert screen.on_enter_called
    
    def test_empty_manager(self):
        """Test behavior with no screens."""
        manager = ScreenManager()
        
        assert manager.current_screen is None
        assert manager.screen_count == 0
        assert manager.next_screen() is None
        assert manager.render_current() is None


class TestBaseScreen:
    """Tests for BaseScreen abstract class."""
    
    def test_screen_name(self):
        """Test that screen has correct name."""
        screen = MockScreen("MyScreen")
        
        assert screen.name == "MyScreen"
    
    def test_screen_repr(self):
        """Test string representation."""
        screen = MockScreen("Test")
        
        assert "MockScreen" in repr(screen)
        assert "Test" in repr(screen)
    
    def test_set_manager(self):
        """Test setting manager reference."""
        screen = MockScreen("Test")
        manager = MagicMock()
        
        screen.set_manager(manager)
        
        assert screen._manager == manager
