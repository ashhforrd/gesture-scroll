"""Pengelolaan model MediaPipe Hand Landmarker."""

from __future__ import annotations

from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)


def ensure_model(model_path: Path) -> Path:
    if model_path.is_file() and model_path.stat().st_size > 0:
        return model_path

    model_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = model_path.with_suffix(model_path.suffix + ".download")

    print(f"Model belum tersedia. Mengunduh ke {model_path} ...")
    try:
        with urlopen(MODEL_URL, timeout=60) as response:
            with temporary_path.open("wb") as destination:
                while chunk := response.read(1024 * 1024):
                    destination.write(chunk)
        temporary_path.replace(model_path)
    except (OSError, URLError) as error:
        temporary_path.unlink(missing_ok=True)
        raise RuntimeError(
            "Gagal mengunduh model MediaPipe. Periksa koneksi internet atau "
            f"unduh manual dari {MODEL_URL}"
        ) from error

    return model_path

