import pygame
from asset_utils import load_image_with_aspect_ratio
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
    BOMB_SCORE_PER_AKSTEROID,
    BOMBS_POSITION_X,
    BOMBS_POSITION_Y,
    BOMB_HUD_IMAGE_PATH,
    USE_BOMB_HUD_IMAGE,
    BOMB_HUD_IMAGE_WIDTH,
    BOMB_HUD_IMAGE_HEIGHT,
    BOMB_HUD_IMAGE_SPACING,
    WEAPON_POSITION_X,
    WEAPON_POSITION_Y,
    USE_WEAPON_ICONS,
    WEAPON_ICON_WIDTH,
    WEAPON_ICON_HEIGHT,
    WEAPON_ICON_SPACING,
    WEAPON_NORMAL,
    WEAPON_SPREAD,
    WEAPON_RAPID,
    WEAPON_NORMAL_ICON_PATH,
    WEAPON_SPREAD_ICON_PATH,
    WEAPON_RAPID_ICON_PATH,
    GAME_STATE_START,
    GAME_STATE_PLAYING,
    GAME_STATE_GAME_OVER,
    SCREEN_TITLE_FONT_SIZE,
    SCREEN_SUBTITLE_FONT_SIZE,
    SCREEN_TEXT_COLOR,
    SCREEN_OVERLAY_COLOR,
    SCREEN_TITLE_Y,
    SCREEN_SUBTITLE_Y,
    SCREEN_INSTRUCTION_Y,
    SCREEN_SECONDARY_INSTRUCTION_Y,
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


def load_weapon_icon(icon_path):
    try:
        return load_image_with_aspect_ratio(
            icon_path,
            WEAPON_ICON_WIDTH,
            WEAPON_ICON_HEIGHT,
        )
    except (pygame.error, FileNotFoundError):
        return None


def load_weapon_icons():
    if not USE_WEAPON_ICONS:
        return {}

    return {
        WEAPON_NORMAL: load_weapon_icon(WEAPON_NORMAL_ICON_PATH),
        WEAPON_SPREAD: load_weapon_icon(WEAPON_SPREAD_ICON_PATH),
        WEAPON_RAPID: load_weapon_icon(WEAPON_RAPID_ICON_PATH),
    }


def draw_weapon(screen, font, player, weapon_icons):
    weapon_name = player.get_weapon_name()
    weapon_surface = font.render(f"Weapon: {weapon_name}", True, SCORE_COLOR)
    screen.blit(weapon_surface, (WEAPON_POSITION_X, WEAPON_POSITION_Y))

    weapon_icon = weapon_icons.get(weapon_name)
    if weapon_icon is None:
        return

    icon_x = WEAPON_POSITION_X + weapon_surface.get_width() + WEAPON_ICON_SPACING
    icon_y = WEAPON_POSITION_Y + (weapon_surface.get_height() - weapon_icon.get_height()) / 2
    screen.blit(weapon_icon, (icon_x, icon_y))


def load_bomb_hud_image():
    if not USE_BOMB_HUD_IMAGE:
        return None

    try:
        return load_image_with_aspect_ratio(
            BOMB_HUD_IMAGE_PATH,
            BOMB_HUD_IMAGE_WIDTH,
            BOMB_HUD_IMAGE_HEIGHT,
        )
    except (pygame.error, FileNotFoundError):
        return None


def draw_bombs(screen, font, bombs, bomb_image):
    bombs_surface = font.render(f"Bombs: {bombs}", True, SCORE_COLOR)
    screen.blit(bombs_surface, (BOMBS_POSITION_X, BOMBS_POSITION_Y))

    if bomb_image is None:
        return

    text_width = bombs_surface.get_width()
    image_x = BOMBS_POSITION_X + text_width + BOMB_HUD_IMAGE_SPACING
    image_y = BOMBS_POSITION_Y + (bombs_surface.get_height() - bomb_image.get_height()) / 2

    for bomb_index in range(bombs):
        screen.blit(
            bomb_image,
            (
                image_x + bomb_index * (bomb_image.get_width() + BOMB_HUD_IMAGE_SPACING),
                image_y,
            ),
        )


def load_background():
    if not USE_BACKGROUND_IMAGE:
        return None

    try:
        background = pygame.image.load(BACKGROUND_IMAGE_PATH).convert()
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        return background
    except (pygame.error, FileNotFoundError):
        return None


def draw_centered_text(screen, font, text, y, color):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, y))
    screen.blit(text_surface, text_rect)


def draw_overlay(screen):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(SCREEN_OVERLAY_COLOR)
    screen.blit(overlay, (0, 0))


