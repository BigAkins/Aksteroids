import pygame
import sys
from logger import log_state, log_event
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCORE_PER_AKSTEROID, SCORE_POSITION_X, SCORE_POSITION_Y, SCORE_FONT_SIZE, SCORE_COLOR, BACKGROUND_COLOR
from player import Player
from aksteroidfield import AksteroidField
from aksteroid import Aksteroid
from shot import Shot

def draw_score(screen, font, score):
    score_surface = font.render(f"Score: {score}", True, SCORE_COLOR)
    screen.blit(score_surface, (SCORE_POSITION_X, SCORE_POSITION_Y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
    score = 0
    dt = 0
    print(f"Starting Aksteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    aksteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    AksteroidField.containers = (updatable,)
    Aksteroid.containers = (aksteroids, updatable, drawable)
    Shot.containers = (shots, updatable, drawable)
    aksteroid_field = AksteroidField()

    Player.containers = (updatable, drawable)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        screen.fill(BACKGROUND_COLOR)

        updatable.update(dt)

        for aksteroid in aksteroids:
            if aksteroid.collides_with(player):
                log_event("player_hit")
                print("Game over!")
                sys.exit()

        for aksteroid in aksteroids:
            for shot in shots:
                if aksteroid.collides_with(shot):
                    log_event("aksteroid_shot")
                    score += SCORE_PER_AKSTEROID
                    aksteroid.split()
                    shot.kill()
                    break

        for obj in drawable:
            obj.draw(screen)

        draw_score(screen, score_font, score)

        pygame.display.flip()
        dt = clock.tick(60) / 1000
      


if __name__ == "__main__":
    main()
