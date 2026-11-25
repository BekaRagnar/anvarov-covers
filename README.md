# anvarov-covers

Square 1080×1080 covers for the Telegram channel @anvarov_si.
Covers live in `YYYY-MM-DD/` folders; raw link:
`https://raw.githubusercontent.com/BekaRagnar/anvarov-covers/main/YYYY-MM-DD/<file>.png`

## Generate

```bash
python3 scripts/make_square.py cover.json out.png
```

```json
{
  "tag": "Yangi model",
  "title": "Gemini 4 Carbon endi hamma uchun ochiq",
  "accent": "#4C8DFF",
  "date": "21.11.2026",
  "scene": {"type": "chat", "app": "Gemini 4 Carbon", "items": []}
}
```

Animated version (silent looping MP4 for Telegram sendAnimation, ~60–180 KB):

```bash
python3 scripts/make_anim.py cover.json out.mp4 [seconds=7]
```

Use the jsDelivr link with the commit SHA for MP4 (it serves `video/mp4`; raw.githubusercontent serves `application/octet-stream`):
`https://cdn.jsdelivr.net/gh/BekaRagnar/anvarov-covers@<SHA>/YYYY-MM-DD/<file>.mp4`

Scene types (`scene.items`):

| type | items |
|---|---|
| `chat` | `[{"role": "user"|"ai", "text": "..."}]` — 2–4 messages |
| `code` | `["line 1", "line 2", ...]` — up to 12 code lines; `app` = file name |
| `settings` | `[{"label": "...", "hint": "...", "value": true/false | 0.0–1.0 | "text"}]` — up to 5 |
| `image` | `["prompt text", "chip1", "chip2", "chip3", "chip4"]` — prompt bar + 4 tiles |
| `voice` | `["transcript line", "result line"]` |
| `stats` | `[{"label": "...", "value": 88.4, "text": "88.4", "highlight": true}]` — up to 5 bars |

Rules: no logos, no real faces; tool and model names only as plain text.

## Slideshow post (Rich Message)

Queue job `"kind": "slideshow"` with `"media": [PNG paths]` and plain `"caption"`: the script sends `sendRichMessage`
(first caption line in bold → swipeable `<tg-slideshow>` → rest of the text). If Telegram rejects it, the same post
goes out as an album; the result has `"sent_as": "slideshow"|"album"` and `"slideshow_error"`.

## Carousel (album)

```bash
python3 scripts/make_carousel.py carousel.json YYYY-MM-DD/HHMM_slug/
```
`carousel.json` = cover fields + `"slides": [{"title", "text", "bullets": [...], "prompt"}]` (up to 9 slides).
Writes `01.png` (cover) + `02.png`… Send with a queue job of `"kind": "album"` and `"media": [list of PNG paths]`.

## Video/animation posts (GitHub Actions)

Zapier cannot send video to Telegram, so MP4 posts go through `.github/workflows/telegram.yml`.
Requires the repository secret `TELEGRAM_BOT_TOKEN` (Settings → Secrets and variables → Actions).

1. Commit the MP4 and `queue/<YYYY-MM-DD>_<HHMM>_<slug>.json`:
   `{"chat_id": "@anvarov_si", "kind": "animation", "media": "YYYY-MM-DD/HHMM_slug.mp4", "caption": "..."}`
2. Push to main. The workflow sends it and commits `queue/<same name>.result.json`:
   `{"ok": true, "message_id": 47, "link": "https://t.me/anvarov_si/47"}` or `{"ok": false, "error": "..."}`
3. Poll `git pull` (or the raw URL) for the result file, usually 20–60 s.
