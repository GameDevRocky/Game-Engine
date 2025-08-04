import numpy as np
from pygame.math import Vector2
from .component import Component
from ..core import Field

class Transform(Component):
    def __init__(self, gameobject, position= [0,0], angle = 0, scale= [0, 0]):
        super().__init__(gameobject)

        # Local transform data
        self.local_position = Field(Vector2(position), Vector2)
        self.local_scale = Field(Vector2(scale), Vector2)
        self.local_angle = Field(angle, float)  # in degrees

        # World transform data
        self.world_position = Vector2(0, 0)
        self.world_scale = Vector2(1, 1)
        self.world_angle = 0.0

        # Parent transform (for hierarchy)
        self.parent = None
        self.children = set()

        # Transformation matrices
        self._local_matrix = np.identity(3)
        self._world_matrix = np.identity(3)
        self._dirty = True

    def to_dict(self):
        return {
            "position": [self.position.x, self.position.y],
            "rotation": self.angle,
            "scale": [self.scale.x, self.scale.y]
        }

    @classmethod
    def from_dict(cls, data, gameobject):
        position = data.get("position", [0, 0])
        scale = data.get("scale", [1, 1])
        return cls(
            gameobject,
            position=position,
            angle=data.get("rotation", 0),
            scale=scale
        )
    
    def set_parent(self, new_transform, keep_world=True):
        """Change the parent of this transform.
        
        Args:
            new_transform: The new parent transform, or None to unparent
            keep_world: If True, maintain world position/rotation/scale while changing parent
        """
        if new_transform is self:
            raise ValueError("Cannot set a Transform as its own parent.")

        # Remove from old parent's children
        if self.parent:
            self.parent.children.discard(self)

        # Store world transform if keeping it
        if keep_world:
            world_matrix = self.get_world_matrix()

        # Update parent reference
        self.parent = new_transform
        
        # Add to new parent's children if there is a new parent
        if new_transform:
            new_transform.children.add(self)

        # Update transform matrices
        if keep_world:
            if self.parent:
                # Calculate new local transform that maintains world transform
                parent_world_inv = np.linalg.inv(self.parent.get_world_matrix())
                self._local_matrix = parent_world_inv @ world_matrix
                
                # Extract local transform values
                self.local_position = Vector2(*self._local_matrix[:2, 2])
                self.local_scale = Vector2(
                    np.linalg.norm(self._local_matrix[0, :2]),
                    np.linalg.norm(self._local_matrix[1, :2])
                )
                self.local_angle = np.degrees(np.arctan2(self._local_matrix[0,1], self._local_matrix[0,0]))
            else:
                # When unparenting, local = world
                self._local_matrix = world_matrix.copy()
                self.local_position = Vector2(*world_matrix[:2, 2])
                self.local_scale = Vector2(
                    np.linalg.norm(world_matrix[0, :2]),
                    np.linalg.norm(world_matrix[1, :2])
                )
                self.local_angle = np.degrees(np.arctan2(world_matrix[0,1], world_matrix[0,0]))
        else:
            # Keep local transform as is, world will update on next access
            pass

        self._dirty = True

    def set_local_position(self, x, y):
        self.local_position.update(x, y)
        self._dirty = True

    def translate(self, dx, dy):
        self.local_position += Vector2(dx, dy)
        self._dirty = True

    def set_local_scale(self, sx, sy):
        self.local_scale.update(sx, sy)
        self._dirty = True

    def scale_by(self, sx, sy):
        self.local_scale.x *= sx
        self.local_scale.y *= sy
        self._dirty = True

    def set_local_angle(self, angle):
        self.local_angle = angle % 360
        self._dirty = True

    def rotate(self, delta_angle):
        self.local_angle = (self.local_angle + delta_angle) % 360
        self._dirty = True

    def _calculate_local_matrix(self):
        angle_rad = np.radians(self.local_angle)
        cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)

        S = np.array([
            [self.local_scale.x, 0, 0],
            [0, self.local_scale.y, 0],
            [0, 0, 1]
        ])

        R = np.array([
            [cos_a, -sin_a, 0],
            [sin_a,  cos_a, 0],
            [0,      0,     1]
        ])

        T = np.array([
            [1, 0, self.local_position.x],
            [0, 1, self.local_position.y],
            [0, 0, 1]
        ])

        self._local_matrix = T @ R @ S
        return self._local_matrix

    def _calculate_world_matrix(self):
        self._calculate_local_matrix()

        if self.parent:
            self._world_matrix = self.parent.get_world_matrix() @ self._local_matrix
        else:
            self._world_matrix = self._local_matrix.copy()

        self.world_position = Vector2(*self._world_matrix[:2, 2])
        self.world_scale = Vector2(
            np.linalg.norm(self._world_matrix[0, :2]),
            np.linalg.norm(self._world_matrix[1, :2])
        )
        self.world_angle = np.degrees(np.arctan2(self._world_matrix[0,1], self._world_matrix[0,0]))
        self._dirty = False

        return self._world_matrix

    def get_local_matrix(self):
        if self._dirty:
            self._calculate_local_matrix()
        return self._local_matrix

    def get_world_matrix(self):
        if self._dirty:
            self._calculate_world_matrix()
        return self._world_matrix

    def get_opengl_matrix(self):
        mat3 = self.get_world_matrix()
        mat4 = np.identity(4)
        mat4[0, :2] = mat3[0, :2]
        mat4[1, :2] = mat3[1, :2]
        mat4[3, :2] = mat3[2, :2]
        return mat4

    @property
    def forward(self):
        return Vector2(1, 0).rotate(-self.world_angle)

    @property
    def right(self):
        return Vector2(0, -1).rotate(-self.world_angle)

    @property
    def position(self):
        self.get_world_matrix()
        return self.world_position

    @position.setter
    def position(self, value):
        self.local_position = Vector2(value)
        self._dirty = True

    @property
    def scale(self):
        self.get_world_matrix()
        return self.world_scale

    @scale.setter
    def scale(self, value):
        self.local_scale = Vector2(value)
        self._dirty = True

    @property
    def angle(self):
        self.get_world_matrix()
        return self.world_angle

    @angle.setter
    def angle(self, value):
        self.local_angle = value % 360
        self._dirty = True

    def __repr__(self):
        return f"<Transform position={self.position} angle={self.angle} scale={self.scale}>"