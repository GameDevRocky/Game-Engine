from abc import ABC, abstractmethod

class EngineState(ABC):
    def __init__(self, engine):
        self.engine = engine  # Reference to the main engine

    @abstractmethod
    def enter(self):
        """Called when this state becomes active."""
        pass

    @abstractmethod
    def exit(self):
        """Called when this state is no longer active."""
        pass

    @abstractmethod
    def update(self):
        """Update the game logic for this state."""
        pass

    @abstractmethod
    def render(self):
        """Render the state."""
        pass
