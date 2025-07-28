from .component import Component
from ..core import Field
from ..core import Options
import pymunk


class Collider(Component):

    def __init__(self, gameobject):
        super().__init__(gameobject)
        self.offset = Field((0.0, 0.0), tuple)  
        self.density = Field(1.0, float)       
        self.friction = Field(0.5, float)
        self.elasticity = Field(0.0, float)
        self.sensor = Field(False, bool)        
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
    def __init__(self, gameobject):
        super().__init__(gameobject)
        self.width = Field(1.0, float)
        self.height = Field(1.0, float)

    def create_shape(self, body):
        from . import Transform
        transform : Transform = self.gameobject.get_component(Transform)
        shape = pymunk.Poly.create_box(body, [self.width * transform.scale.x, self.height * transform.scale.y], 0.1)
        self.shape = shape
        return shape
    
class CircleCollider(Collider):
    def __init__(self, gameobject):
        super().__init__(gameobject)
        self.radius = Field(1.0, float)
        

    def create_shape(self, body):
        from . import Transform
        transform : Transform = self.gameobject.get_component(Transform)
        scale = max(transform.scale.x, transform.scale.y)
        shape = pymunk.Circle(body, self.radius * scale, self.offset)
        self.shape = shape
        return shape