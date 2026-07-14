# Kitchen Planner iPad PWA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship an offline-capable Kitchen Remodel Planner PWA (local package + GitHub Pages) with full feature parity to Desktop `Kitchen Planner.html` plus iPad UX and visual polish.

**Architecture:** Single-origin static site: enhanced `index.html` (app logic + UI), `manifest.webmanifest`, `sw.js`, and PNG icons. No backend. State in `localStorage` + JSON import/export. Service worker cache-first for the app shell.

**Tech Stack:** Vanilla HTML/CSS/JS, Canvas 2D, Web App Manifest, Service Worker, static hosting (GitHub Pages). No npm runtime dependencies required for the app itself.

## Global Constraints

- Source baseline: `/Users/rockmystic/Desktop/Kitchen Planner.html` (copy, then enhance — do not leave the Desktop file as the only copy)
- Project root: `/Users/rockmystic/kitchen-planner/`
- Units remain **inches** internally (existing model)
- Offline after first HTTPS/localhost load; never rely on `file://` for install
- JSON migrate must open old `kitchenPlan_v1` saves without data loss
- No CDN dependencies (all offline)
- iPad Safari is primary target; desktop browsers secondary
- Spec: `docs/superpowers/specs/2026-07-14-kitchen-planner-pwa-design.md`

## File map

| File | Responsibility |
|------|----------------|
| `index.html` | Entire planner: CSS design system, markup, canvas logic, enhancements |
| `manifest.webmanifest` | PWA name, icons, `display: standalone`, theme |
| `sw.js` | Precache + cache-first fetch |
| `icons/icon-180.png` | Apple touch icon |
| `icons/icon-192.png` | Manifest icon |
| `icons/icon-512.png` | Manifest / maskable-ish large icon |
| `README.md` | Local serve + iPad install + deploy notes |
| `scripts/gen-icons.py` | One-shot icon generator (Pillow or pure struct PNG) |

---

### Task 1: Baseline app + PWA shell

**Files:**
- Create: `index.html` (copy from Desktop)
- Create: `manifest.webmanifest`
- Create: `sw.js`
- Create: `scripts/gen-icons.py`
- Create: `icons/icon-180.png`, `icons/icon-192.png`, `icons/icon-512.png`
- Create: `README.md` (minimal; expand in Task 6)

**Interfaces:**
- Produces: App loads at `/` with SW registration; `navigator.serviceWorker.register('/sw.js')` when secure context
- Produces: Manifest linked as `/manifest.webmanifest`

- [ ] **Step 1: Copy baseline**

```bash
cp "/Users/rockmystic/Desktop/Kitchen Planner.html" /Users/rockmystic/kitchen-planner/index.html
```

- [ ] **Step 2: Add head tags** in `index.html` `<head>` after existing meta tags:

```html
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/icon-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Kitchen Planner">
<meta name="theme-color" content="#14181B" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#E9ECEF" media="(prefers-color-scheme: light)">
```

- [ ] **Step 3: Create `manifest.webmanifest`**

```json
{
  "name": "Kitchen Planner",
  "short_name": "Kitchen Planner",
  "description": "To-scale kitchen remodel planner for iPad",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "orientation": "any",
  "background_color": "#14181B",
  "theme_color": "#14181B",
  "icons": [
    { "src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" }
  ]
}
```

- [ ] **Step 4: Create `sw.js`**

```js
const CACHE = "kitchen-planner-v1";
const ASSETS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icons/icon-180.png",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request).then((hit) => {
      if (hit) return hit;
      return fetch(e.request).then((res) => {
        const copy = res.clone();
        if (res.ok && new URL(e.request.url).origin === self.location.origin) {
          caches.open(CACHE).then((c) => c.put(e.request, copy));
        }
        return res;
      }).catch(() => caches.match("./index.html"));
    })
  );
});
```

- [ ] **Step 5: Register SW** at end of `index.html` (before `</body>`):

```html
<script>
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {});
  });
}
</script>
```

- [ ] **Step 6: Generate icons** with `scripts/gen-icons.py` — draw a dark rounded square, teal accent “floor plan” L-shape + counter rectangle using Pillow if available, else write minimal valid PNGs via a small pure-Python PNG writer or `sips`/`qlmanage`. Target colors: bg `#1B2024`, accent `#6AA6D9`, warm wood `#C6893F`. Output 180, 192, 512.

