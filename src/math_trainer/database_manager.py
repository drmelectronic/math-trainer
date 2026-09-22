import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from math_trainer.models import QuestionAttempt

SLOW_RESPONSE_MS = 5000
MIN_FAILURES_FOR_REINFORCEMENT = 2


class DatabaseManager:
    def __init__(self, db_path: str | Path = "math_trainer.db") -> None:
        self.db_path = Path(db_path)
        self._connection = sqlite3.connect(self.db_path)
        self._connection.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                question_text TEXT NOT NULL,
                correct_answer INTEGER NOT NULL,
                user_answer INTEGER,
                is_correct INTEGER NOT NULL,
                response_time_ms INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

    def record_attempt(self, attempt: QuestionAttempt) -> None:
        timestamp = attempt.timestamp or datetime.now(UTC)
        self._connection.execute(
            """
            INSERT INTO attempts (
                operation_type,
                question_text,
                correct_answer,
                user_answer,
                is_correct,
                response_time_ms,
                timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attempt.operation_type,
                attempt.question_text,
                attempt.correct_answer,
                attempt.user_answer,
                int(attempt.is_correct),
                attempt.response_time_ms,
                timestamp.isoformat(),
            ),
        )
        self._connection.commit()

    def get_attempts_for_question(self, question_text: str) -> list[dict]:
        cursor = self._connection.execute(
            """
            SELECT operation_type, question_text, correct_answer, user_answer,
                   is_correct, response_time_ms, timestamp
            FROM attempts
            WHERE question_text = ?
            ORDER BY timestamp ASC
            """,
            (question_text,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_average_time(self, question_text: str) -> float | None:
        cursor = self._connection.execute(
            "SELECT AVG(response_time_ms) AS avg_time FROM attempts WHERE question_text = ?",
            (question_text,),
        )
        row = cursor.fetchone()
        if row is None or row["avg_time"] is None:
            return None
        return float(row["avg_time"])

    def get_error_rate(self, question_text: str) -> float | None:
        cursor = self._connection.execute(
            """
            SELECT
                SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) AS failures,
                COUNT(*) AS total
            FROM attempts
            WHERE question_text = ?
            """,
            (question_text,),
        )
        row = cursor.fetchone()
        if row is None or row["total"] == 0:
            return None
        return row["failures"] / row["total"]

    def get_reinforcement_candidates(self) -> list[str]:
        cursor = self._connection.execute(
            """
            SELECT
                question_text,
                SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) AS failures,
                MAX(response_time_ms) AS max_time
            FROM attempts
            GROUP BY question_text
            """
        )

        candidates: list[str] = []
        for row in cursor.fetchall():
            question_text = row["question_text"]
            failures = row["failures"]
            max_time = row["max_time"]

            if failures >= MIN_FAILURES_FOR_REINFORCEMENT or max_time > SLOW_RESPONSE_MS:
                candidates.append(question_text)

        return candidates

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "DatabaseManager":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
