import math
import random
import pygame

from constants import (
    EXPLOSION_PARTICLE_COUNT,
    EXPLOSION_PARTICLE_MIN_SPEED,
    EXPLOSION_PARTICLE_MAX_SPEED,
    EXPLOSION_DURATION_SECONDS,
    EXPLOSION_PARTICLE_RADIUS,
    EXPLOSION_PARTICLE_OUTLINE_WIDTH,
    EXPLOSION_COLOR,
    EXPLOSION_RADIUS_MULTIPLIER,
)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, source_radius):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.source_radius = source_radius
        self.timer = EXPLOSION_DURATION_SECONDS
        self.duration = EXPLOSION_DURATION_SECONDS
        self.particles = []

        explosion_radius = source_radius * EXPLOSION_RADIUS_MULTIPLIER

        for _ in range(EXPLOSION_PARTICLE_COUNT):
            angle = random.uniform(0, 360)
            direction = pygame.Vector2(1, 0).rotate(angle)
            speed = random.uniform(
                EXPLOSION_PARTICLE_MIN_SPEED,
                EXPLOSION_PARTICLE_MAX_SPEED,
            )

            self.particles.append(
                {
                    "position": self.position.copy(),
                    "velocity": direction * speed,
                    "distance_limit": random.uniform(
                        explosion_radius * 0.5,
                        explosion_radius,
                    ),
                    "distance_traveled": 0,
                }
            )

    def update(self, dt):
        self.timer -= dt

        if self.timer <= 0:
            self.kill()
            return

        for particle in self.particles:
            movement = particle["velocity"] * dt
            particle["position"] += movement
            particle["distance_traveled"] += movement.length()

            if particle["distance_traveled"] >= particle["distance_limit"]:
                particle["velocity"] = pygame.Vector2(0, 0)

    def draw(self, screen):
        life_ratio = self.timer / self.duration
        particle_radius = max(1, int(EXPLOSION_PARTICLE_RADIUS * life_ratio))

        for particle in self.particles:
            pygame.draw.circle(
                screen,
                EXPLOSION_COLOR,
                particle["position"],
                particle_radius,
                EXPLOSION_PARTICLE_OUTLINE_WIDTH,
            )