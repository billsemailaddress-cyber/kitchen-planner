# Kitchen Planner — iPad Home Screen PWA Design

**Date:** 2026-07-14  
**Status:** Draft for review (parity + UX/visual polish)  
**Source of truth:** Claude artifact `0b958352-c8eb-49db-9f7a-3dda547defbe` / Desktop `Kitchen Planner.html`

## Problem

The Kitchen Remodel Planner exists as a Claude artifact and a single HTML file. It already has most mobile meta tags, but it is not a true installable, offline Home Screen app. On iPad it also feels like a dense desktop tool: small chips, sparse empty states, functional (not beautiful) cabinet drawing, and little guidance for first-time use.

## Decision

Ship as a **Progressive Web App (PWA)** installable from **Safari → Add to Home Screen**, with:

1. **Local project** on the Mac (`~/kitchen-planner/`) for development and backup  
2. **Hosted URL** (GitHub Pages or equivalent) so the iPad can open and install it anytime  
3. **UX + visual enhancements** layered on the existing planner so it is easier and more appealing on iPad — without abandoning the proven interaction model

## Goals

- Feature parity with the existing Kitchen Planner (no regressions)
- Full-screen standalone display on iPad (no Safari chrome when launched from Home Screen)
- Works offline after first successful load
- Own Home Screen name and icon (“Kitchen Planner”)
- Save/Open JSON and localStorage behavior preserved
- Light/dark appearance preserved and refined
- **Easier to use** on touch: larger targets, clearer modes, first-run guidance, safer destructive actions
- **More graphically appealing**: richer plan graphics, polished chrome, finish themes, better empty states

## Non-goals

- App Store / native Swift or SwiftUI shell
- Cloud sync or multi-user accounts
- Full BIM / photoreal CAD
- Android-first packaging (Android may work via Chrome install; iPad Safari is the target)
- Backend pricing engines or supplier catalogs

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
| `index.html` | Full planner UI + logic (from Desktop HTML) + polish layers | Canvas 2D only; no CDN required |
| `manifest.webmanifest` | Name, icons, `display: standalone`, theme colors | Icons |
| `sw.js` | Cache-first offline shell for app files | Manifest + index + icons |
| `icons/*` | Apple touch + maskable PWA icons | Generated brand mark |
| Host (GitHub Pages) | HTTPS origin required for SW + reliable install | Repo + Pages config |
| README | Mac run steps + iPad install steps | Host URL once deployed |

### Data

- **In-browser state:** `localStorage` (existing planner behavior)
- **Portable plans:** JSON Save / Open (existing; version field if needed for migrate)
- **New optional fields** (backward compatible): plan `name`, `finishTheme`, item `finish` if themed
- **No server-side data store**

### Offline model

Service worker precaches:

- `/` or `/index.html`
- `/manifest.webmanifest`
- `/icons/*` (listed explicitly)

Strategy: **cache-first** for shell assets. User JSON files are not SW-cached.

### Install model (iPad)

1. Open hosted HTTPS URL in **Safari**
2. Share → **Add to Home Screen**
3. Launch icon → standalone full-screen
4. Subsequent use works offline if SW registered successfully on first load

---

## Feature parity checklist (must not regress)

- [ ] Room dimensions (ft/in)
- [ ] Draw walls, wall thickness, pen tools
- [ ] Base / sink / wall cabinets, tall/pantry, appliances
- [ ] Doors, windows, utility pins, custom pieces
- [ ] 2D plan + 3D view
- [ ] Drag, snap, rotate, delete, multi-select, island group/ungroup
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

---

## Enhancements (easier + more appealing)

Prioritized for iPad. All are **in-scope** for v1 unless marked later.

### A. iPad usability

| Enhancement | Why |
|-------------|-----|
| **Larger touch targets** | Chips, top-bar buttons, zoom ± at ≥44×44pt |
| **iPad landscape layout** | Keep 3-column layout on typical iPad landscape; drawers only when truly narrow |
| **Floating action cluster** | Sticky rotate / duplicate / delete near selection or as stage toolbar (no keyboard required) |
| **On-canvas rotate control** | Tap corner handle or floating “Rotate 90°” so R-key is optional |
| **Safe-area padding** | Respect `env(safe-area-inset-*)` for notch / home indicator / Home Screen mode |
| **Mode clarity** | Active mode chip (Select / Draw walls / Box select) with strong highlight + short hint text |
| **Confirm destructive actions** | Reset, delete multi-select, replace-on-open — short confirm sheet |
| **Toast feedback** | Brief “Saved”, “Opened plan”, “Grouped as island”, “Undo” toasts |
| **Plan name field** | Editable name in top bar; used in print header and default save filename |
| **Room shape presets** | One-tap start: Rectangle, L-shape, Galley, U-shape (still fully editable after) |
| **First-run coach marks** | 3-step dismissible overlay: add piece → drag/rotate → check triangle / build list |
| **Copy build list** | One-tap copy table as TSV/plain text for Messages / Notes / email |

