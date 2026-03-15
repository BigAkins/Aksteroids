from typing import Any, ClassVar

import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    containers: ClassVar[tuple[pygame.sprite.AbstractGroup[Any], ...]] = ()

    position: pygame.Vector2
    velocity: pygame.Vector2
    radius: float

    def __init__(self, x: float, y: float, radius: float):
        super().__init__(*self.containers)

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen):
        # must override
        pass

    def update(self, dt):
        # must override
        pass

    def collides_with(self, other):
        distance = self.position.distance_to(other.position)
        return distance <= (self.radius + other.radius)

    def wrap_position(self):
        if self.position.x < -self.radius:
            self.position.x = SCREEN_WIDTH + self.radius
        elif self.position.x > SCREEN_WIDTH + self.radius:
            self.position.x = -self.radius

        if self.position.y < -self.radius:
            self.position.y = SCREEN_HEIGHT + self.radius
        elif self.position.y > SCREEN_HEIGHT + self.radius:
            self.position.y = -self.radius
