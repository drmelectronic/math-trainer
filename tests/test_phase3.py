import unittest

from math_trainer.game.feedback import ERROR_DURATION, SUCCESS_DURATION, FeedbackAnimator
from math_trainer.models import QuestionAttempt, SessionStats


class TestFeedbackAnimator(unittest.TestCase):
    def test_success_animation_completes(self) -> None:
        animator = FeedbackAnimator()
        animator.start_success()
        self.assertTrue(animator.is_active())

        finished = False
        elapsed = 0.0
        while elapsed < SUCCESS_DURATION + 0.1:
            if animator.update(0.05):
                finished = True
                break
            elapsed += 0.05

        self.assertTrue(finished)
        self.assertFalse(animator.is_active())

    def test_error_animation_last_two_seconds(self) -> None:
        animator = FeedbackAnimator()
        animator.start_error()

        finished = False
        elapsed = 0.0
        while elapsed < ERROR_DURATION + 0.1:
            offset = animator.get_shake_offset()
            self.assertNotEqual(offset, (0, 0))
            if animator.update(0.1):
                finished = True
                break
            elapsed += 0.1

        self.assertTrue(finished)

    def test_flash_alpha_only_on_success(self) -> None:
        animator = FeedbackAnimator()
        self.assertEqual(animator.get_flash_alpha(), 0)
        animator.start_success()
        self.assertGreater(animator.get_flash_alpha(), 0)


class TestSessionStats(unittest.TestCase):
    def test_from_attempts_calculates_metrics(self) -> None:
        attempts = [
            QuestionAttempt("add", "2 + 2 = ?", 4, 4, True, 1200),
            QuestionAttempt("mul", "3 × 3 = ?", 9, 8, False, 4500),
            QuestionAttempt("mul", "7 × 8 = ?", 56, 56, True, 8000),
        ]
        stats = SessionStats.from_attempts(level=2, score=10, stars=2, attempts=attempts)

        self.assertEqual(stats.correct, 2)
        self.assertEqual(stats.total, 3)
        self.assertAlmostEqual(stats.avg_response_ms, (1200 + 4500 + 8000) / 3)
        self.assertEqual(stats.slowest_response_ms, 8000)
        self.assertEqual(stats.slowest_question, "7 × 8 = ?")
        self.assertEqual(stats.weak_questions, ["3 × 3 = ?"])

    def test_empty_attempts(self) -> None:
        stats = SessionStats.from_attempts(level=1, score=0, stars=0, attempts=[])
        self.assertEqual(stats.total, 0)
        self.assertEqual(stats.avg_response_ms, 0.0)


if __name__ == "__main__":
    unittest.main()
