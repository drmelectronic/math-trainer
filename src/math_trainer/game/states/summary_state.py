import pygame

from math_trainer.game.constants import (
    COLOR_BACKGROUND,
    COLOR_ERROR,
    COLOR_TEXT,
    FONT_MEDIUM,
    FONT_SMALL,
    FONT_TITLE,
    SCREEN_WIDTH,
)
from math_trainer.game.states.base import GameState
from math_trainer.game.ui.elements import Button, TextLabel
from math_trainer.models import SessionStats


class SummaryState(GameState):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.title = TextLabel(
            pygame.Rect(0, 70, SCREEN_WIDTH, 60),
            "Resumen de sesión",
            font_size=FONT_TITLE,
            color=COLOR_TEXT,
        )
        self.stats_label = TextLabel(
            pygame.Rect(40, 150, SCREEN_WIDTH - 80, 180),
            "",
            font_size=FONT_MEDIUM,
            color=COLOR_TEXT,
        )
        self.weak_label = TextLabel(
            pygame.Rect(40, 340, SCREEN_WIDTH - 80, 100),
            "",
            font_size=FONT_SMALL,
            color=COLOR_ERROR,
        )
        self.menu_button = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 120, 470, 240, 56),
            "Volver al menú",
            self._return_to_menu,
        )
        self.ui_elements = [self.title, self.stats_label, self.weak_label, self.menu_button]
        self.stats = SessionStats(1, 0, 0, 0, 0, 0, 0.0, 0, None, [])

    def enter(self, **kwargs) -> None:
        self.stats = kwargs.get(
            "stats",
            SessionStats(1, 0, 0, 0, 0, 0, 0.0, 0, None, []),
        )

        accuracy = (self.stats.correct / self.stats.total * 100) if self.stats.total else 0
        avg_seconds = self.stats.avg_response_ms / 1000
        slowest_seconds = self.stats.slowest_response_ms / 1000

        lines = [
            f"Nivel: {self.stats.level}",
            f"Racha actual: {self.stats.current_streak}",
            f"Mejor racha de la sesión: {self.stats.session_best_streak}",
            f"Récord del nivel: {self.stats.level_max_streak}",
            f"Preguntas: {self.stats.total}  |  Aciertos: {self.stats.correct} ({accuracy:.0f}%)",
            f"Tiempo promedio: {avg_seconds:.1f}s",
            f"Respuesta más lenta: {slowest_seconds:.1f}s",
        ]
        if self.stats.slowest_question:
            lines.append(f"  ({self.stats.slowest_question})")
        self.stats_label.set_text("\n".join(lines))

        if self.stats.weak_questions:
            preview = ", ".join(self.stats.weak_questions[:3])
            extra = "" if len(self.stats.weak_questions) <= 3 else "..."
            self.weak_label.set_text(f"Para reforzar: {preview}{extra}")
        else:
            self.weak_label.set_text("¡Excelente! Sin errores en esta sesión.")

    def _return_to_menu(self) -> None:
        self.manager.change_state("menu")

    def handle_event(self, event: pygame.event.Event) -> None:
        for element in self.ui_elements:
            element.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self._return_to_menu()

    def update(self, dt: float) -> None:
        for element in self.ui_elements:
            element.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BACKGROUND)
        for element in self.ui_elements:
            element.draw(surface)
