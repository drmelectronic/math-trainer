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
    score: int
    stars: int
    correct: int
    total: int
    avg_response_ms: float
    slowest_response_ms: int
    slowest_question: str | None
    weak_questions: list[str]

    @classmethod
    def from_attempts(
        cls,
        level: int,
        score: int,
        stars: int,
        attempts: list[QuestionAttempt],
    ) -> "SessionStats":
        total = len(attempts)
        correct = sum(1 for attempt in attempts if attempt.is_correct)
        if total == 0:
            return cls(level, score, stars, 0, 0, 0.0, 0, None, [])

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
            score=score,
            stars=stars,
            correct=correct,
            total=total,
            avg_response_ms=avg_response_ms,
            slowest_response_ms=times[slowest_idx],
            slowest_question=slowest_attempt.question_text,
            weak_questions=weak_questions,
        )
