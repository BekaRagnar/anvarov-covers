"""Send queued posts to Telegram (run by GitHub Actions).

For every queue/*.json that has no matching queue/*.result.json yet:
  {"chat_id": "@anvarov_si", "kind": "animation"|"video"|"photo",
   "media": "2026-11-24/1130_slug.mp4", "caption": "..."}
sends the file from the repo via the Bot API and writes <name>.result.json:
  {"ok": true, "message_id": 47, "link": "https://t.me/anvarov_si/47"} or
  {"ok": false, "error": "..."}
The token comes from the TELEGRAM_BOT_TOKEN secret only.
"""
import glob
import json
import os
import subprocess
import sys

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
METHODS = {"animation": ("sendAnimation", "animation"),
           "video": ("sendVideo", "video"),
           "photo": ("sendPhoto", "photo")}


def send(job):
    kind = job.get("kind", "animation")
    if kind not in METHODS:
        return {"ok": False, "error": f"unknown kind {kind}"}
    if not TOKEN:
        return {"ok": False, "error": "secret TELEGRAM_BOT_TOKEN is not set"}
    media = job["media"]
    if not os.path.isfile(media):
        return {"ok": False, "error": f"file not found: {media}"}
    method, field = METHODS[kind]
    cap = "/tmp/caption.txt"
    with open(cap, "w", encoding="utf-8") as f:
        f.write(job.get("caption", ""))
    cmd = ["curl", "-sS", "--max-time", "120",
           f"https://api.telegram.org/bot{TOKEN}/{method}",
           "--form-string", f"chat_id={job.get('chat_id', '@anvarov_si')}",
           "-F", f"{field}=@{media}",
           "-F", f"caption=<{cap}"]
    if kind == "video":
        cmd += ["--form-string", "supports_streaming=true"]
    out = subprocess.run(cmd, capture_output=True, text=True)
    try:
        r = json.loads(out.stdout)
    except ValueError:
        return {"ok": False, "error": (out.stderr or out.stdout)[:300].replace(TOKEN, "***")}
    if not r.get("ok"):
        return {"ok": False, "error": str(r.get("description", r))[:300]}
    msg = r["result"]
    chat = msg.get("chat", {})
    res = {"ok": True, "message_id": msg["message_id"]}
    if chat.get("username"):
        res["link"] = f"https://t.me/{chat['username']}/{msg['message_id']}"
    return res


def main():
    done = 0
    for path in sorted(glob.glob("queue/*.json")):
        if path.endswith(".result.json"):
            continue
        result_path = path[:-5] + ".result.json"
        if os.path.exists(result_path):
            continue
        try:
            job = json.load(open(path, encoding="utf-8"))
            res = send(job)
        except Exception as e:  # noqa: BLE001
            res = {"ok": False, "error": f"{type(e).__name__}: {e}"[:300]}
        json.dump(res, open(result_path, "w", encoding="utf-8"), ensure_ascii=False)
        print(path, "->", json.dumps(res, ensure_ascii=False))
        done += 1
    print("processed", done)


if __name__ == "__main__":
    sys.exit(main())
