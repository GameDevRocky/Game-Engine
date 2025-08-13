from .component import Component
from ..core import Options
import pymunk
import pygame
from PyQt6.QtCore import QTimer


class Test_Component(Component):

    def __init__(self, gameobject, enabled=True):
        from ..components import Transform
        super().__init__(gameobject, enabled)
        self.transform = None
        self.x = 0
        self.y = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_transform)
        self.timer.start(1000 // 60)

    def set_transform(self):
        if self.transform:
            self.transform.position = pygame.Vector2(self.x, self.y)
            print(self.transform)

    @classmethod
    def from_dict(cls, data, gameobject):
        instance = cls(gameobject)
        instance.x = data.get('x', 0)
        instance.y = data.get('y', 0)
        return instance
    
    def update_transform(self):
        if self.transform:
            self.transform.set_local_position(self.x, self.y)
