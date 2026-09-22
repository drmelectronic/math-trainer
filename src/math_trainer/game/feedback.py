import random

SUCCESS_DURATION = 0.6
ERROR_DURATION = 2.0


class FeedbackAnimator:
    def __init__(self) -> None:
        self.phase = "none"
        self.elapsed = 0.0

    def is_active(self) -> bool:
        return self.phase != "none"

    def start_success(self) -> None:
        self.phase = "success"
        self.elapsed = 0.0

    def start_error(self) -> None:
        self.phase = "error"
        self.elapsed = 0.0

    def reset(self) -> None:
        self.phase = "none"
        self.elapsed = 0.0

    def update(self, dt: float) -> bool:
        if self.phase == "none":
            return False

        self.elapsed += dt
        duration = SUCCESS_DURATION if self.phase == "success" else ERROR_DURATION
        if self.elapsed >= duration:
            self.reset()
            return True

        return False

    def get_shake_offset(self) -> tuple[int, int]:
        if self.phase != "error":
            return (0, 0)

        decay = max(0.0, 1.0 - self.elapsed / ERROR_DURATION)
        intensity = max(1, int(10 * decay))
        return (
            random.randint(-intensity, intensity),
            random.randint(-intensity, intensity),
        )

    def get_flash_alpha(self) -> int:
        if self.phase != "success":
            return 0

        return 100 if int(self.elapsed * 8) % 2 == 0 else 35

    @property
    def flash_color(self) -> tuple[int, int, int]:
        return (39, 174, 96)