```bash
cd /Users/rockmystic/kitchen-planner && python3 scripts/gen-icons.py
# Expected: icons/icon-180.png, icon-192.png, icon-512.png exist and are non-empty
```

- [ ] **Step 7: Smoke-test locally**

```bash
cd /Users/rockmystic/kitchen-planner && python3 -m http.server 8765
# In browser: http://localhost:8765/
# Expected: planner UI loads; Application > Service Workers shows registered; manifest present
```

- [ ] **Step 8: Commit**

```bash
cd /Users/rockmystic/kitchen-planner
git add index.html manifest.webmanifest sw.js icons scripts/gen-icons.py README.md
git commit -m "feat: baseline Kitchen Planner with PWA shell and offline SW"
```

---

### Task 2: Design system + iPad chrome

**Files:**
- Modify: `index.html` (CSS `:root`, topbar, sides, chips, drawers, safe-area)

**Interfaces:**
- Consumes: Existing class names (`.app`, `.topbar`, `.chip`, `.btn`, `.side`, etc.)
- Produces: CSS variables for radius, touch min-size, safe insets; finish theme hooks `--finish-base` etc. (defaults match current CAT colors)

- [ ] **Step 1: Extend `:root` variables** (after existing color tokens):

```css
:root{
  /* existing colors remain */
  --radius:10px;
  --radius-sm:7px;
  --touch:44px;
  --pad-safe-t:env(safe-area-inset-top,0px);
  --pad-safe-b:env(safe-area-inset-bottom,0px);
  --pad-safe-l:env(safe-area-inset-left,0px);
  --pad-safe-r:env(safe-area-inset-right,0px);
  --font-ui: -apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",system-ui,sans-serif;
  --finish-base:#C6893F;
  --finish-wall:#E0C088;
  --finish-tall:#8A5A34;
  --finish-appliance:#7E8C99;
  --finish-sink:#5B8CA6;
  --finish-island:#B9762F;
  --finish-counter:#E8E2D6;
}
body{
  font-family:var(--font-ui);
  padding: var(--pad-safe-t) var(--pad-safe-r) var(--pad-safe-b) var(--pad-safe-l);
}
.btn,.chip,.zoombar button,.drawerToggle{
  min-height:var(--touch);
  min-width:var(--touch);
}
.chip{ padding:8px 12px; border-radius:var(--radius-sm); }
.btn{ border-radius:var(--radius-sm); padding:8px 14px; }
.topbar{ padding:10px 16px; gap:10px; }
.side .grp h2{ letter-spacing:.12em; }
```

- [ ] **Step 2: iPad breakpoint** — keep 3 columns until width &lt; 900px (not 860 only); drawers for phone/portrait narrow:

```css
@media (max-width:900px){
  .drawerToggle{display:inline-flex}
  .cols{grid-template-columns:1fr}
  /* existing fixed drawer rules from baseline */
}
@media (min-width:901px){
  .cols{grid-template-columns:240px 1fr 300px}
  .drawerToggle{display:none}
}
```

- [ ] **Step 3: Toast + modal CSS**

```css
.toast-host{position:fixed;left:50%;bottom:calc(24px + var(--pad-safe-b));transform:translateX(-50%);z-index:50;display:flex;flex-direction:column;gap:8px;pointer-events:none}
.toast{background:var(--panel);border:1px solid var(--border);box-shadow:var(--shadow);padding:10px 16px;border-radius:10px;font-size:13px;opacity:0;transition:opacity .2s}
.toast.show{opacity:1}
.modal-scrim{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:40;display:none;align-items:center;justify-content:center;padding:20px}
.modal-scrim.open{display:flex}
.modal{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:18px;max-width:360px;width:100%;box-shadow:var(--shadow)}
.modal h3{margin:0 0 8px;font-size:16px}
.modal p{margin:0 0 14px;color:var(--muted);font-size:13px}
.modal .row{display:flex;gap:8px;justify-content:flex-end}
```

- [ ] **Step 4: Markup hosts** before closing `</div>` of `.app`:

```html
<div class="toast-host" id="toastHost"></div>
<div class="modal-scrim" id="confirmModal" role="dialog" aria-modal="true">
  <div class="modal">
    <h3 id="confirmTitle">Confirm</h3>
    <p id="confirmMsg"></p>
    <div class="row">
      <button class="btn ghost" id="confirmCancel">Cancel</button>
      <button class="btn primary" id="confirmOk">OK</button>
    </div>
  </div>
</div>
```

- [ ] **Step 5: JS helpers** near top of script after utilities:

