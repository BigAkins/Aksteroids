import math
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
    PLAYER_STARTING_BOMBS,
    WEAPON_NORMAL,
    WEAPON_SPREAD,
    WEAPON_RAPID,
    SPREAD_SHOT_ANGLE,
    NORMAL_WEAPON_COOLDOWN,
    NORMAL_WEAPON_SHOT_SPEED,
    SPREAD_WEAPON_COOLDOWN,
    SPREAD_WEAPON_SHOT_SPEED,
    RAPID_WEAPON_COOLDOWN,
    RAPID_WEAPON_SHOT_SPEED,
    SHIELD_INDICATOR_COLOR,
    SHIELD_INDICATOR_RADIUS_OFFSET,
    SHIELD_INDICATOR_LINE_WIDTH,
    SHIELD_INDICATOR_PULSE_SPEED,
    SHIELD_INDICATOR_PULSE_AMOUNT,
    SPEED_INDICATOR_COLOR,
    SPEED_INDICATOR_RADIUS_OFFSET,
    SPEED_INDICATOR_LINE_WIDTH,
    SPEED_INDICATOR_PULSE_SPEED,
    SPEED_INDICATOR_PULSE_AMOUNT,
)
import pygame
from asset_utils import load_image_with_aspect_ratio
from shot import Shot

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shot_cooldown = 0
        self.player_image = self.load_player_image()
        self.speed_powerup_timer = 0
        self.shield_active = False
        self.bombs = PLAYER_STARTING_BOMBS
        self.bomb_pressed_last_frame = False
        self.trigger_bomb = False
        self.current_weapon = WEAPON_NORMAL
        self.effect_animation_time = 0

    def load_player_image(self):
        if not USE_PLAYER_IMAGE:
            return None

        try:
            return load_image_with_aspect_ratio(
                PLAYER_IMAGE_PATH,
                PLAYER_IMAGE_WIDTH,
                PLAYER_IMAGE_HEIGHT,
            )
        except (pygame.error, FileNotFoundError):
            return None
   
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw_shield_indicator(self, screen):
        pulse = math.sin(self.effect_animation_time * SHIELD_INDICATOR_PULSE_SPEED)
        radius = self.radius + SHIELD_INDICATOR_RADIUS_OFFSET + pulse * SHIELD_INDICATOR_PULSE_AMOUNT

        pygame.draw.circle(
            screen,
            SHIELD_INDICATOR_COLOR,
            self.position,
            radius,
            SHIELD_INDICATOR_LINE_WIDTH,
        )

    def draw_speed_indicator(self, screen):
        pulse = math.sin(self.effect_animation_time * SPEED_INDICATOR_PULSE_SPEED)
        radius = self.radius + SPEED_INDICATOR_RADIUS_OFFSET + pulse * SPEED_INDICATOR_PULSE_AMOUNT

        pygame.draw.circle(
            screen,
            SPEED_INDICATOR_COLOR,
            self.position,
            radius,
            SPEED_INDICATOR_LINE_WIDTH,
        )

    def draw(self, screen):
        if self.shield_active:
            self.draw_shield_indicator(screen)

        if self.speed_powerup_timer > 0:
            self.draw_speed_indicator(screen)

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

    def activate_shield(self):
        self.shield_active = True

    def consume_shield(self):
        if not self.shield_active:
            return False

        self.shield_active = False
        return True

    def can_use_bomb(self):
        return self.bombs > 0

    def use_bomb(self):
        if not self.can_use_bomb():
            return False

        self.bombs -= 1
        return True

    def add_bomb(self, amount=1):
        self.bombs += amount

    def switch_weapon(self, weapon_name):
        self.current_weapon = weapon_name

    def get_weapon_name(self):
        return self.current_weapon

    def get_current_weapon_cooldown(self):
        if self.current_weapon == WEAPON_SPREAD:
            return SPREAD_WEAPON_COOLDOWN
        if self.current_weapon == WEAPON_RAPID:
            return RAPID_WEAPON_COOLDOWN
        return NORMAL_WEAPON_COOLDOWN

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

    def spawn_shot(self, angle_offset, shot_speed):
        shot = Shot(self.position.x, self.position.y)
        direction = pygame.Vector2(0, 1).rotate(self.rotation + angle_offset)
        shot.velocity = direction * shot_speed

    def shoot(self):
        if self.shot_cooldown > 0:
            return

        self.shot_cooldown = self.get_current_weapon_cooldown()

        if self.current_weapon == WEAPON_SPREAD:
            self.spawn_shot(-SPREAD_SHOT_ANGLE, SPREAD_WEAPON_SHOT_SPEED)
            self.spawn_shot(0, SPREAD_WEAPON_SHOT_SPEED)
            self.spawn_shot(SPREAD_SHOT_ANGLE, SPREAD_WEAPON_SHOT_SPEED)
            return

        if self.current_weapon == WEAPON_RAPID:
            self.spawn_shot(0, RAPID_WEAPON_SHOT_SPEED)
            return

        self.spawn_shot(0, NORMAL_WEAPON_SHOT_SPEED)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.effect_animation_time += dt

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

        if keys[pygame.K_1]:
            self.switch_weapon(WEAPON_NORMAL)
        if keys[pygame.K_2]:
            self.switch_weapon(WEAPON_SPREAD)
        if keys[pygame.K_3]:
            self.switch_weapon(WEAPON_RAPID)

        if keys[pygame.K_SPACE]:
            self.shoot()

        bomb_pressed = keys[pygame.K_b]
        self.trigger_bomb = False

        if bomb_pressed and not self.bomb_pressed_last_frame:
            self.trigger_bomb = self.use_bomb()

        self.bomb_pressed_last_frame = bomb_pressed
        
        self.apply_drag()
        self.move(dt)