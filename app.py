#!/usr/bin/env python3
"""
Web Video Downloader
A small self-hosted web app (Flask + yt-dlp) you can open from any browser,
including Safari on iPhone. Bookmark it to your home screen for an app-like feel.

Setup:
    pip install flask yt-dlp

Run:
    python app.py
    # then visit http://<your-server-ip>:5000 from your iPhone's browser
    # (must be on the same network, or hosted on a public server/VPS)

IMPORTANT: Only download content you own, have explicit permission to save,
or that is licensed for reuse. Downloading other people's videos may violate
platform Terms of Service and copyright law depending on your use case.
"""

import os
import re
import threading
import uuid
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory, render_template

try:
    import yt_dlp
except ImportError:
    raise SystemExit("Missing dependency. Install it first with:\n    pip install yt-dlp")

APP_DIR = Path(__file__).parent
DOWNLOAD_DIR = APP_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)

# In-memory job tracker: job_id -> {status, progress, filename, error}
jobs = {}


def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-. ]', '_', name)[:150]


def run_download(job_id: str, url: str, audio_only: bool, quality: str):
    job = jobs[job_id]

    def hook(d):
        if d["status"] == "downloading":
            job["progress"] = d.get("_percent_str", "0%").strip()
        elif d["status"] == "finished":
            job["progress"] = "processing"

    outtmpl = str(DOWNLOAD_DIR / f"{job_id}_%(title)s.%(ext)s")
    opts = {
        "outtmpl": outtmpl,
        "noplaylist": True,
        "progress_hooks": [hook],
        "quiet": True,
        "no_warnings": True,
    }

    if audio_only:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    else:
        # Prefer H.264 video + AAC/M4A audio first — this is the combo iOS's
        # Photos/Files viewer always plays natively. VP9/WebM (common on
        # Instagram/YouTube) often shows a blank or unplayable file on iPhone,
        # so it's only used as a last-resort fallback here.
        if quality == "best":
            opts["format"] = (
                "bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]/"
                "best[vcodec^=avc1]/"
                "bestvideo+bestaudio/best"
            )
        else:
            opts["format"] = (
                f"bestvideo[vcodec^=avc1][height<={quality}]+bestaudio[acodec^=mp4a]/"
                f"best[vcodec^=avc1][height<={quality}]/"
                f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
            )
        opts["merge_output_format"] = "mp4"
        # Re-encode to H.264/AAC if yt-dlp still had to fall back to VP9/Opus,
        # so the saved file always plays on iOS regardless of source format.
        opts["postprocessors"] = opts.get("postprocessors", []) + [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",
        }]

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_path = ydl.prepare_filename(info)
            if audio_only:
                final_path = str(Path(final_path).with_suffix(".mp3"))
            filename = Path(final_path).name
            job["status"] = "done"
            job["filename"] = filename
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.get_json(force=True)
    url = (data.get("url") or "").strip()
    audio_only = bool(data.get("audio_only", False))
    quality = data.get("quality", "best")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    job_id = uuid.uuid4().hex[:12]
    jobs[job_id] = {"status": "running", "progress": "0%", "filename": None, "error": None}

    thread = threading.Thread(target=run_download, args=(job_id, url, audio_only, quality), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/api/status/<job_id>")
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Unknown job"}), 404
    return jsonify(job)


@app.route("/files/<path:filename>")
def get_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    # host="0.0.0.0" makes it reachable externally (e.g. from Render, or other devices on your network)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