```js
function toast(msg, ms=2200){
  const host=document.getElementById("toastHost");
  const el=document.createElement("div");
  el.className="toast"; el.textContent=msg;
  host.appendChild(el);
  requestAnimationFrame(()=>el.classList.add("show"));
  setTimeout(()=>{el.classList.remove("show"); setTimeout(()=>el.remove(),250);}, ms);
}
function confirmAsync(title, msg, okLabel="OK"){
  return new Promise((resolve)=>{
    const m=document.getElementById("confirmModal");
    document.getElementById("confirmTitle").textContent=title;
    document.getElementById("confirmMsg").textContent=msg;
    document.getElementById("confirmOk").textContent=okLabel;
    m.classList.add("open");
    const done=(v)=>{ m.classList.remove("open"); cleanup(); resolve(v); };
    const ok=()=>done(true), cancel=()=>done(false);
    const cleanup=()=>{
      document.getElementById("confirmOk").removeEventListener("click",ok);
      document.getElementById("confirmCancel").removeEventListener("click",cancel);
    };
    document.getElementById("confirmOk").addEventListener("click",ok);
    document.getElementById("confirmCancel").addEventListener("click",cancel);
  });
}
```

- [ ] **Step 6: Wire Reset** to confirm — replace direct reset handler with:

```js
document.getElementById("btnReset").addEventListener("click", async ()=>{
  if(!(await confirmAsync("Reset plan?","This clears the room, cabinets, and openings. This cannot be undone from history after reset.","Reset"))) return;
  state=migrate(DEFAULT()); sel=null; selIds.clear(); undoStack=[]; redoStack=[]; _snap=null;
  autoFit=true; syncRoomInputs(); buildPalette(); updateProps(); updateClear(); updateBuild(); fit2D(); render(); save();
  toast("Plan reset");
});
```

(Adjust to match existing reset implementation’s exact body; wrap with confirm.)

- [ ] **Step 7: Commit**

```bash
git add index.html
git commit -m "feat: iPad design system, safe areas, toasts, and confirms"
```

---

### Task 3: Plan name, modes, stage actions, presets, coach

**Files:**
- Modify: `index.html` (topbar HTML + JS)

**Interfaces:**
- Produces: `state.name` string (default `"Untitled kitchen"`)
- Produces: `state.finishTheme` string key (default `"oak"`)
- Produces: `applyRoomPreset(kind)` where `kind` is `"rect"|"l"|"galley"|"u"`
- Produces: floating `#stageActions` with Rotate / Duplicate / Delete buttons

- [ ] **Step 1: Extend DEFAULT + migrate**

```js
const DEFAULT = ()=>({
  name:"Untitled kitchen",
  finishTheme:"oak",
  units:"ftin",
  room:{w:144,d:120},
  thickness:4.5,
  walls:rectWalls(144,120),
  items:[],
  openings:[
    {id:uid(),kind:"door",wallId:"w-bottom",offset:40,width:32},
    {id:uid(),kind:"window",wallId:"w-top",offset:54,width:36},
  ],
  cam:{yaw:-0.62,pitch:0.98,zoom:1},
  view:"2d",
});
function migrate(st){
  if(!st) return st;
  if(!st.name) st.name="Untitled kitchen";
  if(!st.finishTheme) st.finishTheme="oak";
  // ... keep existing room/walls/openings migration ...
  return st;
}
```

- [ ] **Step 2: Topbar plan name + presets + finish select** — insert after brand:

```html
<input class="plan-name" id="planName" type="text" maxlength="60" aria-label="Plan name" value="Untitled kitchen">
<select id="finishTheme" class="btn" title="Cabinet finish theme" aria-label="Finish theme">
  <option value="oak">Natural Oak</option>
  <option value="shaker">White Shaker</option>
  <option value="walnut">Walnut</option>
  <option value="gray">Soft Gray</option>
  <option value="navy">Navy</option>
</select>
<select id="roomPreset" class="btn" title="Room shape preset" aria-label="Room preset">
  <option value="">Room shape…</option>
  <option value="rect">Rectangle</option>
  <option value="l">L-shape</option>
  <option value="galley">Galley</option>
  <option value="u">U-shape</option>
</select>
```

CSS for `.plan-name`: borderless/underlined input, font-weight 600, max-width 160px.

- [ ] **Step 3: Mode indicator** — update `setMode` to set classes on `#penBtn` / `#selectBtn` and a small `#modePill` text: `Select` | `Draw walls` | `Box select`.

