from circleshape import CircleShape
import pygame
import random
from logger import log_event
from constants import LINE_WIDTH, AKSTEROID_MIN_RADIUS

class Aksteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            "white",
            self.position,
            self.radius,
            LINE_WIDTH
        )

    def update(self, dt):
        self.position += self.velocity * dt
        self.wrap_position()

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
