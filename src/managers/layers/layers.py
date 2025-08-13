from ...managers.serialization import Serializable, SerializeField

class Layer(Serializable):
    count = 0

    @SerializeField(default= 0, type_hint= int)
    def collision_mask(self): pass

    @SerializeField(default= lambda : f"Layer {Layer.count}", type_hint= str)
    def name(self): pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.collision_mask = Layer.count
        Layer.count += 1
