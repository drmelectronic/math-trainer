import pygame

from math_trainer.game.constants import (
    COLOR_BACKGROUND,
    COLOR_TEXT,
    FONT_MEDIUM,
    FONT_TITLE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from math_trainer.game.states.base import GameState
from math_trainer.game.ui.elements import Button, TextLabel


class MenuState(GameState):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.title = TextLabel(
            pygame.Rect(0, 120, SCREEN_WIDTH, 80),
            "Math Trainer",
            font_size=FONT_TITLE,
            color=COLOR_TEXT,
        )
        self.subtitle = TextLabel(
            pygame.Rect(0, 200, SCREEN_WIDTH, 40),
            "Elige tu nivel",
            font_size=FONT_MEDIUM,
            color=COLOR_TEXT,
        )
        button_width = 180
        button_height = 56
        gap = 24
        start_x = (SCREEN_WIDTH - (button_width * 3 + gap * 2)) // 2
        y = 300

        self.level_buttons = [
            Button(
                pygame.Rect(start_x, y, button_width, button_height),
                "Nivel 1",
                lambda level=1: self._start_game(level),
            ),
            Button(
                pygame.Rect(start_x + button_width + gap, y, button_width, button_height),
                "Nivel 2",
                lambda level=2: self._start_game(level),
            ),
            Button(
                pygame.Rect(start_x + (button_width + gap) * 2, y, button_width, button_height),
                "Nivel 3",
                lambda level=3: self._start_game(level),
            ),
        ]
        self.ui_elements = [self.title, self.subtitle, *self.level_buttons]

    def enter(self, **kwargs) -> None:
        for level, button in zip((1, 2, 3), self.level_buttons, strict=True):
            record = self.manager.db.get_max_streak(level)
            button.text = f"Nivel {level} (récord: {record})"

    def _start_game(self, level: int) -> None:
        self.manager.change_state("play", level=level)

    def handle_event(self, event: pygame.event.Event) -> None:
        for element in self.ui_elements:
            element.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
            self._start_game(int(event.unicode))

    def update(self, dt: float) -> None:
        for element in self.ui_elements:
            element.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BACKGROUND)
        for element in self.ui_elements:
            element.draw(surface)

        hint_font = pygame.font.SysFont("dejavusans", 20)
        hint = hint_font.render("También puedes presionar 1, 2 o 3", True, COLOR_TEXT)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 80))
