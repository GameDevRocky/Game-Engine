
class Layer:
    count = 0
    def __init__(self, name: str):
        self.name = name
        self.collision_mask = Layer.count
        Layer.count += 1
