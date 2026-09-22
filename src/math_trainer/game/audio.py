import array
import math

import pygame

from math_trainer.game.constants import COLOR_SUCCESS

SAMPLE_RATE = 44100


def _append_tone(
    buf: array.array,
    frequency: float,
    start_sample: int,
    duration_samples: int,
    volume: float = 0.35,
) -> None:
    attack = max(1, int(SAMPLE_RATE * 0.01))
    release = max(1, int(SAMPLE_RATE * 0.06))
    for i in range(duration_samples):
        envelope = 1.0
        if i < attack:
            envelope = i / attack
        elif i > duration_samples - release:
            envelope = max(0.0, (duration_samples - i) / release)
        sample = int(
            envelope * volume * 32767 * math.sin(2 * math.pi * frequency * i / SAMPLE_RATE)
        )
        sample = max(-32767, min(32767, sample))
        stereo_index = (start_sample + i) * 2
        while len(buf) <= stereo_index + 1:
            buf.extend([0, 0])
        buf[stereo_index] = sample
        buf[stereo_index + 1] = sample


def _build_success_sound() -> pygame.mixer.Sound:
    duration_ms = 320
    total_samples = int(SAMPLE_RATE * duration_ms / 1000)
    tone_samples = int(SAMPLE_RATE * 0.1)
    buf: array.array = array.array("h")
    buf.extend([0, 0] * total_samples)

    for index, frequency in enumerate((523.25, 659.25, 783.99)):
        _append_tone(buf, frequency, index * tone_samples // 2, tone_samples)

    return pygame.mixer.Sound(buffer=buf)


def _build_error_sound() -> pygame.mixer.Sound:
    duration_ms = 280
    total_samples = int(SAMPLE_RATE * duration_ms / 1000)
    buf: array.array = array.array("h")
    _append_tone(buf, 180, 0, total_samples, volume=0.45)
    return pygame.mixer.Sound(buffer=buf)


class SoundEffects:
    def __init__(self) -> None:
        self._success = _build_success_sound()
        self._error = _build_error_sound()

    def play_success(self) -> None:
        self._success.play()

    def play_error(self) -> None:
        self._error.play()
