# IPUI Lifecycle & Timing

> **The single source of truth for *when* things happen in IPUI.**
>
> If you've ever hit a "widget not found" Houston, called a helper that fired too early, or wondered why your tab seemed to initialize twice — this is the doc.

This document maps every moment in an IPUI app's life: from `IPUI.show()` to the first frame, through every tab switch, and around the per-frame loop that runs forever after that. It also catalogs the **danger zones** — patterns that look right but fire at the wrong time — so you can avoid them and we can fix them.

---

## Table of Contents

- [TL;DR — The Three Timescales](#tldr--the-three-timescales)
- [1. Cold Boot Sequence](#1-cold-boot-sequence)
- [2. Widget Construction Sequence](#2-widget-construction-sequence)
- [3. Tab Switch Sequence](#3-tab-switch-sequence)
- [4. The Per-Frame Loop](#4-the-per-frame-loop)
- [5. Hook Reference Table](#5-hook-reference-table)
- [6. Danger Zones](#6-danger-zones)
- [7. Where Does My Code Go?](#7-where-does-my-code-go)
- [Observations Worth Discussing](#observations-worth-discussing)

---

## TL;DR — The Three Timescales

An IPUI app's life splits into three distinct timescales. Each fires different hooks in a different order.

```
┌──────────────────────────────────────────────────────────────────┐
│  COLD BOOT          IPUI.show()  →  first frame painted          │
│                     One-time setup. ip_setup fires here.         │
├──────────────────────────────────────────────────────────────────┤
│  TAB SWITCH         User clicks a tab. Or set_pane() rebuilds.   │
│                     ip_activated fires. Maybe ip_setup if cold.  │
├──────────────────────────────────────────────────────────────────┤
│  PER-FRAME LOOP     60×/sec, forever after.                      │
│                     ip_think → layout → ip_draw → render →       │
│                     ip_draw_hud → flip.                          │
└──────────────────────────────────────────────────────────────────┘
```

**The cheat sheet:**

| You want to… | Hook | Tier |
|---|---|---|
| Lay out widgets | pane method (e.g. `def home(self, parent):`) | Tab |
| Initialize state once | `ip_setup(ip)` | Form, Tab |
| Refresh on tab visit | `ip_activated(ip)` | Form, Tab |
| Tick every frame | `ip_think(ip)` | Form, Tab |
| Paint behind widgets | `ip_draw(ip)` | Form, Tab |
| Paint on top of widgets | `ip_draw_hud(ip)` | Form, Tab |
| Build a custom widget | `build()` | Widget |

---

## 1. Cold Boot Sequence

From the user typing `python myapp.py` to the first pixel on screen. Numbered steps with what's available at each one.

```
1.  show(MyForm)
2.  GameLoop.__init__               → pygame.init(), screen created, IP() created
3.  IPUI.switch(MyForm)             → MyForm() instantiated
4.    _BaseForm.__init__            → widgets dict, pipeline, registry created
5.    _BaseWidget.__init__(form)    → form is its own root widget
6.    _BaseForm.setup()
        ├─ setup_tabs() if TAB_LAYOUT exists
        │    ├─ TabStrip created
        │    ├─ TabStrip.build()
        │    │    └─ switch_tab(first_tab_name)
        │    │         ├─ allow_switch()                  ← tab_on_change can veto
        │    │         ├─ ensure_content(first_tab_name)
        │    │         │    ├─ resolve_tab()              ← imports tab file, instantiates _BaseTab
        │    │         │    │    └─ _BaseTab.__init__()
        │    │         │    │         └─ register_derives()  ← BINDINGS wired into pipeline
        │    │         │    ├─ rebuild_tab_areas()        ← creates Pane widgets
        │    │         │    ├─ ensure_setup()             ← FIRES tab.ip_setup(ip)
        │    │         │    └─ fill_panes()               ← FIRES each pane builder method
        │    │         └─ notify_activated()              ← FIRES tab.ip_activated(ip)  ★ first
        │    └─ (any tabs in tab_early_load are prepared here)
        └─ ip_setup(ip) at form tier                      ← FIRES form.ip_setup(ip)
7.    _BaseForm.build_footer()
8.  IPUI.notify_activated(form)
        ├─ FIRES form.ip_activated(ip)
        └─ if tab_strip exists: FIRES active_tab.ip_activated(ip)  ★ second
9.  GameLoop.run_loop()             → first frame begins
```

### What's available at each step

| After step | You can safely access |
|---|---|
| 5 | `self.form`, `self.widgets`, `self.pipeline` (form-level) |
| 6 — inside `pane_method(parent)` | `self.form`, all widgets *built so far* in *this* and *earlier* panes. **Not** widgets in panes that haven't built yet. |
| 6 — inside `tab.ip_setup(ip)` | All widgets in this tab. Pipeline derives are registered. Tab's panes have **not** built yet at this point — see [Danger Zones](#6-danger-zones). |
| 6 — inside `form.ip_setup(ip)` | The first tab is fully booted — its widgets exist, its `ip_setup` has fired, its `ip_activated` has fired once. |
| 8 | Everything. The form is live. |

---

## 2. Widget Construction Sequence

Inside any single widget's `__init__`. Same for `Button`, `Card`, `TextBox`, every widget in the catalog.

```
1.  preflight_check()             ← input validation (parent, flex, text_align, etc.)
2.  Identity assigned             ← widget_id, name, widget_type
3.  Tree wiring                   ← self.parent, self.form, parent.children.append(self)
4.  REGISTRATION                  ← form.widgets[name] = self     ★ widget is now findable
5.  build()                       ← subclass code runs here
                                    Children built inside build() recurse through this
                                    same sequence, registering as they go.
6.  Caller kwarg overrides        ← pad, pad_x, pad_y, gap, border applied here
                                    (this is why Card(parent, pad=10) wins over build()'s default)
7.  text_align defaults, tab_order, widget_type fallback
8.  private_build_comp = True     ← signals construction complete
```

### The critical insight

Step 4 happens **before** step 5. So:

- A widget is in `form.widgets` *before* its own `build()` runs.
- A widget's children — built inside `build()` — register *during* the parent's `build()`.
- Within a single pane, widgets register **top-down, depth-first**, in the order you write them.

### Example

```python
def home(self, parent):
    Title(parent, "Hello", name="lbl_title")    # ← registers immediately
    card = Card(parent, name="card_main")       # ← registers, then build() recurses
    Body(card, "Hi", name="lbl_body")           # ← registers during card's build
    Button(parent, "OK", name="btn_ok")         # ← registers last
```

Order in `form.widgets`: `lbl_title`, `card_main`, `lbl_body`, `btn_ok`.

If you call `self.form.widgets.get("btn_ok")` from inside `Title`'s creation, it'll Houston — `btn_ok` doesn't exist yet. This is the same trap as the `set_status` bug (see [Danger Zones](#6-danger-zones)).

---

## 3. Tab Switch Sequence

Tab switches come in two flavors. The difference matters.

### Cold switch (first visit to a tab)

```
User clicks "Forge" — never visited before
  │
  ▼
TabStrip.switch_tab("Forge")
  │
  ├─► allow_switch("Forge")              ← tab_on_change can veto (return False)
  │
  ├─► cache_active_content()             ← snapshot current tab's widgets for later restore
  │
  ├─► self.active_tab = "Forge"
  ├─► update_button_visuals()
  │
  ├─► ensure_content("Forge")
  │     │
  │     ├─► resolve_tab("Forge")         ← imports Forge.py, instantiates the _BaseTab
  │     │     └─► _BaseTab.__init__()    ← BINDINGS wired into pipeline
  │     │
  │     ├─► rebuild_tab_areas(entries)   ← creates Pane widgets for each pane slot
  │     ├─► ensure_setup("Forge")        ← FIRES Forge.ip_setup(ip)  (first time only)
  │     └─► fill_panes("Forge", entries) ← FIRES each pane builder method
  │
  └─► notify_activated("Forge")          ← FIRES Forge.ip_activated(ip)
```

### Warm switch (re-visiting a tab)

```
User clicks "Forge" — visited before
  │
  ▼
TabStrip.switch_tab("Forge")
  │
  ├─► allow_switch("Forge")              ← tab_on_change can veto
  │
  ├─► cache_active_content()             ← snapshot current tab's widgets
  │
  ├─► self.active_tab = "Forge"
  ├─► update_button_visuals()
  │
  ├─► ensure_content("Forge")
  │     └─► restore_cached_content()     ← reuse previously-built widgets, NO rebuild
  │                                        NO ip_setup. NO pane builder methods re-run.
  │
  └─► notify_activated("Forge")          ← FIRES Forge.ip_activated(ip)
```

### What this means in practice

| Event | Cold switch | Warm switch |
|---|---|---|
| `tab_on_change` | Fires | Fires |
| Tab class instantiated | Yes | No (cached) |
| `BINDINGS` registered | Yes | No (already done) |
| Pane widgets created | Yes | No (restored from cache) |
| Pane builder methods called | Yes | No |
| `ip_setup` | **Yes** | **No** |
| `ip_activated` | **Yes** | **Yes** |

**The takeaway:** Anything that needs to happen *every time the tab becomes visible* goes in `ip_activated`. Anything that should happen *once* goes in `ip_setup`.

---

## 4. The Per-Frame Loop

After cold boot completes, this loop runs ~60×/sec until the app exits.

```
┌────────────────────────────────────────────────────────────────┐
│  FRAME N                                                        │
│                                                                 │
│  1. dt, fps, frame, screen, form snapshot                       │
│       └─ ip.frame_begin(...)                                    │
│                                                                 │
│  2. pygame.event.get() collected into ip.events                 │
│                                                                 │
│  3. MgrInput.process_frame(ip, form)                            │
│       └─ Mouse/keyboard dispatched to widgets:                  │
│            clicks, drags, hover, scroll, focus                  │
│                                                                 │
│  4. form.dispatch_ip_think(ip)                                  │
│       ├─ if has tabs:                                           │
│       │    for each cached tab:                                 │
│       │      if active OR THINK_ALWAYS:                         │
│       │        state.tick(dt)                                   │
│       │        tab.ip_think(ip)                                 │
│       └─ else (tabless):                                        │
│            state.tick(dt)                                       │
│            form.ip_think(ip)                                    │
│                                                                 │
│  5. screen.fill(BACKGROUND)                                     │
│                                                                 │
│  6. form.dispatch_ip_render(ip, "ip_draw")                      │
│       ├─ if has tabs: active_tab.ip_draw(ip)                    │
│       └─ else:        form.ip_draw(ip)                          │
│                                                                 │
│  7. IPUI.render(screen)                                         │
│       └─ form.render():                                         │
│            ├─ NotNP_HardLayout (Pass 1)                         │
│            ├─ NotNP_HardWrap   (Pass 2 — text wrap)             │
│            ├─ NotNP_HardLayout (Pass 3 if wrap changed)         │
│            ├─ NotNP_HardHug    (Pass 4 — hug_parent shrinks)    │
│            ├─ MgrSanity.check_tree                              │
│            ├─ draw() recurses widget tree                       │
│            ├─ draw_overlays                                     │
│            └─ draw_tooltips                                     │
│                                                                 │
│  8. form.dispatch_ip_render(ip, "ip_draw_hud")                  │
│       └─ same routing as step 6                                 │
│                                                                 │
│  9. pygame.display.flip()                                       │
└────────────────────────────────────────────────────────────────┘
```

### Routing rules — important

- **`ip_think` on a tab** fires only on the active tab, *unless* `THINK_ALWAYS = True` on that tab class.
- **`ip_think` on the form** fires only when there's no `TAB_LAYOUT` (tabless mode). If the form has tabs, the form's `ip_think` is **not** called.
- **`ip_draw` and `ip_draw_hud`** fire only on the active tab (or the form in tabless mode). `THINK_ALWAYS` does not affect drawing.

### What's safe to do where

| Hook | Read widget tree? | Modify widgets? | Pipeline writes? | Custom drawing? |
|---|---|---|---|---|
| `ip_think` | Yes | Yes (`set_text`, etc.) | Yes | No — drawing belongs in `ip_draw`/`ip_draw_hud` |
| `ip_draw` | Yes (rects from last frame) | Avoid — layout already ran for this frame | Avoid — derives won't re-render until next frame | Yes, this is the place |
| `ip_draw_hud` | Yes (rects from this frame) | Avoid — same reason | Avoid — same reason | Yes |

---

## 5. Hook Reference Table

Every hook, every tier, when it fires, what's safe to access.

| Hook | Tier | When it fires | Fires on inactive? | Safe to access |
|---|---|---|---|---|
| `__init__` (do not override) | Form, Tab, Widget | At construction | N/A | Don't touch — framework only |
| `build()` | Widget | During `__init__`, after registration. Re-runs on `set_text` and other state changes. | N/A | `self.parent`, `self.form`, framework attrs. Children created here register as you create them. |
| `register_derives()` | Tab | Inside `_BaseTab.__init__` | N/A | Pipeline. Runs automatically — you don't call it. |
| Pane builder method | Tab/Form | During cold tab switch (or `set_pane`) | N/A | Widgets *built so far* in this and earlier panes. **Not** widgets in later panes. |
| `ip_setup(ip)` | Form, Tab | Once, after the tab/form's widget tree is built. | N/A | Full widget tree of this tab. Pipeline writes here trigger derives. |
| `ip_activated(ip)` | Form, Tab | Each time the form/tab becomes visible (incl. cold boot). | N/A | Identity (`ip.form`, `ip.tab`) and geometry (`ip.rect_pane`) are correct. Per-frame fields (`ip.dt`, `ip.events`, `ip.surface`) reflect the **last completed frame**, not the current one. |
| `ip_think(ip)` | Form, Tab | Every frame | Tab: only with `THINK_ALWAYS = True`. Form: never (form `ip_think` only runs in tabless mode). | Everything. |
| `ip_draw(ip)` | Form, Tab | Every frame, before widget tree renders | Active only | `ip.surface` is the screen. Widget rects from this frame are not yet finalized — layout runs after `ip_draw`. |
| `ip_draw_hud(ip)` | Form, Tab | Every frame, after widget tree renders | Active only | `ip.surface`, widget rects from this frame are correct. |

> **Note on `ip` inside `ip_activated`:** Identity and geometry fields are correct (the framework calls `ip.set_tab_context()` before invoking the hook). But `ip.dt`, `ip.events`, and `ip.surface` are leftovers from the last completed frame — `ip_activated` runs at lifecycle transitions, not inside the per-frame loop.

---

## 6. Danger Zones

These are patterns that *look* right but fire at the wrong time. Each one has bitten us.

### 🚨 Reading a widget that hasn't been built yet

**The bug we just hit.** A pane builder calls a helper that reads from `form.widgets`, but the named widget lives in a *later* pane.

```python
def tables(self, parent):                        # PANE 1 — runs first
    self.build_grid(parent)
    self.refresh_grid()                          # ← calls populate_tables_grid()
                                                 #   which on error calls set_status()
                                                 #   which reads "lbl_sql_status"
                                                 #   which lives in PANE 2 — not built yet!

def query(self, parent):                         # PANE 2 — runs second
    Body(parent, "", name="lbl_sql_status")      # ← only registers HERE
```

**Why it bites:** Widgets register in pane-build order. From inside `tables()`, only `tables()`'s widgets exist. Calling a helper that assumes `lbl_sql_status` is registered will Houston with "Pipeline key not found" — but the *real* bug is that the helper was called too early.

**Fix patterns:**
- Move the call to `ip_setup` — by then, every pane in this tab has built.
- Make the helper defensive: if the status widget doesn't exist yet, no-op or print.
- Reorder pane construction so the status widget exists before anyone needs it.

### 🚨 Pipeline writes during pane construction

```python
def home(self, parent):
    Body(parent, "", name="lbl_count")
    self.form.pipeline_set("count", 0)           # ← fires derives immediately
                                                 #   if any derive targets a widget
                                                 #   in a later pane → Houston
```

**Why it bites:** `pipeline_set` fires all derives immediately. If a derive targets a widget that lives in a later pane, that widget isn't registered yet.

**Fix:** Initialize pipeline values in `ip_setup`, or use `PIPELINE_DEFAULTS` on the form (seeded before any tab builds).

### 🚨 `ip.dt` and `ip.events` inside `ip_activated`

```python
def ip_activated(self, ip):
    self.smooth_pos += self.velocity * ip.dt     # ← dt is from the last completed frame
                                                 #   could be stale, could be huge after a long
                                                 #   period off-screen
```

**Why it bites:** `ip_activated` runs at a lifecycle transition, not inside the per-frame loop. The per-frame fields (`dt`, `events`, `surface`) reflect whatever happened last, which may have been seconds ago.

**Fix:** Use `ip_activated` for state resets and reads of identity/geometry; let `ip_think` handle anything that needs a current `dt`.

### 🚨 Form `ip_setup` runs *after* the first tab is fully booted

This is non-obvious. In `_BaseForm.setup()`:

```python
def setup(self):
    self.pad = 0
    if hasattr(self.__class__, 'TAB_LAYOUT'): self.setup_tabs()   # ← first tab boots here
    if hasattr(type(self), 'ip_setup'):       self.ip_setup(self.ip)  # ← form ip_setup fires AFTER
```

So by the time `form.ip_setup` runs, the first tab has already:
- Been instantiated
- Had its `BINDINGS` registered
- Had its panes built
- Fired `ip_setup`
- Fired `ip_activated`

**Why it bites:** If you put cross-tab initialization in form `ip_setup` (e.g. seeding pipeline values that the first tab reads), the first tab has already booted without them.

**Fix:** Put truly app-wide initial state in the `PIPELINE_DEFAULTS` class dict, which is seeded in `_BaseForm.__init__` *before* any tab boots.

### 🚨 `ip_activated` fires twice on cold boot

On cold boot, the active tab's `ip_activated` fires once during `TabStrip.build()` → `switch_tab(first)` → `notify_activated()`, and again during `IPUI.notify_activated(form)` → tab's `ip_activated`.

**Why it bites:** If `ip_activated` does work that should happen once-per-visit (incrementing a counter, kicking off animation, refreshing data), it'll happen twice on cold boot.

**Fix:** Until the framework deduplicates this, make `ip_activated` idempotent — calling it twice in a row should produce the same result as calling it once.

This is flagged in [Observations Worth Discussing](#observations-worth-discussing) as a candidate for a real fix.

### 🚨 `THINK_ALWAYS` ≠ "draw always"

```python
class TrainingMonitor(_BaseTab):
    THINK_ALWAYS = True

    def ip_think(self, ip):
        self.training_step()                     # ← fires even when off-screen ✓

    def ip_draw(self, ip):
        self.render_chart(ip)                    # ← does NOT fire when off-screen ✗
```

**Why it bites:** Easy to assume `THINK_ALWAYS` means "this tab is fully alive in the background." It doesn't — only `ip_think` fires for inactive `THINK_ALWAYS` tabs. Drawing only happens on the active tab regardless.

**Fix:** Decouple compute from render. Run the simulation in `ip_think`; only paint in `ip_draw`/`ip_draw_hud` when active.

### 🚨 `set_pane` from inside a pane builder

```python
def home(self, parent):
    Title(parent, "Welcome")
    self.set_pane(1, self.details_pane)          # ← mutating tab_layout while building it
```

**Why it bites:** `set_pane` rebuilds pane areas. Doing this from inside a pane builder means you're mutating the structure that's currently being walked.

**Fix:** Defer to `ip_setup` or trigger from a button click / event.

---

## 7. Where Does My Code Go?

A flowchart for the most common questions.

```
"I want to lay out widgets."
  → Pane builder method.

"I want to initialize state once when this tab is created."
  → ip_setup(self, ip)

"I want to refresh data every time the user opens this tab."
  → ip_activated(self, ip)

"I want to do something every frame."
  → ip_think(self, ip)

"I want to draw a custom shape behind the widgets."
  → ip_draw(self, ip)

"I want to draw an FPS counter / overlay on top."
  → ip_draw_hud(self, ip)

"I want to look up another widget by name."
  → ip_setup or later. NEVER from a pane builder that runs before the
    target widget's pane.

"I want to seed a pipeline value before any tab reads it."
  → PIPELINE_DEFAULTS class dict on the form.

"I want to react to a value changing."
  → BINDINGS class dict on the tab. Reactive — no callback needed.

"I want to write a custom widget."
  → Subclass _BaseWidget, override build(). Never override __init__.
```

---

## Observations Worth Discussing

Items uncovered while writing this doc that may be worth real fixes, not just documentation:

1. **Double `ip_activated` on cold boot.** The active tab's `ip_activated` fires once during `TabStrip.build` → `switch_tab` → `notify_activated`, and again during `IPUI.notify_activated(form)`. Currently users have to make `ip_activated` idempotent. A small fix in `IPUI.notify_activated` could skip the second call if the tab was just activated as part of the same boot sequence.

2. **Form `ip_setup` runs after first tab boots.** Order in `_BaseForm.setup()` is `setup_tabs()` then `ip_setup(ip)`. This means form-level init that should seed state for the first tab arrives too late. A swap would mean the first tab's `ip_setup` could read form-level state. Trade-off: the form's `ip_setup` would then run before *any* widget tree existed — needs thought about what's safe to access.

3. **`set_status` and similar helpers should be construction-safe.** When a helper that reads `form.widgets.get("X")` is called from a pane builder before X exists, the resulting Houston blames the pipeline binding rather than the real cause (helper called too early). A defensive `set_status` that no-ops when its target widget isn't registered yet would prevent the rabbit hole.

4. **Errors during pane construction get masked.** When `populate_tables_grid()` raises during `tables()` pane construction, the `except` handler tries to call `set_status` — but `set_status`'s own widget doesn't exist yet, so we get a misleading Houston about the *reporter*, not the original error. Worth considering: a try/except around each pane builder that surfaces the original exception cleanly even if the error-reporting path itself fails.

5. **Tab class instantiation happens inside `switch_tab`.** If the user clicks a tab and the tab file imports a missing module (or has any import-time error), the failure happens in the middle of a tab switch. Currently this surfaces as a Python traceback. Could be wrapped to give a friendlier "tab failed to load" Houston with the import error inline.

6. **Cold boot fires hooks in this order:** widget tree build → tab `ip_setup` → tab `ip_activated` (#1) → form `ip_setup` → form `ip_activated` → tab `ip_activated` (#2). The form's hooks running *between* the tab's two `ip_activated` calls is a strange ordering. Worth a design pass.

---

*Last updated: this is the first version. Things will move as we fix the items above. Keep this doc honest — when timing changes, update here first.*