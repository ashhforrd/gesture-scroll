from dataclasses import dataclass

import pytest

from gesture_scroll.gesture import GestureConfig, ScrollGestureController


@dataclass
class Point:
    x: float
    y: float


def make_hand(palm_y: float = 0.5, pinched: bool = True) -> list[Point]:
    points = [Point(0.5, palm_y) for _ in range(21)]
    points[0] = Point(0.5, palm_y + 0.10)
    points[9] = Point(0.5, palm_y)
    points[4] = Point(0.45, palm_y - 0.05)
    points[8] = Point(0.47 if pinched else 0.65, palm_y - 0.05)
    return points


def test_no_hand_resets_controller() -> None:
    controller = ScrollGestureController()
    assert controller.update(None, now=0).hand_detected is False


def test_open_hand_does_not_scroll() -> None:
    controller = ScrollGestureController(GestureConfig(smoothing=1.0))
    result = controller.update(make_hand(pinched=False), now=0)
    assert result.hand_detected is True
    assert result.active is False
    assert result.scroll_amount == 0


def test_pinched_hand_moving_up_scrolls_up() -> None:
    controller = ScrollGestureController(
        GestureConfig(smoothing=1.0, movement_threshold=0.01, cooldown_seconds=0)
    )
    controller.update(make_hand(palm_y=0.50), now=0)
    result = controller.update(make_hand(palm_y=0.45), now=0.1)
    assert result.active is True
    assert result.scroll_amount > 0


def test_pinched_hand_moving_down_scrolls_down() -> None:
    controller = ScrollGestureController(
        GestureConfig(smoothing=1.0, movement_threshold=0.01, cooldown_seconds=0)
    )
    controller.update(make_hand(palm_y=0.45), now=0)
    result = controller.update(make_hand(palm_y=0.52), now=0.1)
    assert result.scroll_amount < 0


def test_small_movement_is_ignored() -> None:
    controller = ScrollGestureController(
        GestureConfig(smoothing=1.0, movement_threshold=0.02, cooldown_seconds=0)
    )
    controller.update(make_hand(palm_y=0.50), now=0)
    result = controller.update(make_hand(palm_y=0.495), now=0.1)
    assert result.scroll_amount == 0


def test_invalid_smoothing_is_rejected() -> None:
    with pytest.raises(ValueError):
        GestureConfig(smoothing=0)