### B. Visual design (chrome)

| Enhancement | Why |
|-------------|-----|
| **Refined design system** | Softer surfaces, clearer hierarchy, improved type scale, slightly rounder controls, subtle shadows |
| **Branded empty states** | Illustrated “drop a cabinet” / “empty build list” instead of italic-only placeholders |
| **Palette cards** | Category sections with color swatches; appliance chips show mini glyph (fridge, range, DW) |
| **Segmented controls polish** | 2D/3D and mode toggles feel more native (pill segments, pressed states) |
| **Print stylesheet** | Cleaner print/PDF: plan title, date, scale note, build list page break |
| **App icon + splash colors** | Distinct kitchen-plan mark; theme-color matches shell |

### C. Canvas graphics (2D / 3D)

| Enhancement | Why |
|-------------|-----|
| **Richer cabinet drawing** | Subtle countertop strip on base/island, door split lines, sink bowl oval, appliance face details (fridge line, range burners) |
| **Finish themes** | 4–5 global themes (e.g. Natural Oak, White Shaker, Walnut, Soft Gray, Navy) recolor category fills consistently; stored on plan |
| **Selection glow + dim others** | Selected piece pops; optional slight dim of non-selected when something is selected |
| **Snap guides** | When snapping, draw light cyan/magenta alignment lines (like design tools) |
| **Work triangle visualization** | When sink + cook + fridge present, draw soft triangle on plan with length labels |
| **Improved 3D** | Slightly better materials (counter vs body), soft floor grid, gentler lighting tints; keep pure canvas (no Three.js dependency) |
| **Live dimension badges** | Clearer pill labels with better contrast in light and dark |

### D. Nice-to-have if time (still allowed, lower priority)

- Haptic-style pulse animation on place/snap  
- “Duplicate plan” (clone state to a new named plan in localStorage list — multi-plan switcher)  
- CSV export of build list  
- Accessibility: larger Dynamic Type-friendly panel text where possible  

### Explicitly out of enhancement scope

- AR room scan  
- Real product SKUs / pricing  
- Multiplayer collaboration  
- Photoreal rendering engines  

---

## Project layout

```
kitchen-planner/
  index.html
  manifest.webmanifest
  sw.js
  icons/
    icon-180.png
    icon-192.png
    icon-512.png
  docs/superpowers/specs/
    2026-07-14-kitchen-planner-pwa-design.md
  README.md
```

Logic stays single-file HTML for offline simplicity and easy hosting. CSS/JS may be split only if the file becomes unmaintainable; prefer one `index.html` for v1.

## Implementation approach

1. Copy Desktop `Kitchen Planner.html` → `index.html` as baseline  
2. PWA shell: manifest, SW registration, icons, safe-area meta  
3. Visual design system pass (CSS variables, top bar, panels, chips)  
4. Touch / iPad UX: targets, stage action bar, confirms, toasts, plan name  
5. Canvas polish: cabinet details, finish themes, selection, snap guides, work triangle draw  
6. Room presets + first-run coach marks  
7. Print stylesheet + copy build list  
8. README + local serve instructions  
9. Deploy GitHub Pages; smoke-test install + offline + parity  

## Hosting choice

**Primary:** GitHub Pages from `main` (site root).

- If `gh` authenticated: create repo + enable Pages  
- Else: document manual push + Pages setup; local package still complete  

Fallback: Netlify static drop.

## Success criteria

- Safari on iPad: full planner + Add to Home Screen → standalone  
- Offline after first visit  
- Parity checklist all pass  
- Enhancements A–C shipped at a quality bar that feels intentional (not half-styled)  
- New/old plan JSON both open (migrate unknown fields safely)  
- Local static server works on Mac  

## Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Polish bloat breaks core tools | Ship parity baseline first; enhance in layers; keep undo on all mutations |
| Canvas drawing too heavy | Cap detail level; no images required for cabinet glyphs |
| iOS SW quirks | Simple cache name versioning; root scope |
| `file://` no SW | Always document HTTPS/localhost serve |
| Finish themes break saved colors | Themes apply as defaults; per-item override only if already present |

## Decisions logged

- Delivery: **local + hosted (option C)**  
- Packaging: **PWA Home Screen**, not native shell  
- Scope: **parity + usability/visual enhancements** (this revision)  
