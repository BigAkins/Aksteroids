import math
import random
import pygame

from asset_utils import load_image_with_aspect_ratio
from circleshape import CircleShape
from constants import (
    BOMB_POWERUP_RADIUS,
    BOMB_POWERUP_COLOR,
    BOMB_POWERUP_OUTLINE_WIDTH,
    BOMB_POWERUP_IMAGE_PATH,
    USE_BOMB_POWERUP_IMAGE,
    BOMB_POWERUP_IMAGE_WIDTH,
    BOMB_POWERUP_IMAGE_HEIGHT,
    BOMB_POWERUP_GLOW_COLOR,
    BOMB_POWERUP_GLOW_ALPHA,
    BOMB_POWERUP_GLOW_RADIUS_OFFSET,
    BOMB_POWERUP_GLOW_PULSE_SPEED,
    BOMB_POWERUP_GLOW_PULSE_AMOUNT,
    POWERUP_DRIFT_SPEED_MIN,
    POWERUP_DRIFT_SPEED_MAX,
)


class BombPowerUp(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, BOMB_POWERUP_RADIUS)
        self.image = self.load_image()
        self.animation_time = 0

        angle = random.uniform(0, 360)
        drift_speed = random.uniform(
            POWERUP_DRIFT_SPEED_MIN,
            POWERUP_DRIFT_SPEED_MAX,
        )
        self.velocity = pygame.Vector2(1, 0).rotate(angle) * drift_speed

    def load_image(self):
        if not USE_BOMB_POWERUP_IMAGE:
            return None

        try:
            return load_image_with_aspect_ratio(
                BOMB_POWERUP_IMAGE_PATH,
                BOMB_POWERUP_IMAGE_WIDTH,
                BOMB_POWERUP_IMAGE_HEIGHT,
            )
        except (pygame.error, FileNotFoundError):
            return None

    def draw_glow(self, screen):
        pulse = math.sin(self.animation_time * BOMB_POWERUP_GLOW_PULSE_SPEED)
        glow_radius = self.radius + BOMB_POWERUP_GLOW_RADIUS_OFFSET + pulse * BOMB_POWERUP_GLOW_PULSE_AMOUNT

        glow_size = int(glow_radius * 2 + 20)
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)

        glow_center = glow_size // 2
        pygame.draw.circle(
            glow_surface,
            (*BOMB_POWERUP_GLOW_COLOR, BOMB_POWERUP_GLOW_ALPHA),
            (glow_center, glow_center),
            int(glow_radius),
        )

        glow_rect = glow_surface.get_rect(center=self.position)
        screen.blit(glow_surface, glow_rect)

    def draw(self, screen):
        self.draw_glow(screen)

        if self.image is not None:
            image_rect = self.image.get_rect(center=self.position)
            screen.blit(self.image, image_rect)
            return

        pygame.draw.circle(
            screen,
            BOMB_POWERUP_COLOR,
            self.position,
            self.radius,
            BOMB_POWERUP_OUTLINE_WIDTH,
        )

    def update(self, dt):
        self.animation_time += dt
        self.position += self.velocity * dt
        self.wrap_position()