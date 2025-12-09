"""
Screen Manager - manages screen states and transitions (State Pattern Controller).

This class implements the State Pattern to manage multiple screens
with button-based navigation between them.
"""
from typing import List, Optional
from PIL import Image
import logging

from src.app.screens.base_screen import BaseScreen

logger = logging.getLogger(__name__)


class ScreenManager:
    """
    Manages screen states and transitions.
    
    Implements State Pattern where each screen is a state,
    and the manager controls transitions between states.
    """
    
    def __init__(self):
        self._screens: List[BaseScreen] = []
        self._current_index: int = 0
    
    def register_screen(self, screen: BaseScreen) -> None:
        """
        Register a new screen with the manager.
        
        Args:
            screen: Screen instance to register.
        """
        screen.set_manager(self)
        self._screens.append(screen)
        logger.info("Registered screen: %s (total: %d)", screen.name, len(self._screens))
    
    def register_screens(self, screens: List[BaseScreen]) -> None:
        """
        Register multiple screens at once.
        
        Args:
            screens: List of screen instances to register.
        """
        for screen in screens:
            self.register_screen(screen)
    
    @property
    def current_screen(self) -> Optional[BaseScreen]:
        """Get the currently active screen."""
        if not self._screens:
            return None
        return self._screens[self._current_index]
    
    @property
    def current_index(self) -> int:
        """Get current screen index."""
        return self._current_index
    
    @property
    def screen_count(self) -> int:
        """Get total number of registered screens."""
        return len(self._screens)
    
    def next_screen(self) -> Optional[BaseScreen]:
        """
        Switch to the next screen (circular navigation).
        
        Returns:
            The new current screen.
        """
        if not self._screens:
            return None
        
        # Exit current screen
        current = self.current_screen
        if current:
            current.on_exit()
        
        # Move to next screen
        self._current_index = (self._current_index + 1) % len(self._screens)
        
        # Enter new screen
        new_screen = self.current_screen
        if new_screen:
            new_screen.on_enter()
            logger.info("Switched to screen: %s (%d/%d)", 
                       new_screen.name, self._current_index + 1, len(self._screens))
        
        return new_screen
    
    def previous_screen(self) -> Optional[BaseScreen]:
        """
        Switch to the previous screen (circular navigation).
        
        Returns:
            The new current screen.
        """
        if not self._screens:
            return None
        
        # Exit current screen
        current = self.current_screen
        if current:
            current.on_exit()
        
        # Move to previous screen
        self._current_index = (self._current_index - 1) % len(self._screens)
        
        # Enter new screen
        new_screen = self.current_screen
        if new_screen:
            new_screen.on_enter()
            logger.info("Switched to screen: %s (%d/%d)", 
                       new_screen.name, self._current_index + 1, len(self._screens))
        
        return new_screen
    
    def go_to_screen(self, index: int) -> Optional[BaseScreen]:
        """
        Switch to a specific screen by index.
        
        Args:
            index: Screen index to switch to.
            
        Returns:
            The new current screen, or None if index is invalid.
        """
        if not self._screens or index < 0 or index >= len(self._screens):
            logger.warning("Invalid screen index: %d", index)
            return None
        
        # Exit current screen
        current = self.current_screen
        if current:
            current.on_exit()
        
        # Switch to target screen
        self._current_index = index
        
        # Enter new screen
        new_screen = self.current_screen
        if new_screen:
            new_screen.on_enter()
            logger.info("Switched to screen: %s (%d/%d)", 
                       new_screen.name, self._current_index + 1, len(self._screens))
        
        return new_screen
    
    def render_current(self) -> Optional[Image.Image]:
        """
        Render the current screen.
        
        Returns:
            PIL Image of the current screen, or None if no screens.
        """
        screen = self.current_screen
        if screen is None:
            logger.warning("No screen to render")
            return None
        
        try:
            return screen.render()
        except Exception as e:
            logger.exception("Error rendering screen %s: %s", screen.name, e)
            return None
    
    def refresh_current(self) -> Optional[Image.Image]:
        """
        Refresh data and render the current screen.
        
        Returns:
            PIL Image of the current screen, or None if no screens.
        """
        screen = self.current_screen
        if screen is None:
            return None
        
        try:
            screen.get_data()
            return screen.render()
        except Exception as e:
            logger.exception("Error refreshing screen %s: %s", screen.name, e)
            return None
    
    def get_screen_by_name(self, name: str) -> Optional[BaseScreen]:
        """
        Find a screen by its name.
        
        Args:
            name: Name of the screen to find.
            
        Returns:
            The screen if found, None otherwise.
        """
        for screen in self._screens:
            if screen.name == name:
                return screen
        return None
    
    def initialize(self) -> None:
        """Initialize the screen manager and enter the first screen."""
        if self._screens:
            self._screens[0].on_enter()
            logger.info("Initialized with screen: %s", self._screens[0].name)
