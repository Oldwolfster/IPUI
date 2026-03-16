# IPUI `ip` Service Portal — Final Spec

## 1. Purpose

`ip` is the **canonical access path** for high-value framework state and services inside IPUI.

It replaces the current `IPContext` object (which today carries only `dt`, `fps`, `frame_id`, `surface`, `events`, `unhandled`) with a coherent service portal that pane authors and widget developers reach for instinctively.

It exists to:

- reduce wandering across the architecture
- preserve one shared path for repeated needs
- improve discoverability
- make useful framework power easier to find and use
- beat back drift by absorbing repeated patterns into the framework
- make simulations, editors, charts, games, canvases, and other custom-rendered panes feel like first-class citizens

`ip` is not meant to expose the entire object model.
It is the **public mental model** for pane authors and framework users.

---

## 2. Doctrine

A member belongs on `ip` only when it does at least one of these well:

- reduces repeated friction across panes/widgets
- strengthens the single shared path
- exposes one clear source of truth
- improves discoverability significantly
- replaces ad hoc helper logic appearing in multiple places
- makes the framework easier to explain, debug, or teach

A member does **not** belong on `ip` when it is:

- a duplicate truth
- ambiguous in meaning
- context-sensitive without making that context explicit
- a niche convenience unlikely to repeat
- speculative infrastructure without a clear current payoff

### Core rule

`ip` should be the **canonical access path**, not necessarily the canonical storage location.

Behind `ip`, every concept should still aim for **one source of truth**.

### Thin-wrapper rule

A thin wrapper may belong on `ip` when it improves one-stop shopping, discoverability, consistency, or shared-path usage — even if the underlying implementation is simple.

A thin wrapper does **not** belong on `ip` when it:

- duplicates meaning
- subtly changes semantics
- creates competing ways to do the same thing
- hides important context
- exists only because wrapping things feels architectural

### Practical principle

> **Prefer one obvious public path, even when the bridge behind it is simple.**

---

## 3. Design Rules

### 3.1 Attributes vs methods

Use:

- **attributes** for current state / current facts
- **methods** for actions, commands, or derived queries

Examples:

- `ip.mouse_pos` — attribute (current fact)
- `ip.pane_rect` — attribute (current fact)
- `ip.mouse_inside(widget)` — method (derived query, explicit target)
- `ip.request_redraw()` — method (action)
- `ip.help("mouse")` — method (query)

### 3.2 Family-first naming

Public `ip` members use **family-first naming** so related capabilities cluster naturally in autocomplete and scanning.

Prefer: `mouse_x`, `mouse_y`, `mouse_pos`, `pane_rect`, `pane_name`, `state_get`, `state_set`

Over: `x_mouse`, `name_pane`

This mirrors good DB-style cardinality grouping: the shared concept goes first.

### 3.3 Stored vs derived vs delegated

Every `ip` member should be understood as one of:

- **stored** — stable fact held by framework state
- **derived** — computed from one or more canonical truths
- **delegated** — forwarded to another subsystem through the shared path

This distinction should be known during design even if not shown to end users.

### 3.4 Explicit context beats spooky context

If a value depends on a reference object, that reference should usually be explicit.

- Good: `ip.mouse_local_pos(widget)`
- Dangerous: `ip.mouse_local_pos` — unless "local to what?" has exactly one obvious, stable answer

---

## 4. Versioning Strategy

The spec is split into:

- **Tier 1** — core `ip` spine (v0.1 target)
- **Tier 2** — strong follow-up additions (soon after v0.1)
- **Tier 3** — defer until proven necessary

The goal is not maximum API count.
The goal is a **coherent service portal that pays rent**.

---

# Tier 1 — Core `ip` Spine

These are the v0.1 targets. Maximum payoff, minimum chaos.

---

## 5.1 Identity and context

### Attributes
| Member | Type | Kind | Notes |
|---|---|---|---|
| `ip.form` | Form | delegated | The active form instance |
| `ip.form_name` | str | delegated | Name of the active form |
| `ip.pane` | Pane | delegated | The active pane instance |
| `ip.pane_name` | str | delegated | Name of the active pane |
| `ip.is_active_pane` | bool | derived | Whether this pane is currently the active one |

