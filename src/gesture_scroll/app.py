"""Aplikasi webcam untuk mengontrol scroll layar dengan gesture tangan."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Sequence, Tuple

from gesture_scroll.gesture import GestureConfig, ScrollGestureController
from gesture_scroll.model import ensure_model


HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20), (0, 17),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Kontrol scroll layar menggunakan gesture pinch tangan.",
    )
    parser.add_argument("--camera", type=int, default=0, help="Indeks kamera (default: 0)")
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("models/hand_landmarker.task"),
        help="Lokasi model MediaPipe",
    )
    parser.add_argument("--pinch-threshold", type=float, default=0.45)
    parser.add_argument("--dead-zone", type=float, default=0.012)
    parser.add_argument("--sensitivity", type=float, default=120.0)
    parser.add_argument("--cooldown", type=float, default=0.06)
    parser.add_argument("--smoothing", type=float, default=0.35)
    parser.add_argument("--max-scroll", type=int, default=6)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Tampilkan deteksi tanpa mengirim scroll ke sistem",
    )
    parser.add_argument(
        "--download-model-only",
        action="store_true",
        help="Unduh model lalu keluar",
    )
    return parser


def _draw_hand(frame, landmarks: Sequence, color: Tuple[int, int, int], cv2) -> None:
    height, width = frame.shape[:2]
    points = [(int(point.x * width), int(point.y * height)) for point in landmarks]
    for start, end in HAND_CONNECTIONS:
        cv2.line(frame, points[start], points[end], (120, 120, 120), 2)
    for point in points:
        cv2.circle(frame, point, 4, (255, 255, 255), -1)
    for index in (4, 8):
        cv2.circle(frame, points[index], 9, color, -1)


def _open_camera(index: int, cv2):
    """Buka kamera dengan backend native macOS dan fallback otomatis."""
    if sys.platform == "darwin":
        camera = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
        if camera.isOpened():
            return camera
        camera.release()
    return cv2.VideoCapture(index)


def run(args: argparse.Namespace) -> int:
    model_path = ensure_model(args.model)
    if args.download_model_only:
        print(f"Model siap: {model_path}")
        return 0

    # Impor ditunda agar pengujian logika tidak memerlukan GUI atau webcam.
    import cv2
    import mediapipe as mp
    import pyautogui

    config = GestureConfig(
        pinch_threshold=args.pinch_threshold,
        movement_threshold=args.dead_zone,
        scroll_gain=args.sensitivity,
        cooldown_seconds=args.cooldown,
        smoothing=args.smoothing,
        max_scroll=args.max_scroll,
    )
    controller = ScrollGestureController(config)

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.01

    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path=str(model_path),
            delegate=mp.tasks.BaseOptions.Delegate.CPU,
        ),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    camera = _open_camera(args.camera, cv2)
    if not camera.isOpened():
        print(f"Kamera dengan indeks {args.camera} tidak dapat dibuka.")
        print("Tutup aplikasi lain yang memakai kamera atau coba --camera 1.")
        return 1

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    last_timestamp = 0
    consecutive_read_failures = 0
    max_read_failures = 50

    print("Aplikasi berjalan. Pinch untuk mengaktifkan scroll; tekan Q untuk keluar.")
    try:
        with mp.tasks.vision.HandLandmarker.create_from_options(options) as detector:
            while True:
                success, frame = camera.read()
                if not success or frame is None or frame.size == 0:
                    consecutive_read_failures += 1
                    if consecutive_read_failures == 1:
                        print("Menunggu kamera mengirim frame ...")
                    if consecutive_read_failures >= max_read_failures:
                        print("Frame kamera tetap tidak dapat dibaca setelah 5 detik.")
                        print("Tutup FaceTime/Zoom/browser, lalu coba --camera 1.")
                        return 1
                    time.sleep(0.1)
                    continue

                consecutive_read_failures = 0

                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                timestamp = max(int(time.monotonic() * 1000), last_timestamp + 1)
                last_timestamp = timestamp
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                detection = detector.detect_for_video(image, timestamp)
                landmarks = detection.hand_landmarks[0] if detection.hand_landmarks else None
                gesture = controller.update(landmarks, time.monotonic())

                if gesture.active:
                    status = "SCROLL AKTIF"
                    color = (0, 210, 0)
                elif gesture.hand_detected:
                    status = "PINCH JEMPOL + TELUNJUK"
                    color = (0, 210, 255)
                else:
                    status = "TANGAN TIDAK TERDETEKSI"
                    color = (0, 0, 230)

                if landmarks:
                    _draw_hand(frame, landmarks, color, cv2)
                if gesture.scroll_amount and not args.dry_run:
                    pyautogui.scroll(gesture.scroll_amount)

                mode = "DRY RUN" if args.dry_run else "KONTROL AKTIF"
                detail = f"Pinch: {gesture.pinch_ratio:.2f}" if gesture.pinch_ratio else "Pinch: -"
                cv2.putText(frame, status, (20, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.72, color, 2)
                cv2.putText(frame, f"{mode} | {detail}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (240, 240, 240), 1)
                cv2.putText(frame, "Q / ESC: keluar", (20, 98), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 240, 240), 1)
                cv2.imshow("Gesture Scroll", frame)

                pressed_key = cv2.waitKey(1) & 0xFF
                if pressed_key in (ord("q"), ord("Q"), 27):
                    break
    except KeyboardInterrupt:
        pass
    except RuntimeError as error:
        print(f"MediaPipe gagal dimulai: {error}")
        print("Pastikan aplikasi dijalankan dari sesi desktop dan izin kamera aktif.")
        return 1
    finally:
        camera.release()
        cv2.destroyAllWindows()

    return 0


def main() -> None:
    args = build_parser().parse_args()
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
