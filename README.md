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
