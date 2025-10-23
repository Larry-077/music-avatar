"""
Bone System for 2D Avatar Animation
====================================
This implements a hierarchical bone structure where each bone's transform
is relative to its parent, enabling natural character animation.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Tuple
import pygame


@dataclass
class Transform:
    """Represents a 2D transformation (position, rotation, scale)"""
    position: Tuple[float, float] = (0, 0)  # (x, y) offset from parent
    rotation: float = 0  # degrees
    scale: Tuple[float, float] = (1.0, 1.0)  # (sx, sy) scale factors
    
    def to_matrix(self) -> np.ndarray:
        """Convert transform to 3x3 transformation matrix"""
        # Translation matrix
        T = np.array([
            [1, 0, self.position[0]],
            [0, 1, self.position[1]],
            [0, 0, 1]
        ])
        
        # Rotation matrix (in radians)
        angle = np.radians(self.rotation)
        c, s = np.cos(angle), np.sin(angle)
        R = np.array([
            [c, -s, 0],
            [s, c, 0],
            [0, 0, 1]
        ])
        
        # Scale matrix
        S = np.array([
            [self.scale[0], 0, 0],
            [0, self.scale[1], 0],
            [0, 0, 1]
        ])
        
        # Combine: Scale -> Rotate -> Translate
        return T @ R @ S


class Bone:
    """
    A bone in the skeletal hierarchy.
    Each bone can have:
    - A local transform (relative to parent)
    - A sprite/image to render
    - Child bones
    """
    
    def __init__(
        self,
        name: str,
        local_transform: Optional[Transform] = None,
        sprite: Optional[pygame.Surface] = None,
        anchor_point: Tuple[float, float] = (0.5, 0.5),  # Pivot point (0-1 normalized)
    ):
        self.name = name
        self.local_transform = local_transform or Transform()
        self.sprite = sprite
        self.anchor_point = anchor_point
        
        self.parent: Optional[Bone] = None
        self.children: List[Bone] = []
        
        # Cached world transform (updated each frame)
        self._world_matrix: Optional[np.ndarray] = None
        self._world_position: Optional[Tuple[float, float]] = None
    
    def add_child(self, child: 'Bone'):
        """Add a child bone to this bone"""
        child.parent = self
        self.children.append(child)
    
    def get_world_matrix(self) -> np.ndarray:
        """Calculate world transformation matrix (relative to root)"""
        if self.parent is None:
            return self.local_transform.to_matrix()
        else:
            return self.parent.get_world_matrix() @ self.local_transform.to_matrix()
    
    def get_world_position(self) -> Tuple[float, float]:
        """Get the world-space position of this bone"""
        world_mat = self.get_world_matrix()
        return (world_mat[0, 2], world_mat[1, 2])
    
    def set_position(self, x: float, y: float):
        """Set local position relative to parent"""
        self.local_transform.position = (x, y)
    
    def set_rotation(self, angle: float):
        """Set local rotation in degrees"""
        self.local_transform.rotation = angle
    
    def set_scale(self, sx: float, sy: float = None):
        """Set local scale"""
        if sy is None:
            sy = sx
        self.local_transform.scale = (sx, sy)
    
    def update(self):
        """Update cached world transforms (call this once per frame on root)"""
        self._world_matrix = self.get_world_matrix()
        self._world_position = self.get_world_position()
        
        for child in self.children:
            child.update()
    
    def draw(self, screen: pygame.Surface, debug=False):
        """
        Draw this bone and all children recursively.
        
        Args:
            screen: Pygame surface to draw on
            debug: If True, draw bone connections and pivot points
        """
        if self.sprite is not None:
            # Get world position
            world_pos = self.get_world_position()
            
            # Apply rotation and scale
            world_mat = self.get_world_matrix()
            
            # Extract rotation angle from matrix
            rotation_rad = np.arctan2(world_mat[1, 0], world_mat[0, 0])
            rotation_deg = -np.degrees(rotation_rad)  # Negative for pygame
            
            # Extract scale
            scale_x = np.sqrt(world_mat[0, 0]**2 + world_mat[1, 0]**2)
            scale_y = np.sqrt(world_mat[0, 1]**2 + world_mat[1, 1]**2)
            
            # Transform sprite
            scaled_sprite = pygame.transform.scale(
                self.sprite,
                (int(self.sprite.get_width() * scale_x),
                 int(self.sprite.get_height() * scale_y))
            )
            rotated_sprite = pygame.transform.rotate(scaled_sprite, rotation_deg)
            
            # Calculate anchor offset
            anchor_x = rotated_sprite.get_width() * self.anchor_point[0]
            anchor_y = rotated_sprite.get_height() * self.anchor_point[1]
            
            # Draw sprite
            screen.blit(
                rotated_sprite,
                (world_pos[0] - anchor_x, world_pos[1] - anchor_y)
            )
        
        # Debug visualization
        if debug:
            world_pos = self.get_world_position()
            # Draw pivot point
            pygame.draw.circle(screen, (255, 0, 0), (int(world_pos[0]), int(world_pos[1])), 5)
            
            # Draw bone connection to parent
            if self.parent is not None:
                parent_pos = self.parent.get_world_position()
                pygame.draw.line(
                    screen,
                    (0, 255, 0),
                    (int(parent_pos[0]), int(parent_pos[1])),
                    (int(world_pos[0]), int(world_pos[1])),
                    2
                )
            
            # Draw bone name
            font = pygame.font.Font(None, 20)
            text = font.render(self.name, True, (255, 255, 255))
            screen.blit(text, (world_pos[0] + 10, world_pos[1] - 10))
        
        # Draw children
        for child in self.children:
            child.draw(screen, debug)
    
    def find_bone(self, name: str) -> Optional['Bone']:
        """Find a bone by name in the hierarchy"""
        if self.name == name:
            return self
        for child in self.children:
            result = child.find_bone(name)
            if result:
                return result
        return None
    
    def __repr__(self):
        return f"Bone('{self.name}', children={len(self.children)})"


# --- Helper class for managing sprite variants ---

class SpriteVariant:
    """
    Manages multiple variants of a sprite (e.g., different eye directions,
    mouth shapes, hand poses)
    """
    
    def __init__(self, variants: dict[str, pygame.Surface], default: str = None):
        """
        Args:
            variants: Dictionary mapping variant names to sprites
            default: Name of default variant (uses first if None)
        """
        self.variants = variants
        self.default = default or list(variants.keys())[0]
        self.current = self.default
    
    def set_variant(self, name: str) -> bool:
        """
        Set current variant by name.
        Returns True if variant exists, False otherwise.
        """
        if name in self.variants:
            self.current = name
            return True
        return False
    
    def get_sprite(self) -> pygame.Surface:
        """Get the current variant sprite"""
        return self.variants[self.current]
    
    def reset(self):
        """Reset to default variant"""
        self.current = self.default


if __name__ == "__main__":
    # Example usage and testing
    print("Bone system module loaded successfully!")
    print("\nExample bone hierarchy:")
    
    # Create simple hierarchy
    root = Bone("Root", Transform(position=(400, 300)))
    body = Bone("Body", Transform(position=(0, 0)))
    head = Bone("Head", Transform(position=(0, -100)))
    
    root.add_child(body)
    body.add_child(head)
    
    # Print hierarchy
    def print_hierarchy(bone, indent=0):
        print("  " * indent + f"- {bone.name}")
        for child in bone.children:
            print_hierarchy(child, indent + 1)
    
    print_hierarchy(root)
