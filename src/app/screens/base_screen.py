"""
Base Screen - Abstract base class for all screens (State Pattern).

Each screen represents a state in the application.
"""
from abc import ABC, abstractmethod
from PIL import Image
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.screens.screen_manager import ScreenManager


class BaseScreen(ABC):
    """Abstract base class for all display screens."""
    
    def __init__(self, name: str):
        self.name = name
        self._manager: "ScreenManager | None" = None
    
    def set_manager(self, manager: "ScreenManager") -> None:
        """Set the screen manager reference."""
        self._manager = manager
    
    @abstractmethod
    def render(self) -> Image.Image:
        """
        Render the screen content and return a PIL Image.
        
        Returns:
            PIL Image ready to display on e-ink screen.
        """
        pass
    
    @abstractmethod
    def get_data(self) -> dict:
        """
        Fetch and return data needed for this screen.
        
        Returns:
            Dictionary with screen-specific data.
        """
        pass
    
    def on_enter(self) -> None:
        """Called when this screen becomes active."""
        pass
    
    def on_exit(self) -> None:
        """Called when leaving this screen."""
        pass
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"