- [ ] **Step 4: Stage action bar** inside `#stage`:

```html
<div class="stage-actions" id="stageActions" hidden>
  <button class="btn" id="actRotate" type="button">Rotate</button>
  <button class="btn" id="actDup" type="button">Duplicate</button>
  <button class="btn danger" id="actDel" type="button">Delete</button>
</div>
```

```css
.stage-actions{
  position:absolute; left:50%; top:12px; transform:translateX(-50%);
  display:flex; gap:8px; z-index:6;
  background:var(--panel); border:1px solid var(--border); border-radius:12px;
  padding:6px; box-shadow:var(--shadow);
}
```

Wire: `actRotate` → `rotateSelection()`, `actDup` → `duplicateSelection()`, `actDel` → confirm if multi then `deleteSelection()`. Show `#stageActions` when `selIds.size>0` or `sel` set; hide otherwise. Call from `select` / `selectItem` / `updateProps`.

- [ ] **Step 5: Room presets**

```js
function applyRoomPreset(kind){
  const T=state.thickness||4.5;
  if(kind==="rect"){
    state.room={w:144,d:120};
    state.walls=rectWalls(144,120);
  }else if(kind==="l"){
    // outer 14' x 12' L: full rect walls minus inner cut — represent as polyline walls
    const W=168, D=144, cutW=84, cutD=72;
    state.room={w:W,d:D};
    state.walls=[
      {id:uid(),a:{x:0,y:0},b:{x:W,y:0}},
      {id:uid(),a:{x:W,y:0},b:{x:W,y:cutD}},
      {id:uid(),a:{x:W,y:cutD},b:{x:cutW,y:cutD}},
      {id:uid(),a:{x:cutW,y:cutD},b:{x:cutW,y:D}},
      {id:uid(),a:{x:cutW,y:D},b:{x:0,y:D}},
      {id:uid(),a:{x:0,y:D},b:{x:0,y:0}},
    ];
  }else if(kind==="galley"){
    state.room={w:120,d:96};
    state.walls=rectWalls(120,96);
  }else if(kind==="u"){
    const W=156, D=132, open=60;
    state.room={w:W,d:D};
    state.walls=[
      {id:uid(),a:{x:0,y:0},b:{x:W,y:0}},
      {id:uid(),a:{x:W,y:0},b:{x:W,y:D}},
      {id:uid(),a:{x:W,y:D},b:{x:(W+open)/2,y:D}},
      {id:uid(),a:{x:(W-open)/2,y:D},b:{x:0,y:D}},
      {id:uid(),a:{x:0,y:D},b:{x:0,y:0}},
    ];
  }
  state.openings=[];
  autoFit=true; fit2D(); commit(); syncRoomInputs(); toast("Room shape applied");
}
document.getElementById("roomPreset").addEventListener("change", async (e)=>{
  const v=e.target.value; if(!v) return;
  if(state.items.length && !(await confirmAsync("Change room shape?","Cabinets stay in place; walls rebuild. You can undo.","Apply"))){ e.target.value=""; return; }
  applyRoomPreset(v); e.target.value="";
});
```

- [ ] **Step 6: First-run coach** — if `!localStorage.getItem("kitchenCoach_v1")`, show overlay with 3 steps; on dismiss set the flag.

```html
<div class="coach" id="coach" hidden>
  <div class="coach-card">
    <h3 id="coachTitle">Welcome</h3>
    <p id="coachBody"></p>
    <div class="row">
      <button class="btn ghost" id="coachSkip">Skip</button>
      <button class="btn primary" id="coachNext">Next</button>
    </div>
  </div>
</div>
```

Steps copy:
1. “Tap a cabinet size on the left to drop it into the plan.”
2. “Drag to move. Use Rotate on the top of the plan (or R on a keyboard).”
3. “Check the work triangle and build list on the right (Details on narrow screens).”

- [ ] **Step 7: Plan name + export filename**

```js
document.getElementById("planName").value = state.name || "Untitled kitchen";
document.getElementById("planName").addEventListener("change", (e)=>{
  state.name = (e.target.value || "Untitled kitchen").slice(0,60);
  save(); toast("Plan renamed");
});
// In existing export handler, set download name:
// `${(state.name||"kitchen-plan").replace(/[^\w\- ]+/g,"_").trim()||"kitchen-plan"}.json`
```

- [ ] **Step 8: Commit**

