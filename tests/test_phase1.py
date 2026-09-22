import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from math_trainer.database_manager import DatabaseManager
from math_trainer.models import QuestionAttempt
from math_trainer.question_generator import QuestionGenerator


class TestQuestionGeneratorLevels(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test.db"
        self.db = DatabaseManager(db_path)

    def tearDown(self) -> None:
        self.db.close()
        self.temp_dir.cleanup()

    def test_level_1_addition_without_carry(self) -> None:
        generator = QuestionGenerator(self.db, level=1)
        for _ in range(50):
            question = generator.generate_from_operation("add")
            self.assertEqual(
                (question.operand_a % 10) + (question.operand_b % 10),
                question.correct_answer % 10,
            )

    def test_level_1_subtraction_without_borrow(self) -> None:
        generator = QuestionGenerator(self.db, level=1)
        for _ in range(50):
            question = generator.generate_from_operation("sub")
            self.assertGreaterEqual(question.operand_a, question.operand_b)
            self.assertGreaterEqual(question.operand_a % 10, question.operand_b % 10)

    def test_level_2_addition_with_carry(self) -> None:
        generator = QuestionGenerator(self.db, level=2)
        for _ in range(50):
            question = generator.generate_from_operation("add")
            self.assertGreaterEqual((question.operand_a % 10) + (question.operand_b % 10), 10)

    def test_level_2_multiplication_tables_6_to_8(self) -> None:
        generator = QuestionGenerator(self.db, level=2)
        for _ in range(50):
            question = generator.generate_from_operation("mul")
            self.assertGreaterEqual(question.operand_a, 6)
            self.assertLessEqual(question.operand_a, 8)
            self.assertGreaterEqual(question.operand_b, 6)
            self.assertLessEqual(question.operand_b, 8)

    def test_level_3_two_digit_operations(self) -> None:
        generator = QuestionGenerator(self.db, level=3)
        for _ in range(50):
            question = generator.generate_from_operation("add")
            self.assertGreaterEqual(question.operand_a, 10)
            self.assertGreaterEqual(question.operand_b, 10)

    def test_division_is_exact(self) -> None:
        for level in (1, 2, 3):
            generator = QuestionGenerator(self.db, level=level)
            for _ in range(50):
                question = generator.generate_from_operation("div")
                self.assertEqual(question.operand_a % question.operand_b, 0)
                self.assertEqual(
                    question.correct_answer,
                    question.operand_a // question.operand_b,
                )


class TestReinforcementLogic(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test.db"
        self.db = DatabaseManager(db_path)
        self.generator = QuestionGenerator(self.db, level=1)

    def tearDown(self) -> None:
        self.db.close()
        self.temp_dir.cleanup()

    def _record_failure(self, question_text: str, correct_answer: int) -> None:
        self.db.record_attempt(
            QuestionAttempt(
                operation_type="mul",
                question_text=question_text,
                correct_answer=correct_answer,
                user_answer=correct_answer + 1,
                is_correct=False,
                response_time_ms=2000,
            )
        )

    def test_reinforcement_candidates_after_consistent_failures(self) -> None:
        question_text = "7 × 8 = ?"
        self._record_failure(question_text, 56)
        self._record_failure(question_text, 56)

        candidates = self.db.get_reinforcement_candidates()
        self.assertIn(question_text, candidates)

    def test_reinforcement_candidates_after_slow_response(self) -> None:
        question_text = "4 × 5 = ?"
        self.db.record_attempt(
            QuestionAttempt(
                operation_type="mul",
                question_text=question_text,
                correct_answer=20,
                user_answer=20,
                is_correct=True,
                response_time_ms=6000,
            )
        )

        candidates = self.db.get_reinforcement_candidates()
        self.assertIn(question_text, candidates)

    @patch("math_trainer.question_generator.random.random", return_value=0.1)
    @patch(
        "math_trainer.question_generator.random.choice",
        return_value="7 × 8 = ?",
    )
    def test_generator_uses_reinforcement(self, mock_choice, mock_random) -> None:
        self._record_failure("7 × 8 = ?", 56)
        self._record_failure("7 × 8 = ?", 56)

        question = self.generator.generate()
        self.assertEqual(question.question_text, "7 × 8 = ?")
        self.assertEqual(question.correct_answer, 56)


class TestDatabaseManager(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test.db"
        self.db = DatabaseManager(db_path)

    def tearDown(self) -> None:
        self.db.close()
        self.temp_dir.cleanup()

    def test_record_and_query_attempts(self) -> None:
        attempt = QuestionAttempt(
            operation_type="add",
            question_text="15 + 8 = ?",
            correct_answer=23,
            user_answer=23,
            is_correct=True,
            response_time_ms=1500,
        )
        self.db.record_attempt(attempt)

        attempts = self.db.get_attempts_for_question("15 + 8 = ?")
        self.assertEqual(len(attempts), 1)
        self.assertTrue(attempts[0]["is_correct"])

    def test_average_time_and_error_rate(self) -> None:
        question_text = "9 × 9 = ?"
        self.db.record_attempt(
            QuestionAttempt(
                operation_type="mul",
                question_text=question_text,
                correct_answer=81,
                user_answer=81,
                is_correct=True,
                response_time_ms=2000,
            )
        )
        self.db.record_attempt(
            QuestionAttempt(
                operation_type="mul",
                question_text=question_text,
                correct_answer=81,
                user_answer=70,
                is_correct=False,
                response_time_ms=4000,
            )
        )

        self.assertEqual(self.db.get_average_time(question_text), 3000.0)
        self.assertEqual(self.db.get_error_rate(question_text), 0.5)

    def test_max_streak_per_level(self) -> None:
        self.assertEqual(self.db.get_max_streak(1), 0)
        self.db.update_max_streak(1, 5)
        self.assertEqual(self.db.get_max_streak(1), 5)
        self.db.update_max_streak(1, 3)
        self.assertEqual(self.db.get_max_streak(1), 5)
        self.db.update_max_streak(1, 8)
        self.assertEqual(self.db.get_max_streak(1), 8)
        self.db.update_max_streak(2, 4)
        self.assertEqual(self.db.get_max_streak(2), 4)
        self.assertEqual(self.db.get_max_streak(1), 8)


if __name__ == "__main__":
    unittest.main()
