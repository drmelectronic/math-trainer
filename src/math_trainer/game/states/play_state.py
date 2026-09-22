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
)
from math_trainer.game.feedback import FeedbackAnimator
from math_trainer.game.states.base import GameState
from math_trainer.game.ui.elements import Button, NumericInputBox, ProgressBar, TextLabel
from math_trainer.models import Question, QuestionAttempt, SessionStats


class PlayState(GameState):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self.level = 1
        self.current_streak = 0
        self.session_best_streak = 0
        self.level_max_streak = 0
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
        self.streak_label = TextLabel(
            pygame.Rect(0, 10, SCREEN_WIDTH, 30),
            "Racha: 0",
            font_size=FONT_SMALL,
            color=COLOR_TEXT_LIGHT,
        )
        self.record_label = TextLabel(
            pygame.Rect(SCREEN_WIDTH - 260, 10, 240, 30),
            "Récord: 0",
            font_size=FONT_SMALL,
            color=COLOR_STAR,
            align="right",
        )
        self.progress_bar = ProgressBar(pygame.Rect(20, 50, SCREEN_WIDTH - 40, 16))
        self.exit_button = Button(
            pygame.Rect(SCREEN_WIDTH - 110, 45, 90, 28),
            "Salir",
            self._exit_session,
            font_size=20,
        )
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
            self.streak_label,
            self.record_label,
            self.progress_bar,
            self.exit_button,
            self.question_label,
            self.input_box,
            self.feedback_label,
        ]

    def enter(self, **kwargs) -> None:
        self.level = kwargs.get("level", 1)
        self.session_best_streak = 0
        self.current_streak, self.level_max_streak = self.manager.db.get_level_streaks(self.level)
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
            previous_record = self.level_max_streak
            self.current_streak += 1
            self.session_best_streak = max(self.session_best_streak, self.current_streak)
            self.current_streak, self.level_max_streak = self.manager.db.save_level_streaks(
                self.level,
                self.current_streak,
            )
            if self.current_streak > previous_record:
                self.feedback_label.set_text("¡Correcto! ¡Nuevo récord!")
            else:
                self.feedback_label.set_text("¡Correcto!")
            self.feedback_label.color = COLOR_SUCCESS
            self.manager.sounds.play_success()
            self.feedback.start_success()
        else:
            self.current_streak, self.level_max_streak = self.manager.db.save_level_streaks(
                self.level,
                0,
            )
            answer_text = self.current_question.question_text.replace(
                "?",
                str(self.current_question.correct_answer),
            )
            self.question_label.set_text(answer_text)
            self.question_label.color = COLOR_ERROR
            self.feedback_label.set_text("Racha reiniciada")
            self.feedback_label.color = COLOR_ERROR
            self.manager.sounds.play_error()
            self.feedback.start_error()

        self.input_enabled = False
        self.input_box.set_active(False)
        self._update_hud()

    def _finish_feedback(self) -> None:
        self._next_question()

    def _exit_session(self) -> None:
        stats = SessionStats.from_attempts(
            self.level,
            self.session_attempts,
            self.current_streak,
            self.session_best_streak,
            self.level_max_streak,
        )
        self.manager.change_state("summary", stats=stats)

    def _update_hud(self) -> None:
        self.streak_label.set_text(f"Racha: {self.current_streak}")
        self.record_label.set_text(f"Récord: {self.level_max_streak}")
        target = max(self.level_max_streak, 1)
        self.progress_bar.set_progress(self.current_streak, target)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if not self.feedback.is_active():
                self._exit_session()
            return

        if self.input_enabled and event.type == pygame.KEYDOWN:
            if self.input_box.handle_event(event):
                return

        for element in self.ui_elements:
            if element is self.input_box:
                continue
            if element.handle_event(event):
                return

        if self.input_enabled and event.type == pygame.MOUSEBUTTONDOWN:
            self.input_box.handle_event(event)

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
