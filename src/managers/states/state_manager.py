from . import EngineState

class StateManager:    
    def __init__(self):
        self.current_state: EngineState = None

    def set_state(self, new_state: EngineState):
        if self.current_state:
            self.current_state.exit()
        self.current_state = new_state
        self.current_state.enter()

    def update(self):
        if self.current_state:
            self.current_state.update()

    def render(self):
        if self.current_state:
            self.current_state.render()

    def get_state(self):
        return self.current_state
