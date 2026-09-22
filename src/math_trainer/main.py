import os
import sys

import pygame

from math_trainer.game.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from math_trainer.game.state_manager import GameStateManager

# Evita comportamientos erráticos de SDL en Wayland (redimensionado/foco).
os.environ.setdefault("SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS", "0")


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Math Trainer")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill((245, 247, 250))
    pygame.display.flip()
    manager = GameStateManager(screen)
    manager.run()
    sys.exit(0)


if __name__ == "__main__":
    main()
