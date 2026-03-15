from circleshape import CircleShape
import pygame
import random
from asset_utils import load_image_with_aspect_ratio
from logger import log_event
from constants import (
    LINE_WIDTH,
    AKSTEROID_MIN_RADIUS,
    USE_AKSTEROID_IMAGES,
    AKSTEROID_SMALL_IMAGE_PATH,
    AKSTEROID_MEDIUM_IMAGE_PATH,
    AKSTEROID_LARGE_IMAGE_PATH,
    AKSTEROID_IMAGE_OUTLINE_FALLBACK_COLOR,
    AKSTEROID_IMAGE_ROTATION_SPEED_MIN,
    AKSTEROID_IMAGE_ROTATION_SPEED_MAX,
)


class Aksteroid(CircleShape):
    image_cache = {}

    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.image_rotation = random.uniform(0, 360)
        self.image_rotation_speed = random.uniform(
            AKSTEROID_IMAGE_ROTATION_SPEED_MIN,
            AKSTEROID_IMAGE_ROTATION_SPEED_MAX,
        )
        if random.choice([True, False]):
            self.image_rotation_speed *= -1

    @classmethod
    def get_image_path_for_radius(cls, radius):
        if radius <= AKSTEROID_MIN_RADIUS:
            return AKSTEROID_SMALL_IMAGE_PATH
        if radius <= AKSTEROID_MIN_RADIUS * 2:
            return AKSTEROID_MEDIUM_IMAGE_PATH
        return AKSTEROID_LARGE_IMAGE_PATH

    @classmethod
    def load_image(cls, image_path, diameter):
        cache_key = (image_path, diameter)

        if cache_key in cls.image_cache:
            return cls.image_cache[cache_key]

        try:
            image = load_image_with_aspect_ratio(
                image_path,
                diameter,
                diameter,
            )
            cls.image_cache[cache_key] = image
            return image
        except (pygame.error, FileNotFoundError):
            cls.image_cache[cache_key] = None
            return None

    def get_image(self):
        if not USE_AKSTEROID_IMAGES:
            return None

        image_path = self.get_image_path_for_radius(self.radius)
        diameter = int(self.radius * 2)
        return self.load_image(image_path, diameter)

    def draw(self, screen):
        asteroid_image = self.get_image()

        if asteroid_image is not None:
            rotated_image = pygame.transform.rotate(
                asteroid_image,
                self.image_rotation,
            )
            image_rect = rotated_image.get_rect(center=self.position)
            screen.blit(rotated_image, image_rect)
            return

        pygame.draw.circle(
            screen,
            AKSTEROID_IMAGE_OUTLINE_FALLBACK_COLOR,
            self.position,
            self.radius,
            LINE_WIDTH,
        )

    def update(self, dt):
        self.position += self.velocity * dt
        self.wrap_position()
        self.image_rotation += self.image_rotation_speed * dt

    def split(self):
        self.kill()

        if self.radius <= AKSTEROID_MIN_RADIUS:
            return

        log_event("aksteroid_split")
        angle = random.uniform(20, 50)
        velocity1 = self.velocity.rotate(angle)
        velocity2 = self.velocity.rotate(-angle)
        new_radius = self.radius - AKSTEROID_MIN_RADIUS

        aksteroid1 = Aksteroid(self.position.x, self.position.y, new_radius)
        aksteroid2 = Aksteroid(self.position.x, self.position.y, new_radius)

        aksteroid1.velocity = velocity1 * 1.2
        aksteroid2.velocity = velocity2 * 1.2