These establish where code is running and what it belongs to.

---

## 5.2 Timing and frame info

### Attributes
| Member | Type | Kind | Notes |
|---|---|---|---|
| `ip.dt` | float | stored | Seconds since last frame |
| `ip.fps` | int | stored | Current frames per second |
| `ip.frame` | int | stored | Monotonically increasing frame counter |
| `ip.elapsed` | float | stored | Total elapsed seconds since app start |

Common, stable, and useful across many panes/widgets. `elapsed` earns Tier 1 because animation code reaches for it constantly.

---

## 5.3 Geometry and coordinate space

### Attributes
| Member | Type | Kind | Notes |
|---|---|---|---|
| `ip.rect_pane` | Rect | derived | Usable content area after chrome is removed |
| `ip.pane_rect` | Rect | derived | Rectangle owned by the current pane — the most important geometry attribute for custom rendering |
| `ip.clip_rect` | Rect | derived | Currently active clipping rectangle |

### Methods
| Member | Signature | Kind | Notes |
|---|---|---|---|
| `ip.local_to_screen` | `(x, y) → (sx, sy)` | derived | Converts pane-local coords to screen coords |
| `ip.screen_to_local` | `(x, y) → (lx, ly)` | derived | Converts screen coords to pane-local coords |

Only expose rects whose semantics are already stable in the framework. Additional rects (`surface_rect`, `window_rect`, `form_rect`) are Tier 2.

---

## 5.4 Mouse input

### Law
There should be **one canonical mouse snapshot per frame**. Everything else should be derived from that snapshot, delegated through `ip`, and explicit about reference space when needed.

### Attributes — position and motion
| Member | Type | Kind |
|---|---|---|
| `ip.mouse_x` | int | stored |
| `ip.mouse_y` | int | stored |
| `ip.mouse_pos` | tuple | stored |
| `ip.mouse_dx` | int | derived |
| `ip.mouse_dy` | int | derived |
| `ip.mouse_wheel` | int | stored |

### Attributes — containment
| Member | Type | Kind |
|---|---|---|
| `ip.mouse_inside_window` | bool | derived |
| `ip.mouse_inside_content` | bool | derived |
| `ip.mouse_inside_pane` | bool | derived |

### Attributes — button state
| Member | Type | Kind | Semantics |
|---|---|---|---|
| `ip.mouse_down_left` | bool | stored | Held this frame |
| `ip.mouse_down_middle` | bool | stored | Held this frame |
| `ip.mouse_down_right` | bool | stored | Held this frame |
| `ip.mouse_pressed_left` | bool | derived | Just pressed this frame |
| `ip.mouse_pressed_middle` | bool | derived | Just pressed this frame |
| `ip.mouse_pressed_right` | bool | derived | Just pressed this frame |
| `ip.mouse_released_left` | bool | derived | Just released this frame |
| `ip.mouse_released_middle` | bool | derived | Just released this frame |
| `ip.mouse_released_right` | bool | derived | Just released this frame |

### Methods
| Member | Signature | Notes |
|---|---|---|
| `ip.mouse_down` | `(button_name) → bool` | "left", "middle", "right" |
| `ip.mouse_pressed` | `(button_name) → bool` | Just-pressed edge |
| `ip.mouse_released` | `(button_name) → bool` | Just-released edge |
| `ip.mouse_local_pos` | `(widget) → (lx, ly)` | Explicit target — no spooky context |
| `ip.mouse_local_x` | `(widget) → int` | Explicit target |
| `ip.mouse_local_y` | `(widget) → int` | Explicit target |
| `ip.mouse_inside` | `(widget) → bool` | Hit test against widget rect |
| `ip.mouse_hits` | `(rect) → bool` | Hit test against arbitrary rect |

---

## 5.5 Keyboard input

### Attributes
| Member | Type | Kind | Notes |
|---|---|---|---|
| `ip.keys_down` | set | stored | All keys held this frame |
| `ip.mod_shift` | bool | derived | Shift modifier active |
| `ip.mod_ctrl` | bool | derived | Ctrl modifier active |
| `ip.mod_alt` | bool | derived | Alt modifier active |

