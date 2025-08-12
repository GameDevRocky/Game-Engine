from .component import Component
from ..core import Field
from ..core import Options
import pymunk
import pygame
from PyQt6.QtCore import QTimer


class Test_Component(Component):

    def __init__(self, gameobject, enabled=True):
        from ..components import Transform
        super().__init__(gameobject, enabled)
        self.transform: Field[Transform] = Field(None, Transform) 
        self.x = Field(0, float) 
        self.y = Field(0, float) 
        self.x.subscribe(self.set_transform)
        self.y.subscribe(self.set_transform)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_transform)
        self.timer.start(1000 // 60)
        self.read_fields()

    def set_transform(self):
        if self.transform.value:
            self.transform.value.position = pygame.Vector2(self.x.value, self.y.value)
            print(self.transform.value)

    @classmethod
    def from_dict(cls, data, gameobject):
        instance = cls(gameobject)
        instance.x.value = data.get('x', 0)
        instance.y.value = data.get('y', 0)
        return instance
    
    def update_transform(self):
        if self.transform:
            self.transform.value.translate(0.05,0.05)
