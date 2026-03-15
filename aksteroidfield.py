from typing import Any, ClassVar

import pygame
import random
from aksteroid import Aksteroid
from constants import *


class AksteroidField(pygame.sprite.Sprite):
    containers: ClassVar[tuple[pygame.sprite.AbstractGroup[Any], ...]] = ()

    edges = [
        [
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-AKSTEROID_MAX_RADIUS, y * SCREEN_HEIGHT),
        ],
        [
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                SCREEN_WIDTH + AKSTEROID_MAX_RADIUS, y * SCREEN_HEIGHT
            ),
        ],
        [
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, -AKSTEROID_MAX_RADIUS),
        ],
        [
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH, SCREEN_HEIGHT + AKSTEROID_MAX_RADIUS
            ),
        ],
    ]

    def __init__(self):
        super().__init__(*self.containers)
        self.spawn_timer = 0.0

    def spawn(self, radius, position, velocity):
        aksteroid = Aksteroid(position.x, position.y, radius)
        aksteroid.velocity = velocity

    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer > AKSTEROID_SPAWN_RATE_SECONDS:
            self.spawn_timer = 0

            # spawn a new aksteroid at a random edge
            edge = random.choice(self.edges)
            speed = random.randint(40, 100)
            velocity = edge[0] * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            position = edge[1](random.uniform(0, 1))
            kind = random.randint(1, AKSTEROID_KINDS)
            self.spawn(AKSTEROID_MIN_RADIUS * kind, position, velocity)