### Methods
| Member | Signature | Notes |
|---|---|---|
| `ip.key_down` | `(key_name) → bool` | Held this frame |
| `ip.key_pressed` | `(key_name) → bool` | Just-pressed edge |
| `ip.key_released` | `(key_name) → bool` | Just-released edge |

---

## 5.6 Rendering access

### Attributes
| Member | Type | Kind | Notes |
|---|---|---|---|
| `ip.surface` | Surface | stored | The primary pygame render surface |
| `ip.events` | list | stored | All pygame events this frame |
| `ip.unhandled` | list | stored | Events the UI did not consume |

These carry forward from the existing `IPContext` so nothing breaks.

---

## 5.7 Invalidation and lifecycle requests

### Methods
| Member | Signature | Notes |
|---|---|---|
| `ip.request_redraw` | `()` | Mark pane as needing repaint |
| `ip.request_layout` | `()` | Mark pane as needing layout recalc |

Core framework actions. Belong on the portal from day one.

---

## 5.8 Shared state bridge

### Methods
| Member | Signature | Notes |
|---|---|---|
| `ip.state_get` | `(key, default=None) → value` | Read from shared state |
| `ip.state_set` | `(key, value)` | Write to shared state |
| `ip.state_has` | `(key) → bool` | Check existence |
| `ip.state_del` | `(key)` | Remove key |

This exposes the framework's existing shared state path, not a second state system.

---

## 5.9 Discovery and explanation

### Methods
| Member | Signature | Notes |
|---|---|---|
| `ip.help` | `(topic=None)` | Explain what something is, when to use it, related members, examples |
| `ip.find` | `(name_or_id) → widget` | Locate a widget by name or id |
| `ip.explain` | `(name_or_widget=None)` | Dump info about a specific widget or ip member |
| `ip.dump_tree` | `()` | Print the widget tree |

This section is **first-class, not garnish**. This is one of the best anti-entropy levers in the whole design. `ip.help("mouse")` should make a new developer feel oriented in 30 seconds.

---

# Tier 2 — Strong Next Wins

Valuable, but only after Tier 1 is coherent and proven.

---

## 6.1 Expanded geometry

| Candidate | Type | Notes |
|---|---|---|
| `ip.surface_rect` | Rect | Full render surface |
| `ip.window_rect` | Rect | Visible application window |
| `ip.form_rect` | Rect | Form client area |
| `ip.chrome_rect` | Rect | Area consumed by header, tabs, toolbars |
| `ip.safe_rect` | Rect | Draw-safe area after insets/margins |
| `ip.rect_local_to_screen` | method | Rect coordinate conversion |
| `ip.rect_screen_to_local` | method | Rect coordinate conversion |

Only keep members whose meanings are stable and obvious.

---

## 6.2 Expanded timing

| Candidate | Type | Notes |
|---|---|---|
| `ip.dt_ms` | float | Delta time in milliseconds |
| `ip.elapsed_form` | float | Seconds since form became active |
| `ip.elapsed_pane` | float | Seconds since pane became active |
| `ip.time_scale` | float | Scalar for pause/slow-mo/replay |

---

## 6.3 Focus and selection

| Candidate | Type | Notes |
|---|---|---|
| `ip.focus_widget` | Widget/None | Currently focused widget |
| `ip.hover_widget` | Widget/None | Currently hovered widget |
| `ip.focus_set(widget)` | method | Set focus |
| `ip.focus_clear()` | method | Clear focus |

Strong value if the framework already has stable notions of focus/hover.

---

## 6.4 Pane-aware render helpers

| Candidate | Signature | Notes |
|---|---|---|
| `ip.draw_rect` | `(color, rect, width=0, radius=0)` | Pane-local, clip-aware |
| `ip.draw_circle` | `(color, center, radius, width=0)` | Pane-local, clip-aware |
| `ip.draw_line` | `(color, start, end, width=1)` | Pane-local, clip-aware |
| `ip.draw_text` | `(text, x, y, font=None, color=None)` | Pane-local, theme-aware |
| `ip.clear` | `(color=None)` | Clear pane area |
| `ip.fill` | `(color, rect=None)` | Fill pane area |
| `ip.blit` | `(surface, position)` | Blit onto pane |

