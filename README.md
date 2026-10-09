# Icescript Player — Private Offline Video Player

A 100% offline, privacy-first video player for local courses and lessons with integrated hardware-accelerated video playback and a local AES-256 encryption protection layer.

**No server. No internet. No external APIs. No telemetry.**

---

## Features

- **Branding**: Icescript Player with custom multi-resolution high-DPI icon.
- **Authentication**: PIN protection (salted SHA-256 with constant-time comparison).
- **Video Protection**: Custom streaming AES-256-CTR encryption (`.cvid` container).
- **Ephemeral Playback**: Decrypted data exists only temporarily during active playback, securely wiped on track change, stop, or application exit.
- **Offline Library**: Automatically organizes folders as courses and video files as lessons.
- **Progress Tracking**: Remembers exact playback position and provides a **Continue Watching** list.
- **Built-in Encryptor**: GUI tool (`🔒 Protect Videos...`) and CLI tool (`encrypt_course.py`) to convert raw `.mp4`/`.mkv` files into protected `.cvid` files with optional raw deletion.
- **Modern Minimal UI**: Dark-themed PySide6 interface with distraction-free fullscreen mode.

---

## Directory Layout

```
Player Cripto/
├── app/
│   ├── main.py              # Application entry point
│   ├── config.py            # App paths & constants
│   ├── database/
│   │   ├── database.py      # SQLite persistence (WAL mode)
│   │   └── models.py        # Course, Lesson, Settings dataclasses
│   ├── security/
│   │   ├── authentication.py # Salted SHA-256 PIN management
│   │   └── encryption.py    # AES-256-CTR streaming encryption/decryption
│   ├── ui/
│   │   ├── login_window.py  # PIN setup & unlock dialog
│   │   ├── main_window.py   # Primary window (sidebar + player + lessons)
│   │   ├── video_player.py  # QMediaPlayer + QVideoWidget controls
│   │   ├── encrypt_dialog.py# In-app video encryption interface
│   │   └── styles.py        # Dark theme stylesheet
│   └── video/
│       ├── video_manager.py # Ephemeral playback & progress tracking
│       └── video_library.py # Filesystem scanner & sync
├── data/
│   ├── app.db               # SQLite database (auto-created)
│   └── .cache/              # Ephemeral playback cache (auto-wiped)
├── videos/                  # Your courses & lessons (.cvid or raw video)
├── encrypt_course.py        # CLI encryption utility
├── requirements.txt
├── run.bat                  # Launch script
└── build.bat                # PyInstaller packaging script
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the application
```bash
python app/main.py
```
*(Or double-click `run.bat`)*

1. On first launch, create your 4+ digit PIN.
2. The player will open showing your courses in `videos/`.
3. Select a lesson and enjoy smooth, offline playback.

---

## How Video Protection Works

Raw video files (`.mp4`, `.mkv`, etc.) can be converted into protected `.cvid` files:

1. **Header**: Magic signature (`PCVID01`), per-file 16-byte salt, 16-byte IV, and original file extension.
2. **Cipher**: Streamed chunk-by-chunk (64 KB) using AES-256-CTR derived via PBKDF2-HMAC-SHA256 from the master key.
3. **Playback**: When an encrypted lesson is selected:
   - It is decrypted to a session token file in `data/.cache/`.
   - The player streams the temporary file.
   - When you switch lessons, pause, or close the app, the temporary cache file is overwritten and deleted.

### Encrypting Videos

#### Option A: Inside the GUI
1. Open the application.
2. Click **🔒 Protect Videos...** in the sidebar.
3. Click **Find All Unencrypted in 'videos/'** (or select a specific file).
4. Check **Delete original raw video(s)** if you want to remove the source files.
5. Click **Start Encryption**.

#### Option B: From the Terminal
```bash
# Encrypt an entire course folder
python encrypt_course.py "videos/Sample Course"

# Encrypt and delete original .mp4 files
python encrypt_course.py "videos/Sample Course" --delete-original

# Encrypt a single video
python encrypt_course.py "path/to/lesson.mp4" --delete-original
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Space` | Play / Pause |
| `→` | Seek forward 10 seconds |
| `←` | Seek backward 10 seconds |
| `F` or `F11` | Toggle Fullscreen |
| `Esc` | Exit Fullscreen |
| Double Click on Video | Toggle Fullscreen |

---

## Packaging as Windows Executable (`.exe`)

To build a standalone executable that runs without Python:

```cmd
build.bat
```

Output will be located in `dist/PlayerCripto/PlayerCripto.exe`.
Copy your `videos/` folder into `dist/PlayerCripto/` for distribution.
