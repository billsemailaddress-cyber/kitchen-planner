# Kitchen Planner

To-scale kitchen remodel planner PWA for iPad.

## Local development

Serve over HTTP (do not use `file://` for install/PWA testing):

```bash
python3 -m http.server 8765
```

Open http://localhost:8765/

## Files

- `index.html` — app shell and planner
- `manifest.webmanifest` — PWA manifest
- `sw.js` — offline service worker
- `icons/` — app icons
- `scripts/gen-icons.py` — regenerate icons
