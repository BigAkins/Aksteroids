import sys
from pathlib import Path

import pygame
from audio_manager import AudioManager
import random
from asset_utils import load_image_with_aspect_ratio, resource_path
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
    # SPEED_POWERUP_SPAWN_X,
    # SPEED_POWERUP_SPAWN_Y,
    # SHIELD_POWERUP_SPAWN_X,
    # SHIELD_POWERUP_SPAWN_Y,
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
    GAME_STATE_PAUSED,
    GAME_STATE_GAME_OVER,
    GAME_STATE_INSTRUCTIONS,
    SCREEN_TITLE_FONT_SIZE,
    SCREEN_SUBTITLE_FONT_SIZE,
    SCREEN_TEXT_COLOR,
    SCREEN_OVERLAY_COLOR,
    SCREEN_TITLE_Y,
    SCREEN_SUBTITLE_Y,
    SCREEN_INSTRUCTION_Y,
    SCREEN_SECONDARY_INSTRUCTION_Y,
    PAUSE_SCREEN_SUBTITLE_Y,
    PAUSE_SCREEN_INSTRUCTION_Y,
    PAUSE_SCREEN_SECONDARY_INSTRUCTION_Y,
    SCREEN_THIRD_INSTRUCTION_Y,
    TITLE_IMAGE_PATH,
    USE_TITLE_IMAGE,
    TITLE_IMAGE_WIDTH,
    TITLE_IMAGE_HEIGHT,
    GAME_OVER_IMAGE_PATH,
    USE_GAME_OVER_IMAGE,
    GAME_OVER_IMAGE_WIDTH,
    GAME_OVER_IMAGE_HEIGHT,
    HIGH_SCORE_FILE_PATH,
    MENU_MUSIC_PATH,
    GAMEPLAY_MUSIC_PATH,
    SOUND_SHOOT_PATH,
    SOUND_EXPLOSION_PATH,
    SOUND_POWERUP_PICKUP_PATH,
    SOUND_BOMB_PATH,
    SOUND_PLAYER_HIT_PATH,
    SOUND_MENU_START_PATH,
    SOUND_GAME_OVER_PATH,
    START_SCREEN_HIGH_SCORE_Y,
    GAME_OVER_HIGH_SCORE_Y,
    INSTRUCTIONS_TITLE_Y,
    INSTRUCTIONS_LINE_1_Y,
    INSTRUCTIONS_LINE_2_Y,
    INSTRUCTIONS_LINE_3_Y,
    INSTRUCTIONS_LINE_4_Y,
    INSTRUCTIONS_LINE_5_Y,
    INSTRUCTIONS_LINE_6_Y,
    INSTRUCTIONS_RETURN_Y,
    BOMB_POWERUP_SPAWN_INTERVAL_MIN_SECONDS,
    BOMB_POWERUP_SPAWN_INTERVAL_MAX_SECONDS,
    BOMB_POWERUP_MAX_ACTIVE,
    TOTAL_BOMB_PICKUPS_AVAILABLE,
    SCREEN_SHAKE_ENABLED,
    SCREEN_SHAKE_BOMB_DURATION,
    SCREEN_SHAKE_BOMB_INTENSITY,
    SCREEN_SHAKE_EXPLOSION_DURATION,
    SCREEN_SHAKE_EXPLOSION_INTENSITY,
    SCREEN_SHAKE_PLAYER_HIT_DURATION,
    SCREEN_SHAKE_PLAYER_HIT_INTENSITY,
)

from player import Player
from aksteroidfield import AksteroidField
from aksteroid import Aksteroid
from shot import Shot
from explosion import Explosion
from speedpowerup import SpeedPowerUp
from shieldpowerup import ShieldPowerUp
from bombpowerup import BombPowerUp

# --- Outlined text constants and helpers ---
TEXT_OUTLINE_COLOR = (10, 10, 25)
TEXT_OUTLINE_THICKNESS = 3

# --- Power-up spawn configuration ---
POWERUP_SPAWN_INTERVAL_MIN_SECONDS = 6.0
POWERUP_SPAWN_INTERVAL_MAX_SECONDS = 12.0
POWERUP_MAX_ACTIVE = 3
POWERUP_SPAWN_MARGIN = 120
POWERUP_SPEED_WEIGHT = 0.5
POWERUP_SHIELD_WEIGHT = 0.5


