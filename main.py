import pygame
import sys
from logger import log_state, log_event
from constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCORE_PER_AKSTEROID,
    SCORE_POSITION_X,
    SCORE_POSITION_Y,
    SCORE_FONT_SIZE,
    SCORE_COLOR,
    BACKGROUND_COLOR,
    BACKGROUND_IMAGE_PATH,
    USE_BACKGROUND_IMAGE,
    PLAYER_STARTING_LIVES,
    PLAYER_RESPAWN_INVULNERABILITY_SECONDS,
    LIVES_POSITION_X,
    LIVES_POSITION_Y,
    SPEED_POWERUP_SPAWN_X,
    SPEED_POWERUP_SPAWN_Y,
    SHIELD_POWERUP_SPAWN_X,
    SHIELD_POWERUP_SPAWN_Y,
)
from player import Player
from aksteroidfield import AksteroidField
from aksteroid import Aksteroid
from shot import Shot
from explosion import Explosion
from speedpowerup import SpeedPowerUp
from shieldpowerup import ShieldPowerUp

def draw_score(screen, font, score):
    score_surface = font.render(f"Score: {score}", True, SCORE_COLOR)
    screen.blit(score_surface, (SCORE_POSITION_X, SCORE_POSITION_Y))

def draw_lives(screen, font, lives):
    lives_surface = font.render(f"Lives: {lives}", True, SCORE_COLOR)
    screen.blit(lives_surface, (LIVES_POSITION_X, LIVES_POSITION_Y))

def load_background():
    if not USE_BACKGROUND_IMAGE:
        return None

    try:
        background = pygame.image.load(BACKGROUND_IMAGE_PATH).convert()
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        return background
    except (pygame.error, FileNotFoundError):
        return None


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    hud_font = pygame.font.Font(None, SCORE_FONT_SIZE)
    score = 0
    lives = PLAYER_STARTING_LIVES
    respawn_invulnerability_timer = 0
    background = load_background()
    dt = 0
    print(f"Starting Aksteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    aksteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    explosions = pygame.sprite.Group()
    speed_powerups = pygame.sprite.Group()
    shield_powerups = pygame.sprite.Group()
    AksteroidField.containers = (updatable,)
    Aksteroid.containers = (aksteroids, updatable, drawable)
    Shot.containers = (shots, updatable, drawable)
    Explosion.containers = (explosions, updatable, drawable)
    SpeedPowerUp.containers = (speed_powerups, updatable, drawable)
    ShieldPowerUp.containers = (shield_powerups, updatable, drawable)
    _aksteroid_field = AksteroidField()

    Player.containers = (updatable, drawable)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    SpeedPowerUp(SPEED_POWERUP_SPAWN_X, SPEED_POWERUP_SPAWN_Y)
    ShieldPowerUp(SHIELD_POWERUP_SPAWN_X, SHIELD_POWERUP_SPAWN_Y)

    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
       
        if background is not None:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BACKGROUND_COLOR)

        updatable.update(dt)

        for speed_powerup in speed_powerups:
            if speed_powerup.collides_with(player):
                player.activate_speed_powerup()
                speed_powerup.kill()
                break

        for shield_powerup in shield_powerups:
            if shield_powerup.collides_with(player):
                player.activate_shield()
                shield_powerup.kill()
                break

        if respawn_invulnerability_timer > 0:
            respawn_invulnerability_timer -= dt
            if respawn_invulnerability_timer < 0:
                respawn_invulnerability_timer = 0

        for aksteroid in aksteroids:
            if respawn_invulnerability_timer <= 0 and aksteroid.collides_with(player):
                if player.consume_shield():
                    aksteroid.split()
                    break

                log_event("player_hit")
                lives -= 1

                if lives <= 0:
                    print("Game over!")
                    sys.exit()

                player.reset()
                respawn_invulnerability_timer = PLAYER_RESPAWN_INVULNERABILITY_SECONDS
                break

        for aksteroid in aksteroids:
            for shot in shots:
                if aksteroid.collides_with(shot):
                    log_event("aksteroid_shot")
                    score += SCORE_PER_AKSTEROID

                    hit_position = aksteroid.position.copy()
                    hit_radius = aksteroid.radius
                    Explosion(hit_position.x, hit_position.y, hit_radius)

                    aksteroid.split()
                    shot.kill()
                    break

        for obj in drawable:
            obj.draw(screen)

        draw_score(screen, hud_font, score)

        draw_lives(screen, hud_font, lives)

        pygame.display.flip()
        dt = clock.tick(60) / 1000
      


if __name__ == "__main__":
    main()
