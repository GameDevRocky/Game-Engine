from .component import Component
from ..core import Options
import pymunk
import pygame
from PyQt6.QtCore import QTimer
from ..managers.serialization.util import SerializeField
from ..components import Transform, RigidBody


class Test_Component(Component):

    @SerializeField(default= 0,type_hint= float)
    def x(self): pass

    @SerializeField(default= 0,type_hint= float)
    def y(self): pass

    @SerializeField(default= None, editor_hint= Transform, type_hint= Transform)
    def transform(self) -> Transform: pass

    def __init__(self, gameobject, **kwargs):
        super().__init__(gameobject, **kwargs)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_transform)
        self.timer.start(1000 // 60)

    def set_transform(self):
        if self.transform:
            self.transform.position = pygame.Vector2(self.x, self.y)

    @classmethod
    def from_dict(cls, gameobject, **kwargs):
        return cls(gameobject, **kwargs)
    
    def update_transform(self):
        if self.enabled:
            if self.transform:
                self.transform.position = pygame.Vector2(self.x, self.y)
