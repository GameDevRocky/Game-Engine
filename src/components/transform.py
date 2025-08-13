from __future__ import annotations
import numpy as np
from pygame import Vector2
from .component import Component
from ..managers.serialization.util import SerializeField

class Transform(Component):
    
    def parent_setter(self, new_transform, keep_world=True):
        if new_transform is self:
            raise ValueError("Cannot set a Transform as its own parent.")
        if self.parent:
            if self in self.parent.children:
                self.parent.children.remove(self)
        self._parent = new_transform
        if new_transform:
            if self not in new_transform.children:
                new_transform.children.append(self)
        self.gameobject.notify()
    
    def parent_getter(self):
        return self._parent

    @SerializeField(type_hint=Vector2, default=lambda: Vector2(0, 0))
    def position(self): pass
    
    @SerializeField(type_hint=float, default=0.0)
    def angle(self): pass
    
    @SerializeField(type_hint=Vector2, default=lambda: Vector2(1, 1))
    def scale(self): pass    
    
    @SerializeField(type_hint='Transform', setter= parent_setter, getter= parent_getter)
    def parent(self): pass    

    @SerializeField(type_hint= list, default= lambda: [])
    def children(self):  pass
    
    def __init__(self, gameobject, **kwargs):
        super().__init__(gameobject, **kwargs)
        self._children = list(self.children)
        self._position = Vector2(self.position)
        self._scale = Vector2(self.scale)

    def to_dict(self):
        return {
            "position": [self.position.x, self.position.y],
            "angle": self.angle,
            "scale": [self.scale.x, self.scale.y]
        }

    @classmethod
    def from_dict(cls, gameobject, **kwargs):
        return cls(gameobject, **kwargs)
    
    def __repr__(self):
        return f"<Transform position={self.position} angle={self.angle} scale={self.scale}>"
