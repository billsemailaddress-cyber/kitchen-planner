# Kitchen Planner

To-scale kitchen remodel planner PWA, built for iPad (works in desktop browsers too). Draw a room, place cabinets and appliances, check work-triangle clearances, apply finish themes, and export or print the plan.

## Features

- Scale floor plan with base/wall cabinets, island, sink, range, fridge, dishwasher
- Touch-first UI: stage rotate / duplicate / delete (no keyboard required)
- Room presets, plan name, finish themes (e.g. White Shaker)
- Snap guides, work triangle, clearance panel
- Save / open JSON backup; print-friendly plan + title
- Offline shell via service worker after first visit
- Installable PWA (Add to Home Screen on iPad)

## Local development

Serve over HTTP (do not use `file://` — PWA install and service workers need a proper origin):

```bash
cd kitchen-planner
python3 -m http.server 8765
```

Open [http://localhost:8765](http://localhost:8765).

Any static server works (`npx serve`, Caddy, nginx, etc.) as long as it serves the repo root.

## Install on iPad

1. Open the **hosted** URL (or your LAN URL) in **Safari**.
2. Tap **Share** → **Add to Home Screen**.
3. Launch from the home screen icon for standalone display.

## Offline

After the first successful load, the service worker caches the app shell (`index.html`, manifest, icons). You can reopen the app without network for viewing and editing the plan already on the device.

Plans are stored in the browser’s local storage (`kitchenPlan_v1`). iOS may clear site data under storage pressure — treat cloud/JSON export as backup (below).

## JSON backup

Use **Save JSON** / **Open JSON** in the app to export and re-import your plan.

- Keep a copy in Files, email, or cloud drive if you remodel over many sessions.
- JSON is the portable backup if Safari purges local storage.

## Deploy (GitHub Pages)

### From this repo

1. Push `main` to GitHub (remote `origin`).
2. In the repo: **Settings → Pages**.
3. Source: **Deploy from a branch** → branch **`main`** → folder **`/` (root)**.
4. Save. After a minute or two the site is at:

   `https://<owner>.github.io/kitchen-planner/`

The empty `.nojekyll` file tells Pages to serve files as-is (no Jekyll processing).

### Create repo + push (if not done yet)

```bash
gh auth status
gh repo create kitchen-planner --public --source=. --remote=origin --push
```

Then enable Pages as above (branch `main`, root). CLI Pages API may require workflow/build_type depending on account; the Settings UI is reliable.

### Manual push without `gh`

```bash
git remote add origin https://github.com/<owner>/kitchen-planner.git
git push -u origin main
```

Then enable Pages from branch `main` / root in the GitHub UI.

## Project layout

| Path | Role |
|------|------|
| `index.html` | App shell and planner logic |
| `manifest.webmanifest` | PWA manifest |
| `sw.js` | Offline service worker (`kitchen-planner-vN` cache) |
| `icons/` | App icons (180 / 192 / 512) |
| `scripts/gen-icons.py` | Regenerate icons |
| `.nojekyll` | Disable Jekyll on GitHub Pages |

## Smoke checklist

| Check | Expected |
|-------|----------|
| Load app | UI + canvas |
| Place base 36, rotate via stage button | Works without keyboard |
| Finish theme White Shaker | Colors update |
| Sink + range + fridge | Triangle + clearance panel |
| Save / open JSON | Round-trip |
| Print | Title + plan |
| SW | Cached offline after first visit |
| Coach once | Shows then never again |

## License

Use and modify for personal remodel planning as you like.
