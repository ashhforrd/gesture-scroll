"""Logika gesture yang tidak bergantung pada kamera atau MediaPipe."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Optional, Protocol, Sequence


class Landmark(Protocol):
    x: float
    y: float


@dataclass(frozen=True)
class GestureConfig:
    pinch_threshold: float = 0.45
    movement_threshold: float = 0.012
    scroll_gain: float = 120.0
    cooldown_seconds: float = 0.06
    smoothing: float = 0.35
    max_scroll: int = 6

    def __post_init__(self) -> None:
        if self.pinch_threshold <= 0:
            raise ValueError("pinch_threshold harus lebih dari 0")
        if self.movement_threshold < 0:
            raise ValueError("movement_threshold tidak boleh negatif")
        if self.scroll_gain <= 0:
            raise ValueError("scroll_gain harus lebih dari 0")
        if self.cooldown_seconds < 0:
            raise ValueError("cooldown_seconds tidak boleh negatif")
        if not 0 < self.smoothing <= 1:
            raise ValueError("smoothing harus berada di antara 0 dan 1")
        if self.max_scroll < 1:
            raise ValueError("max_scroll minimal 1")


@dataclass(frozen=True)
class GestureResult:
    hand_detected: bool
    active: bool
    scroll_amount: int = 0
    pinch_ratio: Optional[float] = None
    palm_y: Optional[float] = None


def _distance(a: Landmark, b: Landmark) -> float:
    return hypot(a.x - b.x, a.y - b.y)


def _palm_center_y(landmarks: Sequence[Landmark]) -> float:
    palm_indices = (0, 5, 9, 13, 17)
    return sum(landmarks[index].y for index in palm_indices) / len(palm_indices)


class ScrollGestureController:
    """Mengubah landmark tangan menjadi perintah scroll yang stabil."""

    def __init__(self, config: Optional[GestureConfig] = None) -> None:
        self.config = config or GestureConfig()
        self._smoothed_y: Optional[float] = None
        self._anchor_y: Optional[float] = None
        self._last_scroll_time = float("-inf")

    def reset(self) -> None:
        self._smoothed_y = None
        self._anchor_y = None

    def update(
        self,
        landmarks: Optional[Sequence[Landmark]],
        now: float,
    ) -> GestureResult:
        if landmarks is None:
            self.reset()
            return GestureResult(hand_detected=False, active=False)

        if len(landmarks) < 21:
            raise ValueError("Diperlukan 21 landmark tangan")

        wrist = landmarks[0]
        middle_finger_base = landmarks[9]
        palm_size = max(_distance(wrist, middle_finger_base), 0.001)
        pinch_ratio = _distance(landmarks[4], landmarks[8]) / palm_size
        current_y = _palm_center_y(landmarks)

        if self._smoothed_y is None:
            self._smoothed_y = current_y
        else:
            alpha = self.config.smoothing
            self._smoothed_y = alpha * current_y + (1 - alpha) * self._smoothed_y

        active = pinch_ratio < self.config.pinch_threshold
        if not active:
            self._anchor_y = None
            return GestureResult(
                hand_detected=True,
                active=False,
                pinch_ratio=pinch_ratio,
                palm_y=self._smoothed_y,
            )

        if self._anchor_y is None:
            self._anchor_y = self._smoothed_y
            return GestureResult(
                hand_detected=True,
                active=True,
                pinch_ratio=pinch_ratio,
                palm_y=self._smoothed_y,
            )

        movement = self._smoothed_y - self._anchor_y
        cooldown_elapsed = now - self._last_scroll_time >= self.config.cooldown_seconds
        scroll_amount = 0

        if abs(movement) >= self.config.movement_threshold and cooldown_elapsed:
            # Koordinat Y citra bertambah ke bawah, sedangkan nilai scroll positif ke atas.
            scroll_amount = round(-movement * self.config.scroll_gain)
            if scroll_amount == 0:
                scroll_amount = 1 if movement < 0 else -1
            scroll_amount = max(
                -self.config.max_scroll,
                min(self.config.max_scroll, scroll_amount),
            )
            self._anchor_y = self._smoothed_y
            self._last_scroll_time = now

        return GestureResult(
            hand_detected=True,
            active=True,
            scroll_amount=scroll_amount,
            pinch_ratio=pinch_ratio,
            palm_y=self._smoothed_y,
        )
