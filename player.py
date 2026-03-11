from circleshape import CircleShape
from constants import (
    PLAYER_RADIUS,
    LINE_WIDTH,
    PLAYER_TURN_SPEED,
    PLAYER_SHOOT_SPEED,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_ACCELERATION,
    PLAYER_MAX_SPEED,
    PLAYER_DRAG,
    PLAYER_REVERSE_ACCELERATION,
    PLAYER_MIN_VELOCITY,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
import pygame
from shot import Shot

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_cooldown = 0
   
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen):
        pygame.draw.polygon(
            screen,
            "white",
            self.triangle(),
            LINE_WIDTH
        )

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def reset(self):
        self.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.shot_cooldown = 0

    
    def accelerate(self, amount, dt):
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        self.velocity += direction * amount * dt

        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity.scale_to_length(PLAYER_MAX_SPEED)

    def move(self, dt):
        self.position += self.velocity * dt
        self.wrap_position()

    def apply_drag(self):
        self.velocity *= PLAYER_DRAG

        if self.velocity.length() < PLAYER_MIN_VELOCITY:
            self.velocity = pygame.Vector2(0, 0)

    def shoot(self):
        if self.shot_cooldown > 0:
            return

        self.shot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS

        shot = Shot(self.position.x, self.position.y)
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        shot.velocity = direction * PLAYER_SHOOT_SPEED

    def update(self, dt):
        keys = pygame.key.get_pressed()

        self.shot_cooldown -= dt
        if self.shot_cooldown < 0:
            self.shot_cooldown = 0

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.accelerate(PLAYER_ACCELERATION, dt)
        if keys[pygame.K_s]:
            self.accelerate(-PLAYER_REVERSE_ACCELERATION, dt)
        if keys[pygame.K_SPACE]:
            self.shoot()
        
        self.apply_drag()
        self.move(dt)