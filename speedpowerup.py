import pygame
from asset_utils import load_image_with_aspect_ratio

from circleshape import CircleShape
from constants import (
    SPEED_POWERUP_RADIUS,
    SPEED_POWERUP_COLOR,
    SPEED_POWERUP_OUTLINE_WIDTH,
    SPEED_POWERUP_IMAGE_PATH,
    USE_SPEED_POWERUP_IMAGE,
    SPEED_POWERUP_IMAGE_WIDTH,
    SPEED_POWERUP_IMAGE_HEIGHT,
)


class SpeedPowerUp(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, SPEED_POWERUP_RADIUS)
        self.image = self.load_image()

    def load_image(self):
        if not USE_SPEED_POWERUP_IMAGE:
            return None

        try:
            return load_image_with_aspect_ratio(
                SPEED_POWERUP_IMAGE_PATH,
                SPEED_POWERUP_IMAGE_WIDTH,
                SPEED_POWERUP_IMAGE_HEIGHT,
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
            SPEED_POWERUP_COLOR,
            self.position,
            self.radius,
            SPEED_POWERUP_OUTLINE_WIDTH,
        )

    def update(self, dt):
        pass