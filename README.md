# ClipForge by CodeX

ClipForge is a Python GUI by CodeX to split videos into 30s/60s parts quickly.

Requirements:
- Python 3.8+
- FFmpeg (MoviePy will offer to fetch a portable copy if missing)

Setup:
1) Open a terminal in this folder (`video_trimmer`).
2) Install deps: `python -m pip install -r requirements.txt`

Run:
- `python app.py`
- Or double-click `run.bat` on Windows.

Usage:
1) Choose input video and output folder.
2) Select 30s or 60s segment size.
3) Click Analyze to see how many parts will be created and the last part length.
4) Click Split Video to generate all parts. Files are saved as `<name>_part_001.ext`, `<name>_part_002.ext`, ...
  - Optional: Set "Filename base" to change the output name prefix.

Notes:
- If the remaining tail is shorter than the selected duration, the last part will be shorter.
- Output uses H.264 video (libx264) and AAC audio.

Branding & Logo
- Put your PNG logo at `video_trimmer/assets/logo.png`. The window icon uses this logo at runtime.
- To set the EXE/installer icon, add an ICO at `video_trimmer/assets/clipforge.ico`.

Performance
- ClipForge uses ffmpeg stream-copy for cuts where possible (`-c copy`) which is near-instant and avoids re-encoding. If stream-copy fails, it falls back to safe re-encode.
- A progress bar shows percent, with elapsed time and ETA.

Build (Windows)
1) Install PyInstaller: `python -m pip install pyinstaller`
2) Build executable:
   ```bash
   pyinstaller --noconsole --name ClipForge \
     --icon assets/clipforge.ico \
     --add-data assets;assets app.py
   ```
   Output is in `dist/ClipForge/`.
3) Inno Setup: open `installer/ClipForge.iss` and Build. It packages `dist/ClipForge`.

Support
- Developed by CodeX. For issues, include OS version, steps, and logs.
