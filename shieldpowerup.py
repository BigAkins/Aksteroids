import pygame
from asset_utils import load_image_with_aspect_ratio

from circleshape import CircleShape
from constants import (
    SHIELD_POWERUP_RADIUS,
    SHIELD_POWERUP_COLOR,
    SHIELD_POWERUP_OUTLINE_WIDTH,
    SHIELD_POWERUP_IMAGE_PATH,
    USE_SHIELD_POWERUP_IMAGE,
    SHIELD_POWERUP_IMAGE_WIDTH,
    SHIELD_POWERUP_IMAGE_HEIGHT,
)


class ShieldPowerUp(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, SHIELD_POWERUP_RADIUS)
        self.image = self.load_image()

    def load_image(self):
        if not USE_SHIELD_POWERUP_IMAGE:
            return None

        try:
            return load_image_with_aspect_ratio(
                SHIELD_POWERUP_IMAGE_PATH,
                SHIELD_POWERUP_IMAGE_WIDTH,
                SHIELD_POWERUP_IMAGE_HEIGHT,
            )
        except (pygame.error, FileNotFoundError):
            return None

    def draw(self, screen):
        if self.image is not None:
            image_rect = self.image.get_rect(center=self.position)
            screen.blit(self.image, image_rect)
            return

        pygame.draw.circle(
            screen,
            SHIELD_POWERUP_COLOR,
            self.position,
            self.radius,
            SHIELD_POWERUP_OUTLINE_WIDTH,
        )

    def update(self, dt):
        pass