These belong on `ip` when they add framework value: pane-local coordinates, clip awareness, theme defaults, caching. Even when implementation is thin, they keep users on the shared path.

---

## 6.5 Cursor helpers

| Candidate | Notes |
|---|---|
| `ip.cursor_name` | Current cursor name |
| `ip.cursor_set(name)` | "arrow", "hand", "crosshair", "ibeam", "wait" |
| `ip.cursor_reset()` | Restore default |

---

## 6.6 Debug and overlay control

| Candidate | Notes |
|---|---|
| `ip.debug_on` | Whether debug mode is active |
| `ip.overlay_on` | Whether overlay is showing |
| `ip.debug_toggle()` | Toggle debug mode |
| `ip.overlay_toggle()` | Toggle overlay |
| `ip.inspect(widget)` | Dump debug info for a widget |

Fits the doctrine: when the problem is hard, make it visible.

---

## 6.7 Event capture and routing

| Candidate | Notes |
|---|---|
| `ip.consume_event(event)` | Mark event as handled |
| `ip.capture_input()` | Claim all input for this pane |
| `ip.release_input()` | Release input claim |
| `ip.capture_mouse()` | Claim mouse only |
| `ip.release_mouse()` | Release mouse claim |

Useful for drag, paint, pan, and editor behaviors in advanced panes.

---

## 6.8 Clipping and surface helpers

| Candidate | Notes |
|---|---|
| `ip.clip_push(rect)` | Push clipping rect onto stack |
| `ip.clip_pop()` | Pop clipping rect |
| `ip.make_surface(w, h, alpha=True)` | Create a new surface |
| `ip.get_cached_surface(key, w, h)` | Reuse a cached surface |
| `ip.invalidate_surface(key)` | Evict from cache |

---

# Tier 3 — Defer Until Proven

Good ideas, but dangerous to rush. Only add after real usage proves the need.

---

## 7.1 Viewport and camera

| Candidate | Notes |
|---|---|
| `ip.camera_x`, `camera_y`, `camera_zoom` | Camera state |
| `ip.world_to_screen(x, y)` | World-space conversion |
| `ip.screen_to_world(x, y)` | World-space conversion |
| `ip.pan_camera(dx, dy)` | Camera control |
| `ip.zoom_at(sx, sy, delta)` | Zoom anchored at screen point |

Useful for: simulations, map viewers, node editors, strategy games, zoomable charts. Defer until at least one real pane needs it.

---

## 7.2 Chrome / immersive control

| Candidate | Notes |
|---|---|
| `ip.chrome_visible` | Whether chrome is showing |
| `ip.chrome_show()` / `chrome_hide()` | Toggle chrome |
| `ip.immersive_enter()` / `immersive_exit()` | Full immersive mode |

Useful for game mode, presentation mode, editor-style views. Not part of proving the spine.

---

## 7.3 Background work / async

| Candidate | Notes |
|---|---|
| `ip.task_start(fn, on_done=None)` | Offload expensive work |
| `ip.task_cancel(task_id)` | Cancel background task |
| `ip.task_status(task_id)` | Check task state |

This can get swampy fast. Only add after state, invalidation, and thread-safety semantics are deliberately designed.

---

## 7.4 Fixed timestep / simulation

| Candidate | Notes |
|---|---|
| `ip.is_fixed_step` | Whether using fixed timestep |
| `ip.fixed_dt` | Fixed timestep value |
| `ip.tick` | Integer simulation tick |

---

## 7.5 HUD and transient UI

| Candidate | Notes |
|---|---|
| `ip.hud_surface` | Overlay surface for HUD |
| `ip.draw_hud_text(text, x, y)` | Quick HUD text |
| `ip.show_toast(message, duration)` | Transient message |
| `ip.show_overlay(widget_or_builder)` | Show overlay widget |

---

## 7.6 Asset / cache / profiler