def draw_start_screen(screen, title_font, subtitle_font):
    draw_overlay(screen)
    draw_centered_text(screen, title_font, "AKSTEROIDS", SCREEN_TITLE_Y, SCREEN_TEXT_COLOR)
    draw_centered_text(
        screen,
        subtitle_font,
        "Press ENTER to Start",
        SCREEN_SUBTITLE_Y,
        SCREEN_TEXT_COLOR,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "Press Q to Quit",
        SCREEN_INSTRUCTION_Y,
        SCREEN_TEXT_COLOR,
    )


def draw_game_over_screen(screen, title_font, subtitle_font, score):
    draw_overlay(screen)
    draw_centered_text(screen, title_font, "GAME OVER", SCREEN_TITLE_Y, SCREEN_TEXT_COLOR)
    draw_centered_text(
        screen,
        subtitle_font,
        f"Final Score: {score}",
        SCREEN_SUBTITLE_Y,
        SCREEN_TEXT_COLOR,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "Press R to Restart",
        SCREEN_INSTRUCTION_Y,
        SCREEN_TEXT_COLOR,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "Press Q to Quit",
        SCREEN_SECONDARY_INSTRUCTION_Y,
        SCREEN_TEXT_COLOR,
    )


def reset_game(
    updatable,
    drawable,
    aksteroids,
    shots,
    explosions,
    speed_powerups,
    shield_powerups,
):
    updatable.empty()
    drawable.empty()
    aksteroids.empty()
    shots.empty()
    explosions.empty()
    speed_powerups.empty()
    shield_powerups.empty()

    AksteroidField.containers = (updatable,)
    Aksteroid.containers = (aksteroids, updatable, drawable)
    Shot.containers = (shots, updatable, drawable)
    Explosion.containers = (explosions, updatable, drawable)
    SpeedPowerUp.containers = (speed_powerups, updatable, drawable)
    ShieldPowerUp.containers = (shield_powerups, updatable, drawable)
    Player.containers = (updatable, drawable)

    _aksteroid_field = AksteroidField()
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    SpeedPowerUp(SPEED_POWERUP_SPAWN_X, SPEED_POWERUP_SPAWN_Y)
    ShieldPowerUp(SHIELD_POWERUP_SPAWN_X, SHIELD_POWERUP_SPAWN_Y)

    score = 0
    lives = PLAYER_STARTING_LIVES
    respawn_invulnerability_timer = 0

    return player, score, lives, respawn_invulnerability_timer


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    hud_font = pygame.font.Font(None, SCORE_FONT_SIZE)
    title_font = pygame.font.Font(None, SCREEN_TITLE_FONT_SIZE)
    subtitle_font = pygame.font.Font(None, SCREEN_SUBTITLE_FONT_SIZE)
    bomb_hud_image = load_bomb_hud_image()
    weapon_icons = load_weapon_icons()
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

    game_state = GAME_STATE_START
    player, score, lives, respawn_invulnerability_timer = reset_game(
        updatable,
        drawable,
        aksteroids,
        shots,
        explosions,
        speed_powerups,
        shield_powerups,
    )

    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if game_state == GAME_STATE_START:
                    if event.key == pygame.K_RETURN:
                        player, score, lives, respawn_invulnerability_timer = reset_game(
                            updatable,
                            drawable,
                            aksteroids,
                            shots,
                            explosions,
                            speed_powerups,
                            shield_powerups,
                        )
                        game_state = GAME_STATE_PLAYING
                    elif event.key == pygame.K_q:
                        return

                elif game_state == GAME_STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        player, score, lives, respawn_invulnerability_timer = reset_game(
                            updatable,
                            drawable,
                            aksteroids,
                            shots,
                            explosions,
                            speed_powerups,
                            shield_powerups,
                        )
                        game_state = GAME_STATE_PLAYING
                    elif event.key == pygame.K_q:
                        return

        if background is not None:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BACKGROUND_COLOR)

        if game_state == GAME_STATE_START:
            draw_start_screen(screen, title_font, subtitle_font)
            pygame.display.flip()
            dt = clock.tick(60) / 1000
            continue

        if game_state != GAME_STATE_PLAYING:
            draw_game_over_screen(screen, title_font, subtitle_font, score)
            pygame.display.flip()
            dt = clock.tick(60) / 1000
            continue

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

        if player.trigger_bomb:
            aksteroids_to_bomb = list(aksteroids)

            for aksteroid in aksteroids_to_bomb:
                hit_position = aksteroid.position.copy()
                hit_radius = aksteroid.radius

                Explosion(hit_position.x, hit_position.y, hit_radius)
                score += BOMB_SCORE_PER_AKSTEROID
                aksteroid.split()

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
                    game_state = GAME_STATE_GAME_OVER
                    break

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
        draw_bombs(screen, hud_font, player.bombs, bomb_hud_image)
        draw_weapon(screen, hud_font, player, weapon_icons)

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