def create_game_font(size):
    font_names = ["arialblack", "impact", "bahnschrift", "arial"]
    for font_name in font_names:
        matched_font = pygame.font.match_font(font_name)
        if matched_font is not None:
            return pygame.font.Font(matched_font, size)

    return pygame.font.Font(None, size)


def render_outlined_text(font, text, text_color, outline_color, outline_thickness):
    base_surface = font.render(text, True, text_color)
    width = base_surface.get_width() + outline_thickness * 2
    height = base_surface.get_height() + outline_thickness * 2

    outlined_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    for offset_x in range(-outline_thickness, outline_thickness + 1):
        for offset_y in range(-outline_thickness, outline_thickness + 1):
            if offset_x == 0 and offset_y == 0:
                continue

            outline_surface = font.render(text, True, outline_color)
            outlined_surface.blit(
                outline_surface,
                (offset_x + outline_thickness, offset_y + outline_thickness),
            )

    outlined_surface.blit(base_surface, (outline_thickness, outline_thickness))
    return outlined_surface


def draw_score(screen, font, score, offset_x: float = 0, offset_y: float = 0):
    score_surface = render_outlined_text(
        font,
        f"Score: {score}",
        SCORE_COLOR,
        TEXT_OUTLINE_COLOR,
        TEXT_OUTLINE_THICKNESS,
    )
    screen.blit(score_surface, (SCORE_POSITION_X + offset_x, SCORE_POSITION_Y + offset_y))


def draw_lives(screen, font, lives, offset_x: float = 0, offset_y: float = 0):
    lives_surface = render_outlined_text(
        font,
        f"Lives: {lives}",
        SCORE_COLOR,
        TEXT_OUTLINE_COLOR,
        TEXT_OUTLINE_THICKNESS,
    )
    screen.blit(lives_surface, (LIVES_POSITION_X + offset_x, LIVES_POSITION_Y + offset_y))


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


def draw_weapon(screen, font, player, weapon_icons, offset_x: float = 0, offset_y: float = 0):
    weapon_name = player.get_weapon_name()
    weapon_surface = render_outlined_text(
        font,
        f"Weapon: {weapon_name}",
        SCORE_COLOR,
        TEXT_OUTLINE_COLOR,
        TEXT_OUTLINE_THICKNESS,
    )
    screen.blit(weapon_surface, (WEAPON_POSITION_X + offset_x, WEAPON_POSITION_Y + offset_y))

    weapon_icon = weapon_icons.get(weapon_name)
    if weapon_icon is None:
        return

    icon_x = WEAPON_POSITION_X + offset_x + weapon_surface.get_width() + WEAPON_ICON_SPACING
    icon_y = WEAPON_POSITION_Y + offset_y + (weapon_surface.get_height() - weapon_icon.get_height()) / 2
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


def draw_bombs(screen, font, bombs, bomb_image, offset_x: float = 0, offset_y: float = 0):
    bombs_surface = render_outlined_text(
        font,
        f"Bombs: {bombs}",
        SCORE_COLOR,
        TEXT_OUTLINE_COLOR,
        TEXT_OUTLINE_THICKNESS,
    )
    screen.blit(bombs_surface, (BOMBS_POSITION_X + offset_x, BOMBS_POSITION_Y + offset_y))

    if bomb_image is None:
        return

    text_width = bombs_surface.get_width()
    image_x = BOMBS_POSITION_X + offset_x + text_width + BOMB_HUD_IMAGE_SPACING
    image_y = BOMBS_POSITION_Y + offset_y + (bombs_surface.get_height() - bomb_image.get_height()) / 2

    for bomb_index in range(bombs):
        screen.blit(
            bomb_image,
            (
                image_x + bomb_index * (bomb_image.get_width() + BOMB_HUD_IMAGE_SPACING),
                image_y,
            ),
        )




