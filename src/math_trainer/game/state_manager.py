from __future__ import annotations

from pathlib import Path

import pygame

from math_trainer.database_manager import DatabaseManager
from math_trainer.game.audio import SoundEffects
from math_trainer.game.constants import FPS
from math_trainer.game.states.base import GameState
from math_trainer.game.states.menu_state import MenuState
from math_trainer.game.states.play_state import PlayState
from math_trainer.game.states.summary_state import SummaryState
from math_trainer.question_generator import QuestionGenerator


class GameStateManager:
    def __init__(
        self,
        screen: pygame.Surface,
        db_path: str | Path = "math_trainer.db",
    ) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_state: GameState | None = None

        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2)

        self.db = DatabaseManager(db_path)
        self.question_generator = QuestionGenerator(self.db)
        self.sounds = SoundEffects()

        self.states: dict[str, GameState] = {
            "menu": MenuState(self),
            "play": PlayState(self),
            "summary": SummaryState(self),
        }

        self.change_state("menu")

    def change_state(self, name: str, **kwargs) -> None:
        if self.current_state is not None:
            self.current_state.exit()

        self.current_state = self.states[name]
        self.current_state.enter(**kwargs)

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.current_state is not None:
                    self.current_state.handle_event(event)

            if self.current_state is not None:
                self.current_state.update(dt)
                self.current_state.draw(self.screen)

            pygame.display.flip()

        self.db.close()
        pygame.quit()
