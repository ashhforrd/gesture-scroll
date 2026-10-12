# Gesture Scroll

Control screen scrolling with real-time hand gestures captured through a webcam.
The application uses MediaPipe to detect 21 hand landmarks and PyAutoGUI to send
scroll commands to the application under the mouse pointer.

## How It Works

1. Hold one hand in front of the webcam.
2. Bring your thumb and index fingertip together to activate scrolling.
3. Keep pinching while moving your hand up or down.
4. Release the pinch to stop scrolling.

Moving your hand up scrolls up, while moving it down scrolls down. Motion
smoothing, a configurable dead zone, and a short cooldown help prevent jitter
and unintended scrolling.

## Requirements

- Python 3.9 or newer
- A webcam
- macOS, Windows, or Linux with a desktop environment

## Installation

Create a virtual environment and install the project:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

On Windows PowerShell, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Usage

Start in dry-run mode to test hand detection without controlling the screen:

```bash
gesture-scroll --dry-run
```

Once detection works correctly, start the application normally:

```bash
gesture-scroll
```

The MediaPipe Hand Landmarker model is downloaded automatically to `models/`
the first time the application starts. Focus the camera window and press `Q`,
`q`, or `Esc` to exit. You can also press `Ctrl+C` in the terminal.

To run the project without installing its command-line entry point:

```bash
PYTHONPATH=src python -m gesture_scroll --dry-run
```

## System Permissions

### macOS

Grant Terminal, Visual Studio Code, or whichever application launches the
project access to:

- **System Settings → Privacy & Security → Camera**
- **System Settings → Privacy & Security → Accessibility**

Camera permission allows the application to read webcam frames. Accessibility
permission allows PyAutoGUI to send scroll commands. Quit and reopen the
terminal application after changing these permissions.

### Windows

Make sure camera access for desktop applications is enabled under **Settings →
Privacy & security → Camera**.

## Configuration

Example with increased sensitivity:

```bash
gesture-scroll --sensitivity 160 --dead-zone 0.009 --smoothing 0.4
```

Available options:

| Option | Default | Description |
|---|---:|---|
| `--camera` | `0` | Webcam device index |
| `--pinch-threshold` | `0.45` | Higher values make the pinch easier to activate |
| `--sensitivity` | `120` | Scroll strength |
| `--dead-zone` | `0.012` | Minimum movement before scrolling begins |
| `--smoothing` | `0.35` | Motion smoothing factor between 0 and 1 |
| `--cooldown` | `0.06` | Minimum delay between scroll events, in seconds |
| `--max-scroll` | `6` | Maximum scroll amount per update |
| `--dry-run` | off | Run detection without controlling the screen |

If scrolling is too sensitive, lower `--sensitivity` or increase
`--dead-zone`. If scrolling feels slow, do the opposite.

## Testing

Install the development dependencies and run the test suite:

```bash
pip install -e '.[dev]'
pytest
```

The tests cover pinch activation, scroll direction, dead-zone behavior, input
validation, and controller reset when no hand is detected.

## Troubleshooting

- **The camera does not open or frames cannot be read:** Close FaceTime, Zoom,
  browser tabs, or any other application using the webcam. Then try
  `gesture-scroll --dry-run` or `gesture-scroll --camera 1 --dry-run`.
- **Detection works but the screen does not scroll:** Enable Accessibility
  permission and place the mouse pointer over the application you want to
  scroll.
- **The screen scrolls without intentional movement:** Increase `--dead-zone`,
  for example to `0.02`.
- **The pinch is difficult to activate:** Increase `--pinch-threshold`, for
  example to `0.55`.
- **The camera window is lagging:** Close other applications using the webcam
  and improve the lighting around your hand.
- **`Q` does not close the application:** Click the camera window before
  pressing `Q`, or press `Ctrl+C` in the terminal.