def get_user_data_path(filename: str) -> Path:
    if sys.platform == "darwin":
        base_dir = Path.home() / "Library" / "Application Support" / "Aksteroids"
    elif sys.platform == "win32":
        base_dir = Path.home() / "AppData" / "Roaming" / "Aksteroids"
    else:
        base_dir = Path.home() / ".local" / "share" / "Aksteroids"

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / filename


def load_background():
    if not USE_BACKGROUND_IMAGE:
        return None

    try:
        background = pygame.image.load(resource_path(BACKGROUND_IMAGE_PATH)).convert()
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        return background
    except (pygame.error, FileNotFoundError):
        return None


def load_screen_image(image_path, use_image, max_width, max_height):
    if not use_image:
        return None

    try:
        return load_image_with_aspect_ratio(
            image_path,
            max_width,
            max_height,
        )
    except (pygame.error, FileNotFoundError):
        return None


def load_high_score():
    high_score_path = get_user_data_path(HIGH_SCORE_FILE_PATH)
    try:
        with open(high_score_path, "r", encoding="utf-8") as high_score_file:
            return int(high_score_file.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(high_score):
    high_score_path = get_user_data_path(HIGH_SCORE_FILE_PATH)
    with open(high_score_path, "w", encoding="utf-8") as high_score_file:
        high_score_file.write(str(high_score))


# --- Power-up spawn helpers ---

def get_next_powerup_spawn_time():
    return random.uniform(
        POWERUP_SPAWN_INTERVAL_MIN_SECONDS,
        POWERUP_SPAWN_INTERVAL_MAX_SECONDS,
    )


def count_active_powerups(speed_powerups, shield_powerups):
    return len(speed_powerups) + len(shield_powerups)


def spawn_random_powerup(speed_powerups, shield_powerups):
    if count_active_powerups(speed_powerups, shield_powerups) >= POWERUP_MAX_ACTIVE:
        return

    spawn_x = random.uniform(
        POWERUP_SPAWN_MARGIN,
        SCREEN_WIDTH - POWERUP_SPAWN_MARGIN,
    )
    spawn_y = random.uniform(
        POWERUP_SPAWN_MARGIN,
        SCREEN_HEIGHT - POWERUP_SPAWN_MARGIN,
    )

    powerup_type = random.choices(
        ["speed", "shield"],
        weights=[POWERUP_SPEED_WEIGHT, POWERUP_SHIELD_WEIGHT],
        k=1,
    )[0]

    if powerup_type == "speed":
        SpeedPowerUp(spawn_x, spawn_y)
    else:
        ShieldPowerUp(spawn_x, spawn_y)


def get_next_bomb_powerup_spawn_time():
    return random.uniform(
        BOMB_POWERUP_SPAWN_INTERVAL_MIN_SECONDS,
        BOMB_POWERUP_SPAWN_INTERVAL_MAX_SECONDS,
    )


def spawn_bomb_powerup(bomb_powerups):
    if len(bomb_powerups) >= BOMB_POWERUP_MAX_ACTIVE:
        return

    spawn_x = random.uniform(
        POWERUP_SPAWN_MARGIN,
        SCREEN_WIDTH - POWERUP_SPAWN_MARGIN,
    )
    spawn_y = random.uniform(
        POWERUP_SPAWN_MARGIN,
        SCREEN_HEIGHT - POWERUP_SPAWN_MARGIN,
    )

    BombPowerUp(spawn_x, spawn_y)


def draw_centered_text(screen, font, text, y, color, offset_x: float = 0, offset_y: float = 0):
    text_surface = render_outlined_text(
        font,
        text,
        color,
        TEXT_OUTLINE_COLOR,
        TEXT_OUTLINE_THICKNESS,
    )
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2 + offset_x, y + offset_y))
    screen.blit(text_surface, text_rect)


def draw_overlay(screen):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(SCREEN_OVERLAY_COLOR)
    screen.blit(overlay, (0, 0))


