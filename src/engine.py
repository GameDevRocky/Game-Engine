from .managers import Time, StateManager, EditorState, PlayState
from PyQt6.QtCore import QTimer

class Engine:

    def __init__(self):
        self.running = True
        self.state_manager = StateManager()
        self.play_state = PlayState(self)
        self.editor_state = EditorState(self)
        self.editor = None


    def start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000 // 60)

        self.state_manager.set_state(self.editor_state)

    
    def update(self):
        Time.update()
        self.state_manager.update()
        