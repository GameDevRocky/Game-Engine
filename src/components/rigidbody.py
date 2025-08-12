from .component import Component
import pymunk
import pygame
from ..core import Field
from ..core import Options

class RigidBody(Component):
    from ..core import GameObject
    def __init__(self, gameobject, enabled= True):
        super().__init__(gameobject, enabled)
        self.mass = Field(1.0, float)
        self.moment = Field(1.0, float)
        self.body_type = Field({"Static" : pymunk.Body.STATIC, "Kinematic" : pymunk.Body.KINEMATIC, "Dynamic": pymunk.Body.DYNAMIC}, Options)
        self.body = None
        self.read_fields()

    def awake(self):
        self.body = pymunk.Body(self.mass, self.moment, self.body_type['Dynamic'])
    
    def start(self):
        from . import Transform
        transform : Transform = self.gameobject.get_component("Transform")
        self.body.position = pymunk.Vec2d(*transform.position)
        self.body.angle = transform.angle
    
    def fixed_update(self):
        from . import Transform
        transform : Transform = self.gameobject.get_component("Transform")
        transform.position = pygame.Vector2(*self.body.position)
        transform.angle = self.body.angle

    @classmethod
    def from_dict(cls, data, gameobject):
        return cls(
            gameobject
        )
        
    



    

        
