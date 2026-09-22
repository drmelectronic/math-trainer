from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Question:
    operation_type: str
    question_text: str
    correct_answer: int
    operand_a: int
    operand_b: int


@dataclass
class QuestionAttempt:
    operation_type: str
    question_text: str
    correct_answer: int
    user_answer: int | None
    is_correct: bool
    response_time_ms: int
    timestamp: datetime | None = None


@dataclass
class SessionStats:
    level: int
    total: int
    correct: int
    current_streak: int
    session_best_streak: int
    level_max_streak: int
    avg_response_ms: float
    slowest_response_ms: int
    slowest_question: str | None
    weak_questions: list[str]

    @classmethod
    def from_attempts(
        cls,
        level: int,
        attempts: list[QuestionAttempt],
        current_streak: int,
        session_best_streak: int,
        level_max_streak: int,
    ) -> "SessionStats":
        total = len(attempts)
        correct = sum(1 for attempt in attempts if attempt.is_correct)
        if total == 0:
            return cls(
                level,
                0,
                0,
                current_streak,
                session_best_streak,
                level_max_streak,
                0.0,
                0,
                None,
                [],
            )

        times = [attempt.response_time_ms for attempt in attempts]
        avg_response_ms = sum(times) / total
        slowest_idx = max(range(total), key=lambda index: times[index])
        slowest_attempt = attempts[slowest_idx]
        weak_questions = list(
            dict.fromkeys(
                attempt.question_text for attempt in attempts if not attempt.is_correct
            )
        )

        return cls(
            level=level,
            total=total,
            correct=correct,
            current_streak=current_streak,
            session_best_streak=session_best_streak,
            level_max_streak=level_max_streak,
            avg_response_ms=avg_response_ms,
            slowest_response_ms=times[slowest_idx],
            slowest_question=slowest_attempt.question_text,
            weak_questions=weak_questions,
        )