| Candidate | Notes |
|---|---|
| `ip.cache_get(key)` / `cache_set(key, value)` | General-purpose cache |
| `ip.profiler_begin(name)` / `profiler_end(name)` | Manual profiling spans |
| `ip.debug_text(text, x, y)` | Debug draw text |
| `ip.debug_rect(rect, color)` | Debug draw rect |
| `ip.stats.frame_time_ms` (etc.) | Performance stats bundle |

---

# 8. Special Guidance: Mouse Architecture

This deserves its own section because it is a prime drift factory.

### Law

There should be **one canonical mouse snapshot per frame**.

Everything else should be:
- derived from that snapshot
- delegated through `ip`
- explicit about reference space when needed

### Good
- `ip.mouse_pos` — one truth
- `ip.mouse_inside(widget)` — explicit target
- `ip.mouse_local_pos(widget)` — explicit target

### Bad
- Multiple components asking pygame for mouse independently
- Local mouse values with hidden reference assumptions
- Duplicate cached mouse truths in drag, hit, and widget code

---

# 9. Special Guidance: Geometry Architecture

Geometry APIs should reflect **stable framework spaces**, not hopeful guesses.

A geometry member belongs on `ip` when:
- the space exists clearly in the framework
- callers repeatedly need it
- its semantics are consistent across panes
- it reduces ad hoc rect math

Geometry should not be added to `ip` merely because it sounds useful.

---

# 10. What `ip` Is Not

`ip` is not:

- a bag of trivia
- the entire engine flattened into one object
- a replacement for internal architecture
- a hiding place for duplicate truths
- a wrapper layer for the sake of wrapping

`ip` is the **operating console** for pane authors — the geometry oracle, timing source, input router, render bridge, lifecycle truth source, state bridge, and performance microscope.

---

# 11. Review Checklist for Every New `ip` Member

Before adding a new member, ask:

1. What repeated pain does this solve?
2. What family does it belong to?
3. What is the one underlying truth?
4. Is it stored, derived, or delegated?
5. Is its meaning stable?
6. Should it be an attribute or a method?
7. Is any reference context explicit enough?
8. Does this reduce drift?
9. Does this improve discoverability?
10. Would future-you be happy this lives on the public portal?

If those answers are muddy, the member is premature.

---

# 12. What We Have Today (IPContext.py baseline)

The current `IPContext` carries:

| Member | Type | Maps to Tier 1 |
|---|---|---|
| `dt` | float | `ip.dt` ✓ |
| `fps` | int | `ip.fps` ✓ |
| `frame_id` | int | `ip.frame` ✓ (rename) |
| `surface` | Surface | `ip.surface` ✓ |
| `events` | list | `ip.events` ✓ |
| `unhandled` | list | `ip.unhandled` ✓ |

Everything else in Tier 1 is net-new.

---

# 13. Recommended First Implementation Slice

Maximum payoff, minimum chaos. Build these first:

**Identity:** `form`, `form_name`, `pane`, `pane_name`, `is_active_pane`

**Timing:** `dt`, `fps`, `frame`, `elapsed`

**Geometry:** `content_rect`, `pane_rect`, `clip_rect`, `local_to_screen()`, `screen_to_local()`

**Mouse:** `mouse_x`, `mouse_y`, `mouse_pos`, `mouse_down(...)`, `mouse_pressed(...)`, `mouse_inside(widget)`, `mouse_local_pos(widget)`

**Keyboard:** `keys_down`, `key_pressed(...)`, `mod_shift`, `mod_ctrl`, `mod_alt`

**Rendering:** `surface`, `events`, `unhandled` (carry forward from IPContext)

**Lifecycle:** `request_redraw()`, `request_layout()`

**State:** `state_get(...)`, `state_set(...)`

**Discovery:** `help(...)`

That is enough to prove the portal without building an octopus cathedral.

---

# 14. Final Summary

`ip` should become the framework's **canonical access surface** for repeated, high-value questions and actions.

Its success will be measured by whether it:

- pulls repeated needs into one path
- reduces duplicate logic
- improves discoverability
- preserves one source of truth per concept
- makes panes easier to write
- makes the framework easier to explain
- beats back drift instead of becoming a new source of it

When in doubt:

> **A feature belongs on `ip` only if putting it there makes the shared path stronger.**