# Kitchen Planner — iPad Home Screen PWA Design

**Date:** 2026-07-14  
**Status:** Approved for implementation (delivery: local package + hosted URL)  
**Source of truth:** Claude artifact `0b958352-c8eb-49db-9f7a-3dda547defbe` / Desktop `Kitchen Planner.html`

## Problem

The Kitchen Remodel Planner exists as a Claude artifact and a single HTML file. It already has most mobile meta tags, but it is not a true installable, offline Home Screen app. The goal is a **standalone-feeling iPad experience** without App Store or a native rewrite.

## Decision

Ship as a **Progressive Web App (PWA)** installable from **Safari → Add to Home Screen**, with:

1. **Local project** on the Mac (`~/kitchen-planner/`) for development and backup  
2. **Hosted URL** (GitHub Pages or equivalent) so the iPad can open and install it anytime  

## Goals

- Feature parity with the existing Kitchen Planner (no feature rewrite)
- Full-screen standalone display on iPad (no Safari chrome when launched from Home Screen)
- Works offline after first successful load
- Own Home Screen name and icon (“Kitchen Planner”)
- Save/Open JSON and localStorage behavior preserved
- Light/dark appearance preserved

## Non-goals

- App Store / native Swift or SwiftUI shell
- Cloud sync or multi-user accounts
- New kitchen-planning features beyond the current artifact
- Android-first packaging (Android may work via Chrome install; iPad Safari is the target)

## Architecture

```
Browser (Safari on iPad)
    │
    ├─ first visit (HTTPS host)
    │     loads index.html + assets
    │     registers service worker
    │     caches app shell
    │
    └─ Home Screen launch (display: standalone)
          serves from cache when offline
          app state in localStorage + optional JSON export/import
```

### Components

| Unit | Responsibility | Depends on |
|------|----------------|------------|
| `index.html` | Full planner UI + logic (ported from Desktop HTML) | Canvas 2D only; no CDN required |
| `manifest.webmanifest` | Name, icons, `display: standalone`, theme colors | Icons |
| `sw.js` | Cache-first offline shell for app files | Manifest + index + icons |
| `icons/*` | Apple touch + maskable PWA icons | Generated from a simple brand mark |
| Host (GitHub Pages) | HTTPS origin required for SW + reliable install | Repo + Pages config |
| README | Mac run steps + iPad install steps | Host URL once deployed |

### Data

- **In-browser state:** `localStorage` (existing planner behavior)
- **Portable plans:** JSON Save / Open (existing)
- **No server-side data store**

### Offline model

Service worker precaches:

- `/` or `/index.html`
- `/manifest.webmanifest`
- `/icons/*` (listed explicitly)

Strategy: **cache-first** for those shell assets; network is unused for core app after install. Plan JSON files opened by the user are not cached by the SW (user-driven file picker).

### Install model (iPad)

1. Open hosted HTTPS URL in **Safari**
2. Share → **Add to Home Screen**
3. Launch icon → standalone full-screen
4. Subsequent use works offline if SW registered successfully on first load

## Feature parity checklist (must not regress)

From the live artifact / Desktop HTML:

- [ ] Room dimensions (ft/in)
- [ ] Draw walls, wall thickness, pen tools
- [ ] Base / sink / wall cabinets, tall/pantry, appliances
- [ ] Doors, windows, utility pins, custom pieces
- [ ] 2D plan + 3D view
- [ ] Drag, snap, rotate (R), delete, multi-select, island group/ungroup
- [ ] Selected item inspector (exact size/position)
- [ ] Clearances & work triangle metrics
- [ ] Build list
- [ ] Undo / redo
- [ ] Fit, zoom (+/−), pinch
- [ ] Print / PDF
- [ ] Save file / Open file (JSON)
- [ ] Reset
- [ ] Touch layout: Parts / Details drawers on narrow widths
- [ ] Light/dark theme CSS

## Project layout

```
kitchen-planner/
  index.html
  manifest.webmanifest
  sw.js
  icons/
    icon-180.png          # apple-touch-icon
    icon-192.png
    icon-512.png
  docs/superpowers/specs/
    2026-07-14-kitchen-planner-pwa-design.md
  README.md
```

Optional later: `docs/superpowers/plans/` implementation plan if multi-session work needs it.

## Implementation approach

1. Copy Desktop `Kitchen Planner.html` → `index.html`
2. Add/adjust PWA head tags:
   - link `manifest`
   - `apple-touch-icon`
   - ensure `apple-mobile-web-app-capable` / title / theme-color
3. Register service worker at end of `index.html` (HTTPS/localhost only)
4. Implement minimal `sw.js` (install + activate + fetch cache-first)
5. Create simple brand icons (cabinet/grid mark, dark teal accent matching UI)
6. README: local `python3 -m http.server` / `npx serve`, and iPad install steps
7. Initialize git repo; deploy to **GitHub Pages** from `main` (root or `/docs` — prefer root)
8. Smoke-test: load, install meta present, offline after cache, open a saved plan JSON

## Hosting choice

**Primary:** GitHub Pages from a public or private repo the user owns.

- If GitHub CLI/`gh` is available and authenticated: create repo + enable Pages
- If not: document manual “create repo → push → enable Pages” and leave local package complete either way

Fallback host (only if Pages blocked): Netlify drop or similar static host — same static files.

## Success criteria

- Opening the hosted URL in Safari on iPad shows the full planner
- Add to Home Screen yields icon named **Kitchen Planner** and opens without browser UI
- Airplane mode (after prior visit) still loads the app shell
- All parity checklist items work as in the Desktop HTML
- Local clone runs via any static file server on the Mac

## Risks & mitigations

| Risk | Mitigation |
|------|------------|
| iOS Safari PWA quirks (SW scope, cache) | Keep SW simple; same-origin root scope; version cache name |
| `file://` cannot register SW | Never rely on double-click HTML; always serve over http(s) |
| localStorage cleared by iOS | Keep Save file JSON as backup path; document it |
| Icon looks generic | Ship dedicated 180/192/512 assets, not browser default |

## Open items resolved in design

- Delivery: **local + hosted (option C)**
- Packaging: **PWA Home Screen**, not native shell
- Scope: **parity only**, no new planner features
