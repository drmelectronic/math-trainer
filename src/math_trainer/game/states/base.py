from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from math_trainer.game.state_manager import GameStateManager


class GameState(ABC):
    def __init__(self, manager: GameStateManager) -> None:
        self.manager = manager

    def enter(self, **kwargs) -> None:
        return

    def exit(self) -> None:
        return

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        pass
