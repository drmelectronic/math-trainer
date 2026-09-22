import sys

import pygame

from math_trainer.game.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from math_trainer.game.state_manager import GameStateManager


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Math Trainer")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    manager = GameStateManager(screen)
    manager.run()
    sys.exit(0)


if __name__ == "__main__":
    main()
