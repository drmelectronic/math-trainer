import pygame

from math_trainer.game.constants import (
    COLOR_BACKGROUND,
    COLOR_BOARD,
    COLOR_ERROR,
    COLOR_HUD,
    COLOR_STAR,
    COLOR_SUCCESS,
    COLOR_TEXT,
    COLOR_TEXT_LIGHT,
    FONT_LARGE,
    FONT_MEDIUM,
    FONT_SMALL,
    HUD_HEIGHT,
    INPUT_HEIGHT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SESSION_LENGTH,
)
from math_trainer.game.feedback import FeedbackAnimator
from math_trainer.game.states.base import GameState
from math_trainer.game.ui.elements import NumericInputBox, ProgressBar, TextLabel
from math_trainer.models import Question, QuestionAttempt, SessionStats


class PlayState(GameState):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.level = 1
        self.score = 0
        self.stars = 0
        self.answered = 0
        self.current_question: Question | None = None
        self.session_attempts: list[QuestionAttempt] = []
        self.question_start_ms = 0
        self.feedback = FeedbackAnimator()
        self.input_enabled = True

        self.level_label = TextLabel(
            pygame.Rect(20, 10, 200, 30),
            "Nivel 1",
            font_size=FONT_SMALL,
            color=COLOR_TEXT_LIGHT,
            align="left",
        )
        self.score_label = TextLabel(
            pygame.Rect(0, 10, SCREEN_WIDTH, 30),
            "Puntos: 0",
            font_size=FONT_SMALL,
            color=COLOR_TEXT_LIGHT,
        )
        self.stars_label = TextLabel(
            pygame.Rect(SCREEN_WIDTH - 220, 10, 200, 30),
            "★ 0",
            font_size=FONT_SMALL,
            color=COLOR_STAR,
            align="right",
        )
        self.progress_bar = ProgressBar(pygame.Rect(20, 50, SCREEN_WIDTH - 40, 16))
        self.question_label = TextLabel(
            pygame.Rect(0, HUD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT - INPUT_HEIGHT),
            "0 + 0 = ?",
            font_size=FONT_LARGE,
            color=COLOR_TEXT,
        )
        self.input_box = NumericInputBox(
            pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 80, 240, 56)
        )
        self.input_box.on_submit = self._submit_answer
        self.feedback_label = TextLabel(
            pygame.Rect(0, SCREEN_HEIGHT - 130, SCREEN_WIDTH, 30),
            "",
            font_size=FONT_MEDIUM,
            color=COLOR_TEXT,
        )

        self.ui_elements = [
            self.level_label,
            self.score_label,
            self.stars_label,
            self.progress_bar,
            self.question_label,
            self.input_box,
            self.feedback_label,
        ]

    def enter(self, **kwargs) -> None:
        self.level = kwargs.get("level", 1)
        self.score = 0
        self.stars = 0
        self.answered = 0
        self.session_attempts = []
        self.input_enabled = True
        self.feedback.reset()
        self.feedback_label.set_text("")
        self.level_label.set_text(f"Nivel {self.level}")
        self.manager.question_generator.set_level(self.level)
        self._update_hud()
        self._next_question()

    def exit(self) -> None:
        self.input_box.set_active(False)

    def _next_question(self) -> None:
        if self.answered >= SESSION_LENGTH:
            stats = SessionStats.from_attempts(
                self.level,
                self.score,
                self.stars,
                self.session_attempts,
            )
            self.manager.change_state("summary", stats=stats)
            return

        self.current_question = self.manager.question_generator.generate()
        self.question_label.set_text(self.current_question.question_text)
        self.question_label.color = COLOR_TEXT
        self.input_box.clear()
        self.input_box.set_active(True)
        self.input_enabled = True
        self.feedback_label.set_text("")
        self.question_start_ms = pygame.time.get_ticks()

    def _submit_answer(self, value: int | None) -> None:
        if not self.input_enabled or self.feedback.is_active():
            return

        if value is None:
            self.feedback_label.set_text("Escribe un número y presiona Enter")
            return

        if self.current_question is None:
            return

        response_time_ms = pygame.time.get_ticks() - self.question_start_ms
        is_correct = value == self.current_question.correct_answer
        attempt = QuestionAttempt(
            operation_type=self.current_question.operation_type,
            question_text=self.current_question.question_text,
            correct_answer=self.current_question.correct_answer,
            user_answer=value,
            is_correct=is_correct,
            response_time_ms=response_time_ms,
        )
        self.manager.db.record_attempt(attempt)
        self.session_attempts.append(attempt)
        self.answered += 1

        if is_correct:
            self.score += 10
            self.stars += 1
            self.feedback_label.set_text("¡Correcto!")
            self.feedback_label.color = COLOR_SUCCESS
            self.manager.sounds.play_success()
            self.feedback.start_success()
        else:
            answer_text = self.current_question.question_text.replace("?", str(self.current_question.correct_answer))
            self.question_label.set_text(answer_text)
            self.question_label.color = COLOR_ERROR
            self.feedback_label.set_text("Inténtalo de nuevo la próxima vez")
            self.feedback_label.color = COLOR_ERROR
            self.manager.sounds.play_error()
            self.feedback.start_error()

        self.input_enabled = False
        self.input_box.set_active(False)
        self._update_hud()

    def _finish_feedback(self) -> None:
        if self.answered >= SESSION_LENGTH:
            stats = SessionStats.from_attempts(
                self.level,
                self.score,
                self.stars,
                self.session_attempts,
            )
            self.manager.change_state("summary", stats=stats)
            return

        self._next_question()

    def _update_hud(self) -> None:
        self.score_label.set_text(f"Puntos: {self.score}")
        self.stars_label.set_text(f"★ {self.stars}")
        self.progress_bar.set_progress(self.answered, SESSION_LENGTH)

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.input_enabled:
            return

        if event.type == pygame.KEYDOWN:
            if self.input_box.handle_event(event):
                return

        for element in self.ui_elements:
            if element.handle_event(event):
                break

    def update(self, dt: float) -> None:
        if self.feedback.update(dt):
            self._finish_feedback()

        for element in self.ui_elements:
            element.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        shake_x, shake_y = self.feedback.get_shake_offset()
        frame = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        frame.fill(COLOR_BACKGROUND)
        pygame.draw.rect(frame, COLOR_HUD, pygame.Rect(0, 0, SCREEN_WIDTH, HUD_HEIGHT))

        board_rect = pygame.Rect(
            40,
            HUD_HEIGHT + 20,
            SCREEN_WIDTH - 80,
            SCREEN_HEIGHT - HUD_HEIGHT - INPUT_HEIGHT - 40,
        )
        pygame.draw.rect(frame, COLOR_BOARD, board_rect, border_radius=12)

        for element in self.ui_elements:
            element.draw(frame)

        surface.blit(frame, (shake_x, shake_y))

        alpha = self.feedback.get_flash_alpha()
        if alpha > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((*self.feedback.flash_color, alpha))
            surface.blit(overlay, (0, 0))
