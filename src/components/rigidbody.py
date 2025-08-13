from .component import Component
import pymunk
import pygame
from ..core import Options

class RigidBody(Component):
    def __init__(self, gameobject, enabled= True):
        super().__init__(gameobject, enabled)
        self.mass = 1
        self.moment = 1
        self.body_type = {"Static" : pymunk.Body.STATIC, "Kinematic" : pymunk.Body.KINEMATIC, "Dynamic": pymunk.Body.DYNAMIC}
        self.body = None

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
        
    



    

        
