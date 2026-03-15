from circleshape import CircleShape
import pygame
from constants import (
    SHOT_RADIUS,
    LINE_WIDTH,
    SHOT_IMAGE_PATH,
    USE_SHOT_IMAGE,
    SHOT_IMAGE_WIDTH,
    SHOT_IMAGE_HEIGHT,
    SHOT_FALLBACK_COLOR,
)
from asset_utils import load_image_with_aspect_ratio


class Shot(CircleShape):
    image_cache = None
    image_load_attempted = False

    def __init__(self, x, y):
        super().__init__(x, y, SHOT_RADIUS)

    @classmethod
    def load_shot_image(cls):
        if not USE_SHOT_IMAGE:
            return None

        if cls.image_load_attempted:
            return cls.image_cache

        cls.image_load_attempted = True

        try:
            cls.image_cache = load_image_with_aspect_ratio(
                SHOT_IMAGE_PATH,
                SHOT_IMAGE_WIDTH,
                SHOT_IMAGE_HEIGHT,
            )
            return cls.image_cache
        except (pygame.error, FileNotFoundError):
            cls.image_cache = None
            return None

    def draw(self, screen):
        shot_image = self.load_shot_image()

        if shot_image is not None:
            rotation = -self.velocity.angle_to(pygame.Vector2(0, -1))
            rotated_image = pygame.transform.rotate(shot_image, rotation)
            image_rect = rotated_image.get_rect(center=self.position)
            screen.blit(rotated_image, image_rect)
            return

        pygame.draw.circle(
            screen,
            SHOT_FALLBACK_COLOR,
            self.position,
            self.radius,
            LINE_WIDTH
        )

    def update(self, dt):
        self.position += self.velocity * dt
        self.wrap_position()