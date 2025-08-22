from .component import Component
from ..core import Options
import pymunk


class Collider(Component):

    def __init__(self, gameobject, **kwargs):
        super().__init__(gameobject, **kwargs)
        self.offset = (0.0, 0.0)
        self.density = 1 
        self.friction = 0
        self.elasticity = 0
        self.sensor = False
        self.shape = None

    def create_shape(self, body):
        raise NotImplementedError

    def start(self):
        from . import RigidBody
        rigidbody : RigidBody = self.gameobject.get_component(RigidBody)
        if rigidbody:
            body = rigidbody.body
            self.create_shape(body)
        else:
            self.create_shape(None)
        
class BoxCollider(Collider):
    def __init__(self, gameobject, **kwargs):
        super().__init__(gameobject, **kwargs)
        self.width = 1.0
        self.height = 1.0

    def create_shape(self, body):
        from . import Transform
        transform : Transform = self.gameobject.get_component(Transform)
        shape = pymunk.Poly.create_box(body, [self.width * transform.scale.x, self.height * transform.scale.y], 0.1)
        self.shape = shape
        return shape
    
    @classmethod
    def from_dict(cls, gameobject, **kwargs):
        return cls(gameobject, **kwargs)
    

    
class CircleCollider(Collider):
    def __init__(self, gameobject, **kwargs):
        super().__init__(gameobject, **kwargs)
        self.radius = 1.0

    def create_shape(self, body):
        from . import Transform
        transform : Transform = self.gameobject.get_component(Transform)
        scale = max(transform.scale.x, transform.scale.y)
        shape = pymunk.Circle(body, self.radius * scale, self.offset)
        self.shape = shape
        return shape

    @classmethod
    def from_dict(cls, gameobject, **kwargs):
        return cls(gameobject, **kwargs)
