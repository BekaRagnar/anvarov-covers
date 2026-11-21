"""Animated square cover (silent looping MP4, 1080x1080) for Telegram sendAnimation.

Usage: python3 make_anim.py cover.json out.mp4 [seconds=7]
Same cover.json as make_square.py. The mockup animates: chat messages appear and
the AI reply types itself; code is typed; settings toggles flip; benchmark bars
grow; image tiles appear; voice waveform pulses. Ends on a 2-second hold.
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_square import layout, frame  # noqa: E402

FPS = 24


def build(c, out, seconds=7.0):
    base, acc, box = layout(c)
    scene = c.get("scene", {})
    total = int(seconds * FPS)
    hold = 2 * FPS
    anim = max(FPS, total - hold)
    loop_voice = scene.get("type") == "voice"
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(total):
            if loop_voice:
                t = i / total
            else:
                t = min(1.0, i / anim)
            # window slides up 40px with ease-out during the first 0.5 s
            k = min(1.0, i / (FPS * 0.5))
            dy = int(40 * (1 - k) ** 3)
            frame(base, acc, box, scene, t, dy).convert("RGB").save(f"{tmp}/f{i:04d}.png")
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "-an", out], check=True)
    return out


if __name__ == "__main__":
    data = __import__("json").load(open(sys.argv[1], encoding="utf-8"))
    secs = float(sys.argv[3]) if len(sys.argv) > 3 else 7.0
    print("ok", build(data, sys.argv[2], secs), f"{os.path.getsize(sys.argv[2]) // 1024} KB")
