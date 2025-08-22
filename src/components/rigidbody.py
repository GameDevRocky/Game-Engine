from .component import Component
import pymunk
import pygame
from ..core import Options
from ..managers.serialization.util import SerializeField


class RigidBody(Component):

    @SerializeField(default= 1, type_hint= float)
    def mass(self): pass

    @SerializeField(default= lambda : {}, type_hint= dict)
    def body_type(self): pass

    def __init__(self, gameobject, **kwargs):
        super().__init__(gameobject, **kwargs)
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
    def from_dict(cls, gameobject, **kwargs):
        return cls(gameobject, **kwargs)


    

        
