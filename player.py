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
    PLAYER_IMAGE_PATH,
    USE_PLAYER_IMAGE,
    PLAYER_IMAGE_WIDTH,
    PLAYER_IMAGE_HEIGHT,
    SPEED_POWERUP_DURATION_SECONDS,
    SPEED_POWERUP_ACCELERATION_MULTIPLIER,
    SPEED_POWERUP_MAX_SPEED_MULTIPLIER,
)
import pygame
from shot import Shot

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_cooldown = 0
        self.player_image = self.load_player_image()
        self.speed_powerup_timer = 0

    def load_player_image(self):
        if not USE_PLAYER_IMAGE:
            return None

        try:
            player_image = pygame.image.load(PLAYER_IMAGE_PATH).convert_alpha()
            player_image = pygame.transform.smoothscale(
                player_image,
                (PLAYER_IMAGE_WIDTH, PLAYER_IMAGE_HEIGHT),
            )
            return player_image
        except (pygame.error, FileNotFoundError):
            return None
   
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen):
        if self.player_image is not None:
            rotated_image = pygame.transform.rotate(self.player_image, -self.rotation)
            image_rect = rotated_image.get_rect(center=self.position)
            screen.blit(rotated_image, image_rect)
            return

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

    def activate_speed_powerup(self):
        self.speed_powerup_timer = SPEED_POWERUP_DURATION_SECONDS

    def get_current_acceleration(self):
        if self.speed_powerup_timer > 0:
            return PLAYER_ACCELERATION * SPEED_POWERUP_ACCELERATION_MULTIPLIER
        return PLAYER_ACCELERATION

    def get_current_max_speed(self):
        if self.speed_powerup_timer > 0:
            return PLAYER_MAX_SPEED * SPEED_POWERUP_MAX_SPEED_MULTIPLIER
        return PLAYER_MAX_SPEED

    def accelerate(self, amount, dt):
        direction = pygame.Vector2(0, 1).rotate(self.rotation)
        self.velocity += direction * amount * dt

        current_max_speed = self.get_current_max_speed()
        if self.velocity.length() > current_max_speed:
            self.velocity.scale_to_length(current_max_speed)

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

        if self.speed_powerup_timer > 0:
            self.speed_powerup_timer -= dt
            if self.speed_powerup_timer < 0:
                self.speed_powerup_timer = 0

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.accelerate(self.get_current_acceleration(), dt)
        if keys[pygame.K_s]:
            self.accelerate(-PLAYER_REVERSE_ACCELERATION, dt)
        if keys[pygame.K_SPACE]:
            self.shoot()
        
        self.apply_drag()
        self.move(dt)