```bash
git add index.html
git commit -m "feat: plan name, room presets, stage actions, and coach marks"
```

---

### Task 4: Finish themes + richer canvas + triangle + snap guides

**Files:**
- Modify: `index.html` (CAT application, drawItem, draw2D, draw3D, updateClear)

**Interfaces:**
- Produces: `FINISH` map and `applyFinishTheme(key)` updating CSS vars + `CAT.*.fill`
- Produces: `drawWorkTriangle()` called from `draw2D`
- Produces: snap guide state `guides: [{x1,y1,x2,y2}]` cleared each frame after draw

- [ ] **Step 1: Finish themes**

```js
const FINISH = {
  oak:    {base:"#C6893F",wall:"#E0C088",tall:"#8A5A34",appliance:"#7E8C99",sink:"#5B8CA6",island:"#B9762F",counter:"#E8E2D6"},
  shaker: {base:"#F2F0EB",wall:"#FAF8F5",tall:"#E7E2D9",appliance:"#8A939C",sink:"#6B8FA8",island:"#EDE9E1",counter:"#FFFFFF"},
  walnut: {base:"#6B3F2A",wall:"#8B5A3C",tall:"#4A2C1A",appliance:"#6E7780",sink:"#4F738A",island:"#5C3422",counter:"#D9CDB8"},
  gray:   {base:"#9AA3AD",wall:"#C5CCD3",tall:"#6F7882",appliance:"#7A828A",sink:"#6A8FA3",island:"#8B949E",counter:"#E6E9EC"},
  navy:   {base:"#2F4A6E",wall:"#5B7A9D",tall:"#1E334F",appliance:"#6B7280",sink:"#3D6F8C",island:"#35567A",counter:"#E8E4DC"},
};
function applyFinishTheme(key){
  const t=FINISH[key]||FINISH.oak;
  state.finishTheme=key;
  CAT.base.fill=t.base; CAT.wall.fill=t.wall; CAT.tall.fill=t.tall;
  CAT.appliance.fill=t.appliance; CAT.sink.fill=t.sink; CAT.island.fill=t.island;
  const r=document.documentElement;
  r.style.setProperty("--finish-base",t.base);
  r.style.setProperty("--finish-wall",t.wall);
  r.style.setProperty("--finish-tall",t.tall);
  r.style.setProperty("--finish-appliance",t.appliance);
  r.style.setProperty("--finish-sink",t.sink);
  r.style.setProperty("--finish-island",t.island);
  r.style.setProperty("--finish-counter",t.counter);
  document.getElementById("finishTheme").value=key;
  buildPalette(); render(); updateBuild();
}
// on load: applyFinishTheme(state.finishTheme||"oak");
// finishTheme change: applyFinishTheme(e.target.value); commit();
```

- [ ] **Step 2: Enhance `drawItem`** — after fill of body rect:
  - Base/sink/island: draw 1.5" countertop strip along front edge using `--finish-counter` / lighten
  - Base: vertical door split at center if `w>=24`
  - Sink: ellipse for basin inset
  - Range: 4 small circles for burners if name matches /Range|Cooktop/
  - Fridge: horizontal mid line
  - Selection: if selected, stroke accent 2.5px + soft shadow; if something selected and this isn’t, `globalAlpha=0.72`

- [ ] **Step 3: Snap guides** — in `snapItem`, when a snap engages on x or y, push line spanning room bounds into `window._guides` array; in `draw2D` after items, stroke dashed accent lines and clear.

- [ ] **Step 4: Work triangle on canvas** — in `draw2D` after items, if sink + (range|cooktop) + fridge centers exist, stroke translucent triangle + mid-edge length labels (reuse distances from `updateClear`).

- [ ] **Step 5: 3D polish** — when drawing box faces, use slightly lighter top face as counter for base/sink/island (`tint(fill,1.15)`); floor fill slightly warmer; keep existing projection math.

- [ ] **Step 6: Manual visual check**

```bash
# localhost:8765 — switch themes, place sink/range/fridge, verify triangle + cabinet details
```

- [ ] **Step 7: Commit**

```bash
git add index.html
git commit -m "feat: finish themes, richer canvas, snap guides, work triangle"
```

---

### Task 5: Build list copy, print polish, palette glyphs, empty states

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Empty states** — replace plain `.empty` strings with:

```html
<div class="empty-state">
  <div class="empty-illu" aria-hidden="true"><!-- simple CSS block kitchen glyph --></div>
  <p>Drop cabinets from the left to start your plan.</p>
</div>
```

Style `.empty-illu` as a CSS-only mini cabinet (two rectangles).

- [ ] **Step 2: Palette glyphs** — in `buildPalette`, for appliances prepend a span `.glyph` with data-kind and CSS shapes (fridge, range, DW). Size chips for cabinets keep color swatch.

- [ ] **Step 3: Copy build list button** under build table:

```js
function buildListText(){
  // same aggregation as updateBuild → lines "2x Base 36  36x24x36"
  return lines.join("\n");
}
// button Copy list → navigator.clipboard.writeText(buildListText()).then(()=>toast("Build list copied"))
```

- [ ] **Step 4: Print CSS**

```css
@media print{
  .topbar .btn, .zoombar, .hint, .stage-actions, .toast-host, .coach, .drawerToggle, #pentools { display:none !important; }
  .cols{ display:block; }
  .side.left{ display:none; }
  .side.right{ break-before:page; }
  body::before{
    content: attr(data-print-title);
    display:block; font-size:18px; font-weight:700; margin:0 0 8px;
  }
}
```

Before `window.print()`, set `document.body.dataset.printTitle = `${state.name} · ${new Date().toLocaleDateString()}`;`.

- [ ] **Step 5: Open file confirm** if current plan has items — confirm replace then import.

- [ ] **Step 6: Commit**

```bash
git add index.html
git commit -m "feat: empty states, palette glyphs, copy build list, print polish"
```

---

### Task 6: README + deploy GitHub Pages

**Files:**
- Modify: `README.md`
- Possibly: `.nojekyll` (empty file so Pages serves as static)

- [ ] **Step 1: Write README** covering:
  - What it is
  - Local: `python3 -m http.server 8765` then open `http://localhost:8765`
  - iPad: open hosted URL in Safari → Share → Add to Home Screen
  - Offline note
  - Save JSON as backup if iOS clears storage
  - Deploy: push `main`, enable Pages from root

- [ ] **Step 2: Add empty `.nojekyll`**

```bash
touch /Users/rockmystic/kitchen-planner/.nojekyll
```

- [ ] **Step 3: Bump SW cache** to `kitchen-planner-v2` if assets changed after first SW write.

- [ ] **Step 4: Deploy**

```bash
cd /Users/rockmystic/kitchen-planner
gh auth status
# If authenticated:
gh repo create kitchen-planner --public --source=. --remote=origin --push
gh api -X PUT repos/{owner}/kitchen-planner/pages -f build_type=workflow 2>/dev/null || true
# Prefer classic Pages: Settings → Pages → Deploy from branch main / root
# Or:
git remote -v
# If remote exists:
git push -u origin main
```

If `gh` not available, document that remote push is manual; still finish local package.

- [ ] **Step 5: Final smoke checklist**

| Check | Expected |
|-------|----------|
| Load app | UI + canvas |
| Place base 36, rotate via stage button | Works without keyboard |
| Finish theme White Shaker | Colors update |
| Sink + range + fridge | Triangle + clearance panel |
| Save / open JSON | Round-trip |
| Print | Title + plan |
| SW | Cached offline |
| Coach once | Shows then never again |

- [ ] **Step 6: Final commit**

```bash
git add README.md .nojekyll sw.js index.html
git commit -m "docs: README and GitHub Pages ready; finalize offline shell"
```

---

## Spec coverage (self-review)

| Spec requirement | Task |
|------------------|------|
| PWA install + offline | 1, 6 |
| Parity features | 1 baseline (full HTML) + no removals in 2–5 |
| Touch targets / safe area / drawers | 2 |
| Toasts / confirms | 2, 3, 5 |
| Plan name | 3 |
| Room presets | 3 |
| Stage rotate/dup/delete | 3 |
| Coach marks | 3 |
| Finish themes | 4 |
| Richer 2D/3D, snap guides, triangle | 4 |
| Empty states, glyphs, copy list, print | 5 |
| Local + hosted | 6 |

## Placeholder scan

No TBD steps. Exact paths, handlers, and verification commands included.

## Type / name consistency

- `state.name`, `state.finishTheme`
- `applyFinishTheme(key)`, `applyRoomPreset(kind)`
- `toast(msg)`, `confirmAsync(title,msg,okLabel)`
- Storage key remains `kitchenPlan_v1` for plan body; coach uses `kitchenCoach_v1`
- SW cache name versioned `kitchen-planner-vN`
