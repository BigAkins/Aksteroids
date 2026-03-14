import pygame

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
            image = pygame.image.load(SHIELD_POWERUP_IMAGE_PATH).convert_alpha()
            image = pygame.transform.smoothscale(
                image,
                (SHIELD_POWERUP_IMAGE_WIDTH, SHIELD_POWERUP_IMAGE_HEIGHT),
            )
            return image
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
