from __future__ import annotations

from abc import ABC, abstractmethod

import pygame

from math_trainer.game.constants import (
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_INPUT_ACTIVE,
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_PROGRESS_BG,
    COLOR_PROGRESS_FILL,
    COLOR_TEXT,
    COLOR_TEXT_LIGHT,
    FONT_LARGE,
    FONT_MEDIUM,
    FONT_SMALL,
)


class UIElement(ABC):
    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect
        self.visible = True

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Procesa un evento. Retorna True si fue consumido."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Actualiza estado interno."""

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja el elemento en pantalla."""


class TextLabel(UIElement):
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font_size: int = FONT_MEDIUM,
        color: tuple[int, int, int] = COLOR_TEXT,
        align: str = "center",
    ) -> None:
        super().__init__(rect)
        self.text = text
        self.font_size = font_size
        self.color = color
        self.align = align
        self._font = pygame.font.SysFont("dejavusans", font_size, bold=True)

    def set_text(self, text: str) -> None:
        self.text = text

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def update(self, dt: float) -> None:
        return

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        rendered = self._font.render(self.text, True, self.color)
        if self.align == "center":
            x = self.rect.centerx - rendered.get_width() // 2
            y = self.rect.centery - rendered.get_height() // 2
        elif self.align == "left":
            x = self.rect.left
            y = self.rect.centery - rendered.get_height() // 2
        else:
            x = self.rect.right - rendered.get_width()
            y = self.rect.centery - rendered.get_height() // 2
        surface.blit(rendered, (x, y))


class Button(UIElement):
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        on_click: callable,
        font_size: int = FONT_SMALL,
    ) -> None:
        super().__init__(rect)
        self.text = text
        self.on_click = on_click
        self.font_size = font_size
        self.hovered = False
        self._font = pygame.font.SysFont("dejavusans", font_size, bold=True)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()
                return True

        return False

    def update(self, dt: float) -> None:
        return

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        color = COLOR_ACCENT_HOVER if self.hovered else COLOR_ACCENT
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        rendered = self._font.render(self.text, True, COLOR_TEXT_LIGHT)
        surface.blit(
            rendered,
            (
                self.rect.centerx - rendered.get_width() // 2,
                self.rect.centery - rendered.get_height() // 2,
            ),
        )


class NumericInputBox(UIElement):
    def __init__(self, rect: pygame.Rect, max_digits: int = 4) -> None:
        super().__init__(rect)
        self.max_digits = max_digits
        self.text = ""
        self.active = False
        self.placeholder = "?"
        self._font = pygame.font.SysFont("dejavusans", FONT_LARGE, bold=True)
        self.on_submit: callable | None = None

    def clear(self) -> None:
        self.text = ""

    def get_value(self) -> int | None:
        if not self.text:
            return None
        return int(self.text)

    def set_active(self, active: bool) -> None:
        self.active = active

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            return self.active or was_active

        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.on_submit is not None:
                    self.on_submit(self.get_value())
                return True

            if event.key == pygame.K_ESCAPE:
                self.clear()
                return True

            if event.unicode.isdigit() and len(self.text) < self.max_digits:
                if self.text == "0":
                    self.text = event.unicode
                else:
                    self.text += event.unicode
                return True

        return False

    def update(self, dt: float) -> None:
        return

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        border_color = COLOR_INPUT_ACTIVE if self.active else COLOR_INPUT_BORDER
        pygame.draw.rect(surface, COLOR_INPUT_BG, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, width=3, border_radius=8)

        display_text = self.text if self.text else self.placeholder
        text_color = COLOR_TEXT if self.text else COLOR_INPUT_BORDER
        rendered = self._font.render(display_text, True, text_color)
        surface.blit(
            rendered,
            (
                self.rect.centerx - rendered.get_width() // 2,
                self.rect.centery - rendered.get_height() // 2,
            ),
        )


class ProgressBar(UIElement):
    def __init__(self, rect: pygame.Rect) -> None:
        super().__init__(rect)
        self.progress = 0.0

    def set_progress(self, current: int, total: int) -> None:
        if total <= 0:
            self.progress = 0.0
        else:
            self.progress = max(0.0, min(1.0, current / total))

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

    def update(self, dt: float) -> None:
        return

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        pygame.draw.rect(surface, COLOR_PROGRESS_BG, self.rect, border_radius=6)
        fill_width = int(self.rect.width * self.progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.left, self.rect.top, fill_width, self.rect.height)
            pygame.draw.rect(surface, COLOR_PROGRESS_FILL, fill_rect, border_radius=6)
