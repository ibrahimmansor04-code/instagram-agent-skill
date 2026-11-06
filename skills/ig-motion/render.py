#!/usr/bin/env python3
"""render.py - turn a storyboard player into an MP4, frame by frame, with your audio.

    python3 render.py reel.html --audio voice.m4a --out reel.mp4
    python3 render.py reel.html --fps 30 --workers 2 --scale 1

The player is a pure function of time, so every frame is drawn on its own and
the result is identical on every run. Needs Playwright for Python, Chrome (or
Chromium) and ffmpeg. 1080x1920 at scale 1; scale 0.667 gives 720x1280.
"""
import argparse
import multiprocessing as mp
import pathlib
import shutil
import subprocess
import sys
import tempfile


def find_chrome():
    for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        p = shutil.which(c)
        if p:
            return p
    return None


def work(args):
    html, frames, start, stop, fps, scale, outdir, chrome = args
    from playwright.sync_api import sync_playwright
    w, h = int(round(1080 * scale)), int(round(1920 * scale))
    with sync_playwright() as p:
        kw = {"args": ["--no-sandbox", "--disable-gpu", "--hide-scrollbars"]}
        if chrome:
            kw["executable_path"] = chrome
        b = p.chromium.launch(**kw)
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto(pathlib.Path(html).resolve().as_uri() + "?t=0&record=1")
        pg.wait_for_function("typeof window.__seek === 'function'")
        pg.evaluate("document.fonts.ready")
        for i in range(start, stop):
            pg.evaluate("t => window.__seek(t)", i / fps)
            pg.screenshot(path=str(outdir / ("f_%05d.jpg" % i)), type="jpeg", quality=93)
        b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--audio", default="")
    ap.add_argument("--out", default="reel.mp4")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--scale", type=float, default=1.0)
    a = ap.parse_args()
    if a.audio and not pathlib.Path(a.audio).exists():
        sys.exit("Audio file not found: " + a.audio)

    from playwright.sync_api import sync_playwright
    chrome = find_chrome()
    with sync_playwright() as p:
        kw = {"args": ["--no-sandbox"]}
        if chrome:
            kw["executable_path"] = chrome
        b = p.chromium.launch(**kw)
        pg = b.new_page()
        pg.goto(pathlib.Path(a.html).resolve().as_uri() + "?t=0&record=1")
        pg.wait_for_function("typeof window.__duration === 'number'")
        dur = pg.evaluate("window.__duration")
        b.close()
    n = int(round(dur * a.fps))
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="igmotion_"))
    step = -(-n // a.workers)
    jobs = [(a.html, n, k * step, min(n, (k + 1) * step), a.fps, a.scale, tmp, chrome) for k in range(a.workers) if k * step < n]
    print("rendering %d frames (%.1fs at %d fps) with %d workers -> %s" % (n, dur, a.fps, len(jobs), tmp))
    with mp.Pool(len(jobs)) as pool:
        pool.map(work, jobs)
    cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(a.fps), "-i", str(tmp / "f_%05d.jpg")]
    if a.audio:
        cmd += ["-i", a.audio]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-t", "%.2f" % dur]
    if a.audio:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-map", "0:v", "-map", "1:a"]
    cmd += ["-movflags", "+faststart", a.out]
    subprocess.check_call(cmd)
    shutil.rmtree(tmp, ignore_errors=True)
    print("wrote " + a.out)


if __name__ == "__main__":
    main()