def draw_start_screen(screen, title_font, subtitle_font, title_image, high_score, offset_x: float = 0, offset_y: float = 0):
    draw_overlay(screen)

    if title_image is not None:
        title_rect = title_image.get_rect(center=(SCREEN_WIDTH / 2 + offset_x, SCREEN_TITLE_Y + offset_y))
        screen.blit(title_image, title_rect)
    else:
        draw_centered_text(screen, title_font, "AKSTEROID", SCREEN_TITLE_Y, SCREEN_TEXT_COLOR, offset_x, offset_y)

    draw_centered_text(
        screen,
        subtitle_font,
        "Press ENTER to Start",
        SCREEN_SUBTITLE_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "Press I for Instructions",
        SCREEN_INSTRUCTION_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "Press Q to Quit",
        SCREEN_SECONDARY_INSTRUCTION_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        f"High Score: {high_score}",
        START_SCREEN_HIGH_SCORE_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )


def draw_game_over_screen(screen, title_font, subtitle_font, score, high_score, game_over_image, offset_x: float = 0, offset_y: float = 0):
    draw_overlay(screen)

    if game_over_image is not None:
        game_over_rect = game_over_image.get_rect(center=(SCREEN_WIDTH / 2 + offset_x, SCREEN_TITLE_Y + offset_y))
        screen.blit(game_over_image, game_over_rect)
    else:
        draw_centered_text(screen, title_font, "GAME OVER", SCREEN_TITLE_Y, SCREEN_TEXT_COLOR, offset_x, offset_y)

    draw_centered_text(
        screen,
        subtitle_font,
        f"Final Score: {score}",
        SCREEN_SUBTITLE_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "Press R to Restart",
        SCREEN_INSTRUCTION_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "Press I for Instructions",
        SCREEN_SECONDARY_INSTRUCTION_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "Press Q to Quit",
        SCREEN_THIRD_INSTRUCTION_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        f"High Score: {high_score}",
        GAME_OVER_HIGH_SCORE_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )


def draw_pause_screen(screen, title_image, title_font, subtitle_font, offset_x: float = 0, offset_y: float = 0):
    draw_overlay(screen)

    if title_image is not None:
        title_rect = title_image.get_rect(center=(SCREEN_WIDTH / 2 + offset_x, SCREEN_TITLE_Y + offset_y))
        screen.blit(title_image, title_rect)
    else:
        draw_centered_text(screen, title_font, "AKSTEROID", SCREEN_TITLE_Y, SCREEN_TEXT_COLOR, offset_x, offset_y)

    draw_centered_text(
        screen,
        subtitle_font,
        "PAUSED",
        PAUSE_SCREEN_SUBTITLE_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "Press ESC to Resume",
        PAUSE_SCREEN_INSTRUCTION_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "Press I for Instructions",
        PAUSE_SCREEN_SECONDARY_INSTRUCTION_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "Press Q to Quit",
        SCREEN_THIRD_INSTRUCTION_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )


