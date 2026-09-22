import unittest

import pygame

from math_trainer.game.ui.elements import NumericInputBox, ProgressBar


class TestNumericInputBox(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def setUp(self) -> None:
        self.input_box = NumericInputBox(pygame.Rect(0, 0, 200, 50), max_digits=4)
        self.input_box.set_active(True)
        self.submitted: list[int | None] = []
        self.input_box.on_submit = self.submitted.append

    def _key(self, key: int, unicode: str = "") -> pygame.event.Event:
        return pygame.event.Event(pygame.KEYDOWN, key=key, unicode=unicode)

    def test_accepts_key_codes_without_unicode(self) -> None:
        self.input_box.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_7, unicode="")
        )
        self.input_box.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_8, unicode="")
        )
        self.assertEqual(self.input_box.text, "78")

    def test_ignores_textinput_to_avoid_duplicates(self) -> None:
        self.input_box.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1, unicode="")
        )
        self.input_box.handle_event(pygame.event.Event(pygame.TEXTINPUT, text="1"))
        self.assertEqual(self.input_box.text, "1")

    def test_key_code_and_unicode_on_same_event_count_once(self) -> None:
        self.input_box.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_5, unicode="5")
        )
        self.assertEqual(self.input_box.text, "5")

    def test_accepts_digits_up_to_max(self) -> None:
        for digit in "1234":
            self.input_box.handle_event(self._key(ord(digit), digit))
        self.assertEqual(self.input_box.text, "1234")
        self.input_box.handle_event(self._key(ord("5"), "5"))
        self.assertEqual(self.input_box.text, "1234")

    def test_backspace_removes_last_digit(self) -> None:
        self.input_box.handle_event(self._key(ord("7"), "7"))
        self.input_box.handle_event(self._key(ord("2"), "2"))
        self.input_box.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, unicode=""))
        self.assertEqual(self.input_box.text, "7")

    def test_enter_submits_value(self) -> None:
        self.input_box.handle_event(self._key(ord("9"), "9"))
        self.input_box.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="")
        )
        self.assertEqual(self.submitted, [9])

    def test_empty_submit_returns_none(self) -> None:
        self.input_box.handle_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="")
        )
        self.assertEqual(self.submitted, [None])

    def test_clear_resets_text(self) -> None:
        self.input_box.handle_event(self._key(ord("3"), "3"))
        self.input_box.clear()
        self.assertEqual(self.input_box.text, "")
        self.assertIsNone(self.input_box.get_value())

    def test_leading_zero_is_replaced(self) -> None:
        self.input_box.handle_event(self._key(ord("0"), "0"))
        self.input_box.handle_event(self._key(ord("5"), "5"))
        self.assertEqual(self.input_box.text, "5")


class TestProgressBar(unittest.TestCase):
    def test_clamps_progress(self) -> None:
        bar = ProgressBar(pygame.Rect(0, 0, 100, 10))
        bar.set_progress(3, 10)
        self.assertAlmostEqual(bar.progress, 0.3)
        bar.set_progress(15, 10)
        self.assertAlmostEqual(bar.progress, 1.0)
        bar.set_progress(-1, 10)
        self.assertAlmostEqual(bar.progress, 0.0)


if __name__ == "__main__":
    unittest.main()
