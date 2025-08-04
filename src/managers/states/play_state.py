from .state import EngineState
from ..time.time_manager import Time

class PlayState(EngineState):

    def __init__(self, engine):
        super().__init__(engine)
        self.accumulator = 0.0

    def enter(self):
        print("Game started!")

    def exit(self):
        print("Exiting Play Mode")

    def update(self):
        self.accumulator += Time.deltaTime

        while self.accumulator >= Time.fixedDeltaTime:
            self.update_physics(Time.fixedDeltaTime)
            self.accumulator -= Time.fixedDeltaTime

        self.render()
    def render(self):
        # Game rendering
        pass
