import pygame
import sys
from logger import log_state, log_event
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from player import Player
from aksteroidfield import AksteroidField
from aksteroid import Aksteroid
from shot import Shot


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
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

        screen.fill("black")

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
                    aksteroid.split()
                    shot.kill()

        for obj in drawable:
            obj.draw(screen)

        pygame.display.flip()
        dt = clock.tick(60) / 1000
      


if __name__ == "__main__":
    main()
