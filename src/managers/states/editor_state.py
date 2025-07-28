from .state import EngineState

class EditorState(EngineState):
    def enter(self):
        print("Entered Editor Mode")

    def exit(self):
        print("Exiting Editor Mode")

    def update(self):
        # Editor-specific logic
        pass

    def render(self):
        # Draw editor UI
        pass