# INSTRUCTIONS SCREEN
def draw_instructions_screen(screen, title_image, title_font, subtitle_font, offset_x: float = 0, offset_y: float = 0):
    draw_overlay(screen)

    if title_image is not None:
        title_rect = title_image.get_rect(center=(SCREEN_WIDTH / 2 + offset_x, SCREEN_TITLE_Y + offset_y))
        screen.blit(title_image, title_rect)
    else:
        draw_centered_text(screen, title_font, "AKSTEROID", SCREEN_TITLE_Y, SCREEN_TEXT_COLOR, offset_x, offset_y)

    draw_centered_text(
        screen,
        subtitle_font,
        "INSTRUCTIONS",
        INSTRUCTIONS_TITLE_Y + 20,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "W / S = Thrust Forward / Backward",
        INSTRUCTIONS_LINE_1_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "A / D = Rotate Left / Right",
        INSTRUCTIONS_LINE_2_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "SPACE = Shoot    B = Bomb",
        INSTRUCTIONS_LINE_3_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "1 / 2 / 3 = Switch Weapons",
        INSTRUCTIONS_LINE_4_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "ESC = Pause / Resume",
        INSTRUCTIONS_LINE_5_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "Collect power-ups for speed boosts and shields",
        INSTRUCTIONS_LINE_6_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
    draw_centered_text(
        screen,
        subtitle_font,
        "Press ESC or ENTER to Return",
        INSTRUCTIONS_RETURN_Y,
        SCREEN_TEXT_COLOR,
        offset_x,
        offset_y,
    )
def add_screen_shake(current_timer, current_intensity, duration, intensity):
    return max(current_timer, duration), max(current_intensity, intensity)


def get_screen_shake_offset(shake_timer, shake_intensity) -> tuple[float, float]:
    if not SCREEN_SHAKE_ENABLED or shake_timer <= 0 or shake_intensity <= 0:
        return 0, 0

    offset_x = random.uniform(-shake_intensity, shake_intensity)
    offset_y = random.uniform(-shake_intensity, shake_intensity)
    return offset_x, offset_y


def reset_game(
    updatable,
    drawable,
    aksteroids,
    shots,
    explosions,
    speed_powerups,
    shield_powerups,
    bomb_powerups,
):
    updatable.empty()
    drawable.empty()
    aksteroids.empty()
    shots.empty()
    explosions.empty()
    speed_powerups.empty()
    shield_powerups.empty()
    bomb_powerups.empty()

    AksteroidField.containers = (updatable,)
    Aksteroid.containers = (aksteroids, updatable, drawable)
    Shot.containers = (shots, updatable, drawable)
    Explosion.containers = (explosions, updatable, drawable)
    SpeedPowerUp.containers = (speed_powerups, updatable, drawable)
    ShieldPowerUp.containers = (shield_powerups, updatable, drawable)
    BombPowerUp.containers = (bomb_powerups, updatable, drawable)
    Player.containers = (updatable, drawable)

    _aksteroid_field = AksteroidField()
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    score = 0
    lives = PLAYER_STARTING_LIVES
    respawn_invulnerability_timer = 0

    bomb_pickups_remaining = TOTAL_BOMB_PICKUPS_AVAILABLE
    return player, score, lives, respawn_invulnerability_timer, bomb_pickups_remaining


def main():
    pygame.init()
    audio_manager = AudioManager()
    audio_manager.load_sound("shoot", SOUND_SHOOT_PATH)
    audio_manager.load_sound("explosion", SOUND_EXPLOSION_PATH)
    audio_manager.load_sound("powerup_pickup", SOUND_POWERUP_PICKUP_PATH)
    audio_manager.load_sound("bomb", SOUND_BOMB_PATH)
    audio_manager.load_sound("player_hit", SOUND_PLAYER_HIT_PATH)
    audio_manager.load_sound("menu_start", SOUND_MENU_START_PATH)
    audio_manager.load_sound("game_over", SOUND_GAME_OVER_PATH)
    audio_manager.play_music(MENU_MUSIC_PATH)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Aksteroid")
    clock = pygame.time.Clock()
    hud_font = create_game_font(SCORE_FONT_SIZE)
    title_font = create_game_font(SCREEN_TITLE_FONT_SIZE)
    subtitle_font = create_game_font(SCREEN_SUBTITLE_FONT_SIZE)
    bomb_hud_image = load_bomb_hud_image()
    weapon_icons = load_weapon_icons()
    title_image = load_screen_image(
        TITLE_IMAGE_PATH,
        USE_TITLE_IMAGE,
        TITLE_IMAGE_WIDTH,
        TITLE_IMAGE_HEIGHT,
    )
    game_over_image = load_screen_image(
        GAME_OVER_IMAGE_PATH,
        USE_GAME_OVER_IMAGE,
        GAME_OVER_IMAGE_WIDTH,
        GAME_OVER_IMAGE_HEIGHT,
    )
    high_score = load_high_score()
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
    bomb_powerups = pygame.sprite.Group()

    game_state = GAME_STATE_START
    previous_game_state = GAME_STATE_START
    player, score, lives, respawn_invulnerability_timer, bomb_pickups_remaining = reset_game(
        updatable,
        drawable,
        aksteroids,
        shots,
        explosions,
        speed_powerups,
        shield_powerups,
        bomb_powerups,
    )
    powerup_spawn_timer = get_next_powerup_spawn_time()
    bomb_powerup_spawn_timer = get_next_bomb_powerup_spawn_time()

    screen_shake_timer = 0
    screen_shake_intensity = 0

    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if game_state == GAME_STATE_START:
                    if event.key == pygame.K_RETURN:
                        audio_manager.play_sound("menu_start")
                        audio_manager.play_music(GAMEPLAY_MUSIC_PATH, force_restart=True)
                        player, score, lives, respawn_invulnerability_timer, bomb_pickups_remaining = reset_game(
                            updatable,
                            drawable,
                            aksteroids,
                            shots,
                            explosions,
                            speed_powerups,
                            shield_powerups,
                            bomb_powerups,
                        )
                        powerup_spawn_timer = get_next_powerup_spawn_time()
                        bomb_powerup_spawn_timer = get_next_bomb_powerup_spawn_time()
                        game_state = GAME_STATE_PLAYING
                    elif event.key == pygame.K_i:
                        previous_game_state = game_state
                        game_state = GAME_STATE_INSTRUCTIONS
                    elif event.key == pygame.K_q:
                        return

                elif game_state == GAME_STATE_PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        game_state = GAME_STATE_PAUSED
                        audio_manager.play_music(MENU_MUSIC_PATH)
                    elif event.key == pygame.K_i:
                        previous_game_state = game_state
                        game_state = GAME_STATE_INSTRUCTIONS

                elif game_state == GAME_STATE_PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        game_state = GAME_STATE_PLAYING
                        audio_manager.play_music(GAMEPLAY_MUSIC_PATH)
                    elif event.key == pygame.K_i:
                        previous_game_state = game_state
                        game_state = GAME_STATE_INSTRUCTIONS
                    elif event.key == pygame.K_q:
                        return

                elif game_state == GAME_STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        audio_manager.play_sound("menu_start")
                        audio_manager.play_music(GAMEPLAY_MUSIC_PATH, force_restart=True)
                        player, score, lives, respawn_invulnerability_timer, bomb_pickups_remaining = reset_game(
                            updatable,
                            drawable,
                            aksteroids,
                            shots,
                            explosions,
                            speed_powerups,
                            shield_powerups,
                            bomb_powerups,
                        )
                        powerup_spawn_timer = get_next_powerup_spawn_time()
                        bomb_powerup_spawn_timer = get_next_bomb_powerup_spawn_time()
                        game_state = GAME_STATE_PLAYING
                    elif event.key == pygame.K_i:
                        previous_game_state = game_state
                        game_state = GAME_STATE_INSTRUCTIONS
                    elif event.key == pygame.K_q:
                        return

                elif game_state == GAME_STATE_INSTRUCTIONS:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        game_state = previous_game_state

                        if previous_game_state == GAME_STATE_PLAYING:
                            audio_manager.play_music(GAMEPLAY_MUSIC_PATH)
                        else:
                            audio_manager.play_music(MENU_MUSIC_PATH)
                    elif event.key == pygame.K_q:
                        return

        if screen_shake_timer > 0:
            screen_shake_timer -= dt
            if screen_shake_timer < 0:
                screen_shake_timer = 0

        shake_offset_x, shake_offset_y = get_screen_shake_offset(
            screen_shake_timer,
            screen_shake_intensity,
        )

        if screen_shake_timer <= 0:
            screen_shake_intensity = 0

        if background is not None:
            screen.blit(background, (shake_offset_x, shake_offset_y))
        else:
            screen.fill(BACKGROUND_COLOR)

        if game_state == GAME_STATE_START:
            draw_start_screen(screen, title_font, subtitle_font, title_image, high_score, shake_offset_x, shake_offset_y)
            pygame.display.flip()
            dt = clock.tick(60) / 1000
            continue

        if game_state == GAME_STATE_PAUSED:
            draw_pause_screen(screen, title_image, title_font, subtitle_font, shake_offset_x, shake_offset_y)
            pygame.display.flip()
            dt = clock.tick(60) / 1000
            continue

        if game_state == GAME_STATE_INSTRUCTIONS:
            draw_instructions_screen(screen, title_image, title_font, subtitle_font, shake_offset_x, shake_offset_y)
            pygame.display.flip()
            dt = clock.tick(60) / 1000
            continue

        if game_state != GAME_STATE_PLAYING:
            draw_game_over_screen(screen, title_font, subtitle_font, score, high_score, game_over_image, shake_offset_x, shake_offset_y)
            pygame.display.flip()
            dt = clock.tick(60) / 1000
            continue

        shots_before_update = len(shots)
        updatable.update(dt)
        if len(shots) > shots_before_update:
            audio_manager.play_sound("shoot")

        powerup_spawn_timer -= dt
        if powerup_spawn_timer <= 0:
            spawn_random_powerup(speed_powerups, shield_powerups)
            powerup_spawn_timer = get_next_powerup_spawn_time()

        bomb_powerup_spawn_timer -= dt
        if (
            player.bombs <= 0
            and bomb_pickups_remaining > 0
            and len(bomb_powerups) < BOMB_POWERUP_MAX_ACTIVE
            and bomb_powerup_spawn_timer <= 0
        ):
            spawn_bomb_powerup(bomb_powerups)
            bomb_powerup_spawn_timer = get_next_bomb_powerup_spawn_time()

        for speed_powerup in speed_powerups:
            if speed_powerup.collides_with(player):
                player.activate_speed_powerup()
                speed_powerup.kill()
                audio_manager.play_sound("powerup_pickup")
                break

        for shield_powerup in shield_powerups:
            if shield_powerup.collides_with(player):
                player.activate_shield()
                shield_powerup.kill()
                audio_manager.play_sound("powerup_pickup")
                break

        for bomb_powerup in bomb_powerups:
            if bomb_powerup.collides_with(player):
                player.add_bomb(1)
                bomb_powerup.kill()
                bomb_pickups_remaining -= 1
                audio_manager.play_sound("powerup_pickup")
                break

        if player.trigger_bomb:
            screen_shake_timer, screen_shake_intensity = add_screen_shake(
                screen_shake_timer,
                screen_shake_intensity,
                SCREEN_SHAKE_BOMB_DURATION,
                SCREEN_SHAKE_BOMB_INTENSITY,
            )
            audio_manager.play_sound("bomb")
            aksteroids_to_bomb = list(aksteroids)

            if aksteroids_to_bomb:
                audio_manager.play_sound("explosion")

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
                audio_manager.play_sound("player_hit")
                screen_shake_timer, screen_shake_intensity = add_screen_shake(
                    screen_shake_timer,
                    screen_shake_intensity,
                    SCREEN_SHAKE_PLAYER_HIT_DURATION,
                    SCREEN_SHAKE_PLAYER_HIT_INTENSITY,
                )
                lives -= 1

                if lives <= 0:
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)

                    audio_manager.play_sound("game_over")
                    audio_manager.play_music(MENU_MUSIC_PATH, force_restart=True)
                    game_state = GAME_STATE_GAME_OVER
                    break

                player.reset()
                respawn_invulnerability_timer = PLAYER_RESPAWN_INVULNERABILITY_SECONDS
                break

        for aksteroid in aksteroids:
            for shot in shots:
                if aksteroid.collides_with(shot):
                    log_event("aksteroid_shot")
                    audio_manager.play_sound("explosion")
                    screen_shake_timer, screen_shake_intensity = add_screen_shake(
                        screen_shake_timer,
                        screen_shake_intensity,
                        SCREEN_SHAKE_EXPLOSION_DURATION,
                        SCREEN_SHAKE_EXPLOSION_INTENSITY,
                    )
                    score += SCORE_PER_AKSTEROID

                    hit_position = aksteroid.position.copy()
                    hit_radius = aksteroid.radius
                    Explosion(hit_position.x, hit_position.y, hit_radius)

                    aksteroid.split()
                    shot.kill()
                    break

        for obj in drawable:
            original_position = obj.position.copy()
            obj.position.x += shake_offset_x
            obj.position.y += shake_offset_y
            obj.draw(screen)
            obj.position = original_position

        draw_score(screen, hud_font, score, shake_offset_x, shake_offset_y)
        draw_lives(screen, hud_font, lives, shake_offset_x, shake_offset_y)
        draw_bombs(screen, hud_font, player.bombs, bomb_hud_image, shake_offset_x, shake_offset_y)
        draw_weapon(screen, hud_font, player, weapon_icons, shake_offset_x, shake_offset_y)

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
