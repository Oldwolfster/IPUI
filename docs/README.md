# IPUI - Idiot Proof UI - Because we've all spent 3 hours debugging a button!

A Python/Pygame UI framework

> **Easy to get right, hard to get wrong.**

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![Pygame-ce](https://img.shields.io/badge/pygame--ce-2.x-orange)
![License](https://img.shields.io/badge/license-MIT-green)

**Actively developed • First public release — March 2026**

> IPUI is developed and tested against `pygame-ce`. It is imported in code as `pygame`.

```bash
pip install ipui
```

---
## Table of Contents

- [The IPUI Advantage](#-the-ipui-advantage)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [The ip Service Portal](#the-ip-service-portal)
- [Lifecycle Hooks](#lifecycle-hooks)
- [Updating the UI](#updating-the-ui)
- [Widget Catalog](#widget-catalog)
- [Layout System](#layout-system)
- [Tabs and Panes](#tabs-and-panes)
- [Reactive Pipeline](#reactive-pipeline)
- [Imperative Approach](#imperative-approach)
- [Construction-Time Safety](#construction-time-safety)
- [Styling and Theming](#styling-and-theming)
- [Launching Your App](#launching-your-app)
- [API Reference](#api-reference)
- [Dependencies](#dependencies)
- [Appendix A: Single Pass Cycle](#appendix-a-detail-of-single-pass-cycle)
- [Appendix B: The Game Loop](#appendix-b-the-game-loop)
- [Appendix C: Tab Switch Lifecycle](#appendix-c-tab-switch-lifecycle)

---

## Additional Documentation
- [Naming Conventions](docs/NamingAndConventions.md)
- [Layout Guide](docs/IPUI_Layout_Guide_Original_Flex.md)

---

## 🛠️ The IPUI Advantage

- 🗂️ **First-Class Tab System:** Define your app's tabs and pane layout from a single dictionary. IPUI scaffolds the structure and keeps each tab cleanly modular.
- 📱 **Resolution Independent:** UI scales automatically to physical screen height, so it stays usable on an old laptop or a 4K monitor.
- 📐 **Declarative Layout:** Simple, flexible syntax that handles the math so you can focus on the logic.
- 🧩 **Built to Extend:** Custom widgets get layout, events, and styling automatically. Standard widgets take 5–10 LOC; even tools like a network diagram widget come in under 150 LOC.
- 📜 **One-Touch Scrolling:** Make any Card scrollable with a single parameter—no complex viewport setup required. Scrollbars are draggable and styled automatically.
- 🔗 **Construction IS Attachment:** No floating widgets or `add()` calls. If you build it inside a container, it's attached automatically.
- 🔄 **Multiple Update Styles:** Use DAG-based reactivity, pipeline-driven synchronization, or direct widget access—whichever fits the job best.
- ⛓️ **Data Pipeline:** Bind widgets to a Pipeline Key and let IPUI propagate updates automatically. Derives stay in sync with zero manual update code.
- 🎮 **Pygame Lifecycle Hooks:** `ip_think`, `ip_draw`, and `ip_draw_hud` give you full access to the game loop without fighting the framework.
- 💡 **Multi-Tier Tooltips:** Choose between standard hover tips or "Super Tooltips"—pinnable, scrollable windows capable of displaying deep technical data.
- 🗃️ **Automatic Widget Registry:** When DAG or pipeline isn't the right fit, named widgets stay easy to reach across tabs and panes—no globals, no reference plumbing required.
- 🐞 **Pro Debug Mode:** Includes a live Widget Tree and layout overlays to make positioning issues easy to diagnose.
- 💻 **Beautiful Code Boxes:** Display source code by passing a string or a file path; IPUI handles the formatting.
- 🗺️ **Tab Map:** A bird's-eye view of your entire application for quick review and navigation.
- 📊 **Grid:** The most capable grid in the pygame ecosystem. Automatic sorting across pages, pagination, and SQL-ready. Feed it lists, dicts, or databases—it adapts to your workflow.
- 📚 **Self-Documenting:** Documentation stays in sync with the framework by reading the source code directly.
- 📈 **Live Matplotlib Charts:** Embed real-time updating research visuals directly in your pygame UI—useful for training curves, experiment monitoring, and diagnostics.

---

## Quick Start

IPUI is built to grow across files, but the fastest way to start is with **one file**.

Get it running first. Then let IPUI help you split things out as your app grows.

---

### Step 1: First Taste — Run in 30 Seconds

Save this as `SmokeTest.py` (or any name you like):
```python
# SmokeTest.py  New: one-class smoke test using form-as-pane
from ipui import *

class SmokeTest(_BaseForm):
    TAB_LAYOUT = {
        "Hello World"   :["welcome"     ],  # ← This one works immediately...
                                            #   Due to the welcome method below
        "Widgets"       :["demo","demo2"],  # ← Will trigger template picker
        "Bouncing Ball" :["arena", None ],  # ← Will trigger template picker
    }
    
    def welcome(self, parent):               # ← matches "welcome" in TAB_LAYOUT
        Banner  (parent, "IPUI"              , text_align=CENTER, glow=True)
        Title   (parent, "Easy to get right!", text_align=CENTER)
        Body    (parent, "Hard to get wrong.", text_align=CENTER)
        Button  (parent, "Click Me :)"       , on_click=lambda: self.form.show_modal("Hello"))
        
if __name__ == "__main__": show(SmokeTest)
```

```bash
python SmokeTest.py
```

Three tabs appear immediately:
  - **Hello World**   — fully working with banner, text, and button
  - **Widgets**       — show IPUI's helper card with template options
  - **Bouncing Ball** — show IPUI's helper card with template options

---

### Step 2: Open Widgets — Let IPUI Forge the File

Change to the 'Widgets' tab.

> Hello World already has real content.
> Widgets and Bouncing Ball do not have matching .py files yet.

**Problem? Not even a little.**

Instead of throwing an error or even showing an empty tab, IPUI steps in with a helper card:

<!-- SCREENSHOT: ipui/assets/images/houston_card.png — the Houston helper card offering to scaffold a missing tab -->

Pick Full Showcase on the Widgets tab. IPUI will create Widgets.py and hot-swap in a complete, interactive widget playground with real working controls (buttons, textboxes, cards, grids, etc.).

It's not a dead stub — it's live code you can immediately click, rearrange, and copy-paste from.

---

### Step 3: Customize and Scale

After IPUI generates the file (e.g. Widgets.py), it's packed with working examples. Trim it down to just what you need:

```python
from ipui import *

class Widgets(_BaseTab):
    def demo(self, parent):
        Title(parent, "Widget Playground")
        Button(parent, "Test Me", on_click=lambda: self.form.show_modal("Nice"))
```

Save the file and re-run to see your changes.

This is the normal workflow:

1) Add (or modify) entries in TAB_LAYOUT
2) Let IPUI discover or generate the file(s)
3) Edit the builder methods on your _BaseTab class
4) Save and keep going

You can define pane methods directly inside _BaseForm (as in the smoke test) or in separate files — both work seamlessly.

<!-- SCREENSHOT: ipui/assets/images/quick_start.png — the Hello World form with banner, body text, and green button -->
![QuickStart Screenshot](https://raw.githubusercontent.com/Oldwolfster/IPUI/main/src/ipui/assets/images/quick_start.png)

---

## Core Concepts

### How Tab Discovery Works

The `TAB_LAYOUT` dictionary is the blueprint for your application.
* **The Keys** define the names of your tabs.
* **The Values** are lists that divide that tab into one or more **Panes**.
* You can size panes by including a flex number (below, `chill` gets 2/3 and `None` gets 1/3)

```python
TAB_LAYOUT = {
    "Hello World"   :["welcome"     ],  # Tab 'Hello World'   with one pane 'welcome'
    "Widgets"       :["demo","demo2"],  # Tab 'Widgets'       with two panes.
    "Bouncing Ball" :["arena", None ],  # Tab 'Bouncing Ball' with one pane 'arena' and a blank Pygame area
}
```
(Note: A pane value of None creates a blank region for you to draw directly to with Pygame!)

### What Panes Do

Each pane name in your TAB_LAYOUT maps to a builder method with the exact same name.
**IPUI is highly flexible** and will look for that builder method in two places:

1. **The Main Form File** (Fastest)
Just like in SmokeTest.py, you can define the builder method directly inside your _BaseForm class. Perfect for quick prototypes.

2. **A Dedicated Tab File** (Most Scalable)
When a tab grows, you can move it to its own file. If you have a tab named "Hey There", IPUI will scan your project folder (and subfolders) for a file named Hey_There.py and HeyThere.py.
Inside that file, IPUI looks for any class inheriting from _BaseTab. The actual class name doesn't matter!

```python
# Widgets.py
from ipui import *

# The class name can be anything, as long as it inherits from _BaseTab
class TotallyWhateverNameYouWant(_BaseTab):

    # This matches the 'demo' pane in TAB_LAYOUT
    def demo(self, parent):
        Title(parent, "Hello from Widgets.py")
```

#### The Golden Rule: _BaseTab Wins

What happens if IPUI finds a demo() pane builder in both your main _BaseForm and an external Widgets.py file?

**The external** _BaseTab **file always wins**. This is deliberate. The main form is great for a fast start, but once a tab earns its own file, that file becomes the boss. If you extract a method into a new file and leave the old one behind, IPUI gracefully switches over to the new dedicated file.

#### Why the `__name__` Guard Is Necessary

Your main file should always end with:
```python
if __name__ == "__main__": show(SmokeTest)
```

Don't skip this! In a one-file setup, this standard Python guard prevents accidental re-entry during import.

#### Where Your Logic Lives

A `_BaseTab` (or tabless `_BaseForm`) doesn't have an `__init__`. **You don't write one** — IPUI raises a `TypeError` at class definition if you try. This is on purpose: it keeps the framework in charge of construction order, so by the time your code runs, everything around you is already wired.

So where does *your* code go? Two places, and the split is the whole mental model:

- **Pane methods** — build the UI. Same names you put in `TAB_LAYOUT`. Run when the pane first appears (and again on rebuild). This is where you create widgets.
- **`ip_*` hooks** — run the logic. `ip_setup` for one-time initialization, `ip_think` every frame, `ip_draw` for custom rendering, and a few more. The framework calls these; you override them.

Here's the split in one example:

```python
class BouncingBall(_BaseTab):

    def arena(self, parent):                        # ← pane method: builds the UI
        Title(parent, text="Bouncing Ball")         # Print Title
        card=Card(parent, scrollable=True)          # Create a card for codebox
        CodeBox(card,data  =__file__)               # Put Codebox in the card

    def ip_setup(self, ip):                         # ← hook: runs once, initializes state
        self.ball_x, self.ball_y   = 0.5, 0.5       # put ball in middle of screen
        self.ball_dx, self.ball_dy = 0.4, 0.3       # set ball x and y movement

    def ip_think(self, ip):                         # ← hook: runs every frame
        self.ball_x += self.ball_dx * ip.dt         # move ball * ip.dt normalizes based on fps
        self.ball_y += self.ball_dy * ip.dt         # same but in y dimension
        self.bounce_off_walls(ip.rect_pane)         # check if it needs to bounce

    def ip_draw(self, ip):                          # ← hook: custom drawing
        pos = ip.to_screen(self.ball_x,self.ball_y) # convert normalized to screen coords
        pygame.draw.circle(ip.surface, (255, 160, 40), pos, ip.scale_y(0.02))

    def bounce_off_walls(self, arena):
        if self.ball_x < 0: self.ball_dx = .4       # reverse if at left edge
        if self.ball_x > 1: self.ball_dx = -.4      # reverse if at right edge
        if self.ball_y < 0: self.ball_dy = .3       # reverse if it hit's top
        if self.ball_y > 1: self.ball_dy = -.3      # reverse if it hits bottom
```

If it lays out widgets, it goes in a pane method. If it ticks, decides, animates, or paints custom graphics, it goes in an `ip_*` hook. The full set of hooks and what each one does is covered in [Lifecycle Hooks](#lifecycle-hooks) below — for now, knowing the split exists is enough to read most IPUI code.

---

### The Philosophy

IPUI makes the right path the easy path.

- Simple things should be trivial
- Missing structure should be fixable, not fatal
- Scaling out should feel natural
- Boilerplate should be forged, not copied around by hand
- Learning should happen by playing with real, running examples

> That's why the **Full Showcase** template gives you a fully functional widget gallery — click, rearrange, copy-paste, and keep building. Start stealing code before you've written your first line.

No event loop setup. No manual sizing. No coordinate math. IPUI handles the Pygame lifecycle, layout, rendering, and event dispatch automatically.

---

### The Widget Tree

Every IPUI app is a tree. Construction attaches:

```python
card = CardCol(parent)      # attaches to parent
Title(card, "Settings")     # attaches to card
Body(card, "Change stuff")  # attaches to card
```

No `add()`. No `pack()`. No `grid()`. Construction IS attachment — an entire class of "widget exists but isn't visible" bugs is gone.

#### A Note on `build()` vs `__init__` (for custom widget authors)

You may have noticed there's no `__init__` when you write a custom widget either. That's deliberate. Override `build()` instead — by the time it runs, `self.parent`, `self.form`, and `self.children` are already wired, so you don't have to call `super().__init__()` with a maze of arguments.

```python
class MyWidget(_BaseWidget):
    def build(self):
        self.font     = Style.FONT_BODY
        self.color_bg = Style.COLOR_CARD_BG
```

Most users never need to write a custom widget — IPUI ships with a full catalog. This is here so you know where to look when the day comes.

---

## Updating the UI 

**Reactive** — Declare relationships at the top of your _BaseTab. The pipeline handles propagation:

```python
class MyPane(_BaseTab):
    BINDINGS = {
        "lbl_status": {
            "property": "text",
            "compute":  "compute_status",
            "triggers": ["training_active", "epoch"],
        },
    }

    def compute_status(self, training_active, epoch):
        if training_active:
            return f"Epoch {epoch}"
        return "Idle"
```

**Imperative** — Store widget references, call methods when things change:

```python
def build(self):
    self.lbl = Body(parent, "Idle", name="lbl_status")

def on_epoch_done(self, epoch):
    self.lbl.set_text(f"Epoch {epoch}")
```

**Hybrid** — Use the pipeline as a shared key-value store, but read it imperatively:

```python
def on_run_clicked(self):
    active = self.form.pipeline_read("training_active")
    if active:
        self.form.show_modal("Already running!")
```

Mix all three freely. The reactive approach requires less code and eliminates update-ordering bugs. Imperative gives you surgical control when you need it. The pipeline connects them.

<!-- SCREENSHOT: ipui/assets/images/reactive_pipeline.png — the Paradigm tab showing reactive vs imperative side-by-side -->

---

## The `ip` Service Portal

Every lifecycle hook receives a single argument: `ip`. It's the IPUI Service Portal — one object that gives you everything you need. Type `ip.` in your IDE and autocomplete shows every attribute and method, organized by family.

```python
class MySimulation(_BaseTab):
    def ip_think(self, ip):
        self.ball_x += self.ball_dx * ip.dt

    def ip_draw(self, ip):
        pos = ip.to_screen(self.ball_x, self.ball_y)
        r   = ip.scale_y(self.ball_r)
        pygame.draw.circle(ip.surface, (255, 160, 40), pos, r)

    def ip_draw_hud(self, ip):
        font = Style.FONT_DETAIL
        surf = font.render(f"FPS: {ip.fps}", True, Style.COLOR_TEXT_ACCENT)
        ip.surface.blit(surf, (10, 10))
```

### Identity

| Attribute          | Type        | Description |
|--------------------|-------------|-------------|
| `ip.form`          | _BaseForm   | Active Form instance |
| `ip.form_name`     | str         | Name of the active form |
| `ip.tab`           | _BaseTab    | Active Tab instance (or the form, in tabless mode) |
| `ip.tab_name`      | str         | Name of the active tab |
| `ip.is_active_tab` | bool        | Is this the visible tab? |

### Timing

| Attribute | Type | Description |
|-----------|------|-------------|
| `ip.dt` | float | Seconds since last frame |
| `ip.fps` | int | Current frames per second |
| `ip.frame` | int | Monotonically increasing frame counter |
| `ip.elapsed` | float | Total seconds since app started |

### Geometry

| Attribute | Type | Description |
|-----------|------|-------------|
| `ip.rect_pane` | Rect | Your drawing canvas — the None pane slot, or the whole pane if no None slot exists |
| `ip.rect_tab_area` | Rect | The entire tab content row (all pane slots combined) |
| `ip.rect_screen` | Rect | The full pygame surface |

Use `ip.rect_pane` for all custom rendering in `ip_draw` and `ip_draw_hud`. No need for spelunking through the widget tree — the framework finds your canvas for you.

### Coordinate Helpers

Work in normalized coordinates (0.0–1.0) and let IPUI handle the pixel math:

| Method | Description |
|--------|-------------|
| `ip.to_screen(nx, ny)` | Normalized (0–1) → screen pixel tuple within `rect_pane` |
| `ip.to_local(sx, sy)` | Screen pixels → normalized (0–1) within `rect_pane` |
| `ip.scale_x(n)` | Normalized width → pixel width |
| `ip.scale_y(n)` | Normalized height → pixel height |
| `ip.local_to_screen(x, y)` | Pane-local pixel coords → screen coords |
| `ip.screen_to_local(x, y)` | Screen coords → pane-local pixel coords |

**Before:**
```python
def draw_ball(self, surface):
    arena = self.form.tab_strip.panes[1].rect   # spelunking
    sx = arena.left + int(self.ball_x * arena.width)
    sy = arena.top  + int(self.ball_y * arena.height)
    r  = int(self.ball_r * arena.height)
    pygame.draw.circle(surface, WHITE, (sx, sy), r)
```

**After:**
```python
def draw_ball(self, ip):
    pos = ip.to_screen(self.ball_x, self.ball_y)
    r   = ip.scale_y(self.ball_r)
    pygame.draw.circle(ip.surface, WHITE, pos, r)
```

Three lines. No spelunking. No manual math. Resolution independent.

<!-- SCREENSHOT: ipui/assets/images/canvas_ball.png — PygameBall2 bouncing in the None pane with trail effect -->

### Mouse

| Attribute / Method | Type | Description |
|--------------------|------|-------------|
| `ip.mouse_x` | int | Mouse x position (screen) |
| `ip.mouse_y` | int | Mouse y position (screen) |
| `ip.mouse_pos` | tuple | Mouse (x, y) tuple |
| `ip.mouse_wheel` | int | Scroll wheel delta this frame |
| `ip.mouse_down(Mouse.LEFT)` | bool | Is the button held this frame? |
| `ip.mouse_pressed(Mouse.LEFT)` | bool | Was the button just pressed this frame? (edge detect) |
| `ip.mouse_released(Mouse.LEFT)` | bool | Was the button just released this frame? |
| `ip.mouse_inside(widget)` | bool | Is the mouse inside this widget's rect? |
| `ip.mouse_inside_pane()` | bool | Is the mouse inside `rect_pane`? |
| `ip.mouse_inside_content()` | bool | Is the mouse inside `rect_tab_area`? |
| `ip.mouse_hits(rect)` | bool | Is the mouse inside an arbitrary rect? |
| `ip.mouse_local_pos()` | tuple | Mouse position relative to `rect_pane` |
| `ip.mouse_local_pos(widget)` | tuple | Mouse position relative to a widget |
| `ip.mouse_local_x()` | int | Mouse x relative to `rect_pane` |
| `ip.mouse_local_y()` | int | Mouse y relative to `rect_pane` |

Constants: `Mouse.LEFT`, `Mouse.MIDDLE`, `Mouse.RIGHT`. Import with `from ipui import *`.

### Keyboard

| Attribute / Method | Type | Description |
|--------------------|------|-------------|
| `ip.mod_shift` | bool | Shift held? |
| `ip.mod_ctrl` | bool | Ctrl held? |
| `ip.mod_alt` | bool | Alt held? |
| `ip.key_down(Key.SPACE)` | bool | Is this key held this frame? |
| `ip.key_pressed(Key.SPACE)` | bool | Was this key just pressed this frame? |
| `ip.key_released(Key.SPACE)` | bool | Was this key just released this frame? |

Constants live on the `Key` class — autocomplete shows everything. Examples:
`Key.LEFT`, `Key.RIGHT`, `Key.UP`, `Key.DOWN`, `Key.SPACE`, `Key.RETURN`, `Key.ESCAPE`,
`Key.TAB`, `Key.BACKSPACE`, `Key.A`–`Key.Z`, `Key.NUM_0`–`Key.NUM_9`, `Key.F1`–`Key.F12`,
`Key.HOME`, `Key.END`, `Key.PAGEUP`, `Key.PAGEDOWN`, `Key.DELETE`.

### Rendering

| Attribute | Type | Description |
|-----------|------|-------------|
| `ip.surface` | Surface | The pygame draw surface |
| `ip.events` | list | All pygame events this frame |
| `ip.unhandled` | list | Events the UI did not consume |

### Cache

A simple key-value scratch pad. Persists across frames but has **no connection** to the reactive pipeline — it does not trigger derives or update widgets.

| Method | Description |
|--------|-------------|
| `ip.cache_get(key, default=None)` | Read a value |
| `ip.cache_set(key, value)` | Store a value |
| `ip.cache_has(key)` | Check if key exists |
| `ip.cache_del(key)` | Remove a key |

For reactive state, use `self.form.pipeline_set()` / `self.form.pipeline_read()`. For scratch data (animation counters, drag state, accumulators), use `ip.cache`.

### Discovery

| Method | Description |
|--------|-------------|
| `ip.find("widget_name")` | Locate a widget by name. Returns widget or None |
| `ip.help()` | Print a guided tour of the full API |
| `ip.help("mouse")` | Print help for a specific topic |

Help topics: `identity`, `timing`, `geometry`, `mouse`, `keyboard`, `render`, `cache`, `redraw`, `discover`.

### Invalidation (scaffolded for future optimization)

| Method | Description |
|--------|-------------|
| `ip.request_redraw()` | Mark pane as needing repaint |
| `ip.request_layout()` | Mark pane as needing layout recalc |

Currently IPUI renders every frame, so these are effectively no-ops. They exist so your code will work unchanged when dirty-flag optimization lands.

---
### State Machine

`ip.state` is a built-in state machine available everywhere — panes, forms, hooks. Each state pairs a **name** with a **delegate** (a method to run while in that state). States can chain to a follow-up state and auto-advance after a duration.

The state machine tracks *what* state you're in. Drawing a flash overlay or a "GAME OVER" message is your job — the state machine just tells you which one to draw.

**Register states with `add()`, transition with `go()`:**

```python
class Breakout(_BaseTab):
    def ip_setup(self, ip):
        ip.state.add("DEMO"     , self.state_demo)
        ip.state.add("READY"    , self.state_ready)
        ip.state.add("PLAYING"  , self.state_playing)
        ip.state.add("LEVEL_UP" , None,    "READY",     1.5)   # auto-advance after 1.5s
        ip.state.add("GAME_OVER", None,    "DEMO",      2.5)   # auto-advance after 2.5s
        ip.state.go("DEMO")

    def state_demo(self):       ...    # called every frame while in DEMO
    def state_ready(self):      ...    # called every frame while in READY
    def state_playing(self):    ...    # called every frame while in PLAYING
```

When a state has a duration, the engine counts down automatically and transitions to the named follow-up state when the timer expires. A `None` delegate means "do nothing this frame" — useful for pure timed transitions like flash messages where your draw code reads `ip.state.current` and renders accordingly.

**API:**

| Method / Property | Description |
|-------------------|-------------|
| `ip.state.add(name, delegate, next=None, duration=0)` | Register a state |
| `ip.state.go(name, duration=None)` | Transition to a state (override duration optional) |
| `ip.state.next()` | Follow the registered chain to the next state |
| `ip.state.is_("NAME")` | True if current state matches |
| `ip.state.current` | Current state name (or None) |

**Branch your logic on the current state:**

```python
def ip_think(self, ip):
    if ip.state.is_("READY"):
        if ip.mouse_pressed(Mouse.LEFT):
            ip.state.go("PLAYING")
        return

    if ip.state.is_("PLAYING"):
        self.run_physics(ip)
```

**Multiple state machines** — the default covers most cases, but named machines are available:

```python
ip.state("combat").add("IDLE", self.combat_idle)
ip.state("combat").go("IDLE")
ip.state("ui").go("MENU_OPEN")
```

`ip.state` and `ip.state()` both return the default machine. `ip.state("name")` returns a named one, created on first access.

> **🚧 Coming soon:** declarative state config via a `STATES` class dict and `ip.state.configure(self.STATES)`, plus `ip.state.in_("A", "B")` for multi-name membership tests.

---

## Lifecycle Hooks

IPUI gives you five hooks into the application lifecycle. Each one fires at a specific moment, has a clear job, and works identically whether you're on a `_BaseTab` or a `_BaseForm`.

### The Five Hooks

**`ip_setup(self, ip)`** — Runs once, when the pane or form is first created. Initialize your state here: positions, velocities, counters, loaded assets, state machine configuration. By the time this fires, `self.form`, `self.ip`, and the widget tree are fully wired.

```python
def ip_setup(self, ip):
    self.ball_x  = 0.5
    self.ball_y  = 0.5
    self.speed   = 0.4
    self.score   = 0
    ip.state.add("READY"  , self.state_ready)
    ip.state.add("PLAYING", self.state_playing)
    ip.state.go("READY")
```

**`ip_activated(self, ip)`** — Runs every time this pane or form becomes visible. On a `_BaseTab`, this fires when the user switches to your tab, and also on the initial load after `ip_setup`. On a `_BaseForm`, this fires when `IPUI.show()` or `IPUI.back()` brings the form to the front.

Use it to refresh data that might have changed while you were off-screen, restart animations, or sync state from the pipeline.

```python
def ip_activated(self, ip):
    self.refresh_leaderboard()
    self.resume_particle_effects()
```

> **Note on `ip` inside `ip_activated`:** Identity (`ip.form`, `ip.tab`, `ip.tab_name`, `ip.is_active_tab`) and geometry (`ip.rect_pane`, `ip.rect_tab_area`) are correct when this hook fires. Per-frame fields like `ip.dt`, `ip.events`, and `ip.surface` reflect the *last* completed frame — `ip_activated` runs at lifecycle transitions, not inside the per-frame loop, so use the per-frame fields with care here.

**`ip_think(self, ip)`** — Runs every frame. This is your logic tick: state machines, physics, AI, input polling, data checks. No drawing here — just thinking.

By default, `ip_think` only fires on the active pane. Set `THINK_ALWAYS = True` on your `_BaseTab` subclass if you need background processing even when the tab isn't visible (useful for simulations that shouldn't pause when the user switches tabs).

```python
def ip_think(self, ip):
    if ip.state.is_("PLAYING"):
        self.ball_x += self.ball_dx * ip.dt
        self.ball_y += self.ball_dy * ip.dt
        if self.ball_y > 1.0:
            ip.state.go("GAME_OVER")
```

**`ip_draw(self, ip)`** — Runs every frame, before the widget tree draws. This is where you paint game worlds, backgrounds, visualizations — anything that should appear behind your widgets.

```python
def ip_draw(self, ip):
    pos = ip.to_screen(self.ball_x, self.ball_y)
    r   = ip.scale_y(self.ball_r)
    pygame.draw.circle(ip.surface, (255, 160, 40), pos, r)
```

**`ip_draw_hud(self, ip)`** — Runs every frame, after the widget tree draws. Overlays, cursors, FPS counters, debug text — anything that should appear on top of everything else.

```python
def ip_draw_hud(self, ip):
    font = Style.FONT_DETAIL
    surf = font.render(f"FPS: {ip.fps}", True, Style.COLOR_TEXT_ACCENT)
    ip.surface.blit(surf, (10, 10))
```

### Execution Order

Every frame follows this sequence:

```
ip_think       →  your logic runs
Layout pass    →  widget tree measures and positions
ip_draw        →  you paint behind the widgets
Widget render  →  the UI draws itself
ip_draw_hud    →  you paint on top of everything
```

`ip_setup` and `ip_activated` are not per-frame — they fire at lifecycle transitions.

### Using Hooks on a Pane

Override any hook directly on your `_BaseTab` subclass:

```python
class BouncingBall(_BaseTab):
    def ip_setup(self, ip):
        self.x, self.y   = 0.5, 0.5
        self.dx, self.dy = 0.4, 0.3

    def ip_activated(self, ip):
        self.x, self.y   = 0.5, 0.5      # reset position on tab switch

    def ip_think(self, ip):
        self.x += self.dx * ip.dt
        self.y += self.dy * ip.dt
        if self.x < 0 or self.x > 1: self.dx = -self.dx
        if self.y < 0 or self.y > 1: self.dy = -self.dy

    def ip_draw(self, ip):
        pos = ip.to_screen(self.x, self.y)
        pygame.draw.circle(ip.surface, (255, 160, 40), pos, ip.scale_y(0.02))

    def ip_draw_hud(self, ip):
        surf = Style.FONT_DETAIL.render(f"FPS: {ip.fps}", True, Style.COLOR_TEXT_ACCENT)
        ip.surface.blit(surf, (10, 10))
```

### Using Hooks on a Form

Override on your `_BaseForm` subclass for app-wide logic. Form hooks fire in addition to pane hooks — the form thinks first, then the active pane thinks.

```python
class MyApp(_BaseForm):
    def ip_setup(self, ip):
        self.global_timer = 0

    def ip_activated(self, ip):
        # Fires when IPUI.show() brings this form to the front
        self.refresh_global_state()

    def ip_think(self, ip):
        self.global_timer += ip.dt
```

Render hooks (`ip_draw`, `ip_draw_hud`) only fire on the active pane — no point drawing to a tab nobody can see.

### Background Processing

By default, `ip_think` only fires on the visible pane. If your pane runs a simulation or background process that shouldn't pause when the user switches tabs, opt in:

```python
class TrainingMonitor(_BaseTab):
    THINK_ALWAYS = True

    def ip_think(self, ip):
        if not ip.is_active_tab:
            self.training_step()     # keep training even when not visible
            return
        self.update_charts()         # only update visuals when visible
```

### Quick Reference

| Hook            | Receives `ip`? | When it fires                             | Fires on inactive pane?           |
|-----------------|----------------|-------------------------------------------|-----------------------------------|
| `ip_setup`      | Yes            | Once, at creation                         | N/A — only fires once             |
| `ip_activated`  | Yes            | Each time pane/form becomes visible       | N/A — fires on activation         |
| `ip_think`      | Yes            | Every frame                               | Only with `THINK_ALWAYS = True`   |
| `ip_draw`       | Yes            | Every frame, before widgets               | Active pane only                  |
| `ip_draw_hud`   | Yes            | Every frame, after widgets                | Active pane only                  |

---

## Widget Catalog

### Text Hierarchy

IPUI scales text proportionally to your physical screen. You pick semantic roles, not font sizes:

| Widget    | Purpose                           | Example                                    |
|-----------|-----------------------------------|--------------------------------------------|
| `Banner`  | App title.                        | `Banner(parent, "NeuroForge", glow=True)`  |
| `Title`   | Pane/section header.              | `Title(parent, "Settings", glow=True)`     |
| `Heading` | Subsection label.                 | `Heading(parent, "Hyperparams:")`          |
| `Body`    | The workhorse. Most text is this. | `Body(parent, "Configure your model.")`    |
| `Detail`  | Fine print, timestamps.           | `Detail(parent, "Last updated: 2:30pm")`   |

All text widgets support `glow=True` (molten-orange forge effect) and `text_align=CENTER` or `RIGHT`.

### Layout Containers

| Widget    | Direction  | Chrome          | Usage                                    |
|-----------|------------|-----------------|------------------------------------------|
| `Row`     | Horizontal | None            | `Row(parent, justify_spread=True)`       |
| `Col`     | Vertical   | None            | `Col(parent)`                            |
| `CardRow` | Horizontal | Beveled, filled | `CardRow(parent, width_flex=1)`       |
| `CardCol` | Vertical   | Beveled, filled | `CardCol(parent, scrollable=True)`       |
| `Card`    | Vertical   | Beveled, filled | `Card(parent, height_flex=1)`         |

`Row`/`Col` are invisible structure. `CardRow`/`CardCol`/`Card` have a background and beveled edges.

### Interactive Widgets

**Button**
```python
Button(parent, "Launch",
    color_bg = Style.COLOR_BUTTON_CTA,
    on_click = self.launch_training,
    width_flex = 2)
```
Automatic hover brightening, press bevel inversion, disabled dimming using HSL math.
> Note:  Automatically generating hover/disabled colors saves a lot of work but isn't always perfect.
> You can always override the automatically generated colors.

**TextBox**
```python
TextBox(parent,
    placeholder  = "Enter learning rate",
    pipeline_key = "learning_rate",
    on_change    = self.rate_changed)
```
With `pipeline_key`, writes to the pipeline on every keystroke. With `on_change`, you get a callback too. Use both, either, or neither.

**SelectionList**
```python
SelectionList(parent,
    data          = {"SGD": {...}, "Adam": {...}, "RMSProp": {...}},
    pipeline_key  = "optimizer",
    single_select = True,
    on_change     = self.optimizer_changed)
```

**DropDown**
```python
DropDown(parent,
    data          = {"SGD": {}, "Adam": {}, "RMSProp": {}},
    pipeline_key  = "optimizer",
    single_select = True)
```

**PowerGrid**
```python
grid = PowerGrid(parent, name="results_grid")
grid.set_data(rows, columns=["Run", "Accuracy", "Loss"])
grid.set_column_max("Run", 200)
grid.set_page_size(50)
grid.on_row_click(self.on_row_selected, column="Run")
```

PowerGrid also accepts SQL databases directly:

```python
grid.set_data("path/to/database.db",
    query="SELECT run_id, accuracy FROM batch_history ORDER BY accuracy DESC")
```

Or load an entire table:

```python
grid.set_data("path/to/database.db", table="batch_history")
```

Sorting works across pages — sort the full dataset, then paginate the sorted result.

<!-- SCREENSHOT: ipui/assets/images/powergrid_sql.png — PowerGrid with sorted columns showing SQL data -->

**Chart**
```python
chart = Chart(parent, width_flex=1, height_flex=1)
chart.set_data(
    lines   = {"Train Loss": [(0, 0.9), (1, 0.7), (2, 0.5)],
               "Val Loss":   [(0, 0.95),(1, 0.75),(2, 0.6)]},
    x_label = "Epoch",
    y_label = "Loss"
)
```

---

## Layout System

IPUI uses a flex-inspired layout. Set `width_flex` or `height_flex` to a weight; the remaining space is distributed proportionally:

```python
row = Row(parent)
Col(row, width_flex=1)   # gets 1/3 of width
Col(row, width_flex=2)   # gets 2/3 of width
```

Unset (or `0`) means the widget takes its natural size. No explicit pixel math required.

**Scrollable containers:**
```python
CardCol(parent, scrollable=True, height_flex=1)
```
Scrollable containers clip and scroll their children automatically. Scrollbars support both mouse wheel and click-and-drag.

---

## Tabs and Panes

Tab layout is declared in one dict on your form:

```python
class MyApp(_BaseForm):
    TAB_LAYOUT = {
        "Config":  ["settings", "hyperparams"],
        "Results": ["chart",    "grid"],
        "Log":     ["log"],
    }
```

Each value is a list of method names. IPUI discovers the corresponding `_BaseTab` subclass by tab name (matching a Python file in the same directory), calls those methods to build each pane, and arranges them side-by-side.

```python
# Config.py
class Config(_BaseTab):
    def settings(self, parent):
        Title(parent, "Settings")
        ...

    def hyperparams(self, parent):
        Title(parent, "Hyperparameters")
        ...
```

### Canvas Panes

Use `None` in the pane list to create a transparent, chrome-free drawing canvas:

```python
TAB_LAYOUT = {
    "Game": ["controls", None, "scoreboard"],
}
```

The `None` slot becomes `ip.rect_pane` — your game's arena. Draw in `ip_draw`, read mouse position with `ip.mouse_local_x()`, convert coordinates with `ip.to_screen()`. Zero framework spelunking required.

<!-- SCREENSHOT: ipui/assets/images/breakout_canvas.png — Breakout game running in the None pane with bricks, paddle, and ball -->

### Pane Weights

Control relative pane widths with tuples:

```python
TAB_LAYOUT = {
    "Dashboard": [("sidebar", 1), ("main", 3)],
}
```

Bare strings default to weight 1. Mix freely: `["info", ("detail", 3)]`.

### Cross-Tab Pane Sharing

Reuse pane methods from other tabs with dot notation:

```python
TAB_LAYOUT = {
    "Armory":  ["match_hints", "match_settings", None],
    "Pro":     ["Armory.match_settings", "Forge.workbench", "Forge.preview"],
}
```

### Tab Control at Runtime

```python
self.form.switch_tab("Results")
self.form.hide_tab("Log")
self.form.show_tab("Log")
self.form.set_pane(1, self.rebuild_results)
self.form.refresh_pane(1)
```

**Early-load tabs** (pre-built at startup instead of on first click):

```python
class MyApp(_BaseForm):
    tab_early_load = ["Config", "Results"]
```

**Hidden tabs** (initially hidden, shown later via `show_tab`):

```python
class MyApp(_BaseForm):
    tab_hidden = ["Colosseum"]
```

### Guarding Tab Switches with `tab_on_change`

Sometimes you need to *block* a tab switch — for example, "the user hasn't picked a project yet, so don't let them leave Home." That's the job of `tab_on_change`.

Set `tab_on_change` to the **name of a method on your form**. IPUI calls it *before* every tab switch and lets it veto the change by returning `False`:

```python
class FormNeuroForge(_BaseForm):
    TAB_LAYOUT     = {"Home": ["..."], "Forge": ["..."], "Pro": ["..."]}
    tab_on_change  = "guard_tab_switch"

    def guard_tab_switch(self, name, current):
        if current == "Home" and not self.has_active_project():
            self.show_modal("Pick a project first!")
            return False           # ← veto: tab does NOT switch
        return True                 # ← allow the switch
```

**Signature:** `method(name, current)` — `name` is the destination tab, `current` is the tab the user is leaving.

**Return value:**
- `False` → veto. The tab strip stays where it is. No `ip_activated` fires.
- Any other value (`True`, `None`, missing return) → switch proceeds normally.

This is a different superpower from `ip_activated`. `tab_on_change` is a **gate** — it can stop a switch before it happens. `ip_activated` is a **welcome mat** — it runs after the switch is already in motion. Both can coexist on the same form.

For the full lifecycle of a tab switch — including exactly when each hook fires — see [Appendix C](#appendix-c-tab-switch-lifecycle).



---
## Tabless Mode

Not every app needs tabs. Games, visualizations, single-screen tools — sometimes you just want a window and some widgets.

Skip `TAB_LAYOUT` entirely. Build widgets in `build()`. Use the same lifecycle hooks you already know.

---

### Minimal Example

    from ipui import *

    class MyApp(_BaseForm):
        def build(self):
            Banner(self, "My App", glow=True, text_align=CENTER)
            Title(self, "No tabs. No panes. Just widgets.", text_align=CENTER)
            Body(self, "Everything lives right here.", text_align=CENTER)
            Button(self, "Do Something",
                color_bg=Style.COLOR_BUTTON_CTA,
                on_click=self.do_something)

        def do_something(self):
            self.show_modal("It works!")

    if __name__ == "__main__":
        show(MyApp)

No `TAB_LAYOUT`. No `_BaseTab`. One class, one file, name it whatever you want.

---

### Using Lifecycle Hooks

The same hooks work on a tabless form as on any `_BaseTab` pane:

    from ipui import *
    import pygame

    class Asteroids(_BaseForm):
        def build(self):
            self.lbl_score = Title(self, "Score: 0")

        def ip_setup(self, ip):
            self.ship_x  = 0.5
            self.ship_y  = 0.5
            self.speed   = 0.4
            self.bullets = []
            ip.state.add("READY"    , self.state_ready)
            ip.state.add("PLAYING"  , self.state_playing)
            ip.state.add("GAME_OVER", None, "READY", 2.5)
            ip.state.go("READY")

        def state_ready(self):    pass
        def state_playing(self):  pass

        def ip_think(self, ip):
            if ip.state.is_("PLAYING"):
                self.ship_x += self.speed * ip.dt
                self.lbl_score.set_text(f"Score: {len(self.bullets)}")

        def ip_draw(self, ip):
            pos = ip.to_screen(self.ship_x, self.ship_y)
            pygame.draw.circle(ip.surface, (255, 160, 40), pos, ip.scale_y(0.02))

        def ip_draw_hud(self, ip):
            font = Style.FONT_DETAIL
            surf = font.render(f"FPS: {ip.fps}", True, Style.COLOR_TEXT_ACCENT)
            ip.surface.blit(surf, (10, 10))

    if __name__ == "__main__":
        show(Asteroids)

Every hook — `ip_setup`, `ip_activated`, `ip_think`, `ip_draw`, `ip_draw_hud` — works identically whether it lives on a `_BaseForm` or a `_BaseTab`. Move code between the two freely.

---

### When to Use Tabless vs Tabbed

| Scenario | Approach |
|----------|----------|
| Quick prototype, single screen | Tabless — one class, `build()` |
| Game or visualization | Tabless — full hook access, no tab chrome |
| Multi-view app | Tabbed — `TAB_LAYOUT` with `_BaseTab` files |
| One-file demo with tabs | Tabbed — builder methods on the form |

Tabless is the on-ramp. Tabs are the highway. Both use the same engine.

---

### Layout Without Panes

In tabbed mode, panes give you automatic side-by-side columns. In tabless mode, use `Row` and `Col` directly:

    class Dashboard(_BaseForm):
        def build(self):
            row = Row(self, width_flex=1, height_flex=1)

            sidebar = CardCol(row, width_flex=1)
            Title(sidebar, "Controls")
            Button(sidebar, "Reset", on_click=self.reset)

            main = CardCol(row, width_flex=3)
            Title(main, "Output")
            self.lbl_result = Body(main, "Ready")

You get the same layout flexibility — just with explicit containers instead of pane slots.

---

## Reactive Pipeline

The pipeline is a centralized key-value store. Write to it, and any widget that declared a dependency is automatically updated:

```python
# Write
self.form.pipeline_set("training_active", True)

# Read
active = self.form.pipeline_read("training_active")
```

Declare widget reactions in `BINDINGS` at the top of your _BaseTab:

```python
class TrainingPane(_BaseTab):
    BINDINGS = {
        "btn_start": {
            "property": "enabled",
            "compute":  "compute_start_enabled",
            "triggers": ["training_active", "config_valid"],
        },
        "lbl_epoch": {
            "property": "text",
            "compute":  "compute_epoch_label",
            "triggers": ["epoch"],
        },
    }

    def compute_start_enabled(self, training_active, config_valid):
        if training_active:
            return "Training in progress"   # disabled with tooltip reason
        return True                         # enabled

    def compute_epoch_label(self, epoch):
        return f"Epoch: {epoch}"
```

Each entry maps a widget name (`name=` parameter) → property → compute method → trigger keys. When any trigger key changes, the compute method runs and the property is updated. No manual wiring. No update-ordering bugs.

The pipeline also pushes values back to source widgets — if you call `pipeline_set("my_key", "")`, any TextBox with `pipeline_key="my_key"` updates its displayed text automatically.

**Seeding initial values:** declare `PIPELINE_DEFAULTS` on your form to populate the pipeline at startup:

```python
class MyApp(_BaseForm):
    PIPELINE_DEFAULTS = {
        "training_active": False,
        "epoch":           0,
        "config_valid":    True,
    }
```

---

## Imperative Approach

Store widget references and drive them yourself:

```python
class MyPane(_BaseTab):
    def widgets(self, parent):
        self.lbl_count = Body(parent, "0 selected", name="lbl_count")
        self.btn_run   = Button(parent, "Run",
                             color_bg = Style.COLOR_BUTTON_CTA,
                             on_click = self.on_run)

    def on_selection_changed(self, count):
        self.lbl_count.set_text(f"{count} selected")
        if count == 0:
            self.btn_run.set_disabled("Select at least one item")
        else:
            self.btn_run.set_enabled()
```

Access named widgets from anywhere via `self.form.widgets["widget_name"]`.

---

> 🧠 **The IPUI Philosophy: Engineering for Fitts's Law**
> IPUI doesn't just put pixels on the screen; it optimizes for the human hand and eye. Every interaction is designed to minimize cognitive load and physical movement.
>
> 🎯 **The Prime Pixel & The Zero-Distance Pin**
> We leverage **Fitts's Law** — which states that the time to acquire a target is determined by **distance** and **size** — to make your workflow feel instantaneous.
>
> - **The Prime Pixel:** Our "Super Tips" utilize the most valuable real estate on your screen: the pixel where your cursor already sits.
> - **Zero-Distance Acquisition:** By spawning the **Pin** button directly under the mouse after a brief *intent delay*, we reduce the movement distance (D) to **zero**. This makes pinning information a *near-instant* action.
>
> ⏲️ **Temporal Guardrails**
> To prevent accidental interactions (misclicks), IPUI implements **Temporal Buffering**:
>
> - **Hover State (1.5s):** Standard tooltip appears — non-invasive and follows the mouse.
> - **Engagement (0.5s):** The Super Tip expands, providing deep contextual data.
> - **Action Readiness (0.5s later):** The **Pin** button manifests. This staggered entry ensures that a click meant for the underlying button isn't accidentally "stolen" by the tooltip.

<!-- SCREENSHOT: ipui/assets/images/super_tooltip.png — Super Tooltip showing hover → expand → pin sequence -->

---

## Construction-Time Safety

IPUI catches mistakes when you make them, not when users hit them:

| Mistake                                   | Error raised                               |
|-------------------------------------------|--------------------------------------------|
| Override `__init__` in a widget           | `TypeError` at class definition            |
| Override `__init__` in a pane             | `TypeError` at class definition            |
| `justify_center` AND `justify_spread`     | `ValueError` at construction               |
| `text_align='x'`                          | `ValueError` at construction               |
| `widgets["typo"]`                         | `RuntimeError` listing valid names         |
| `on_click_me(non_callable)`               | `TypeError` at registration                |
| `on_click_me(func_with_params)`           | `ValueError` at registration               |

IPUI Error messages stand out by always starting: `Houston we have a problem!`

---

## Styling and Theming

All styling lives in `Style`. Import and use constants — don't hard-code colors or sizes:

```python
from ipui import Style

Button(parent, "Go", color_bg=Style.COLOR_BUTTON_CTA)
Body(parent,   "Status", font=Style.FONT_BODY)
```

**Color constants:** `COLOR_BACKGROUND`, `COLOR_MODAL_BG`, `COLOR_PANEL_BG`, `COLOR_CARD_BG`, `COLOR_TEXT`, `COLOR_TEXT_SECONDARY`, `COLOR_TEXT_MUTED`, `COLOR_TEXT_ACCENT`, `COLOR_BORDER`, `COLOR_BORDER_SUBTLE`, `COLOR_BUTTON_BG`, `COLOR_BUTTON_CTA` (green), `COLOR_BUTTON_DANGER` (red), `COLOR_BUTTON_SECONDARY` (blue), `COLOR_BUTTON_ACCENT` (orange), `COLOR_BUTTON_WARNING`, `COLOR_CODE_BG`

**Font constants:** `FONT_BANNER`, `FONT_TITLE`, `FONT_HEADING`, `FONT_BODY`, `FONT_DETAIL`, `FONT_MONO`

**Tokens:** `TOKEN_PAD`, `TOKEN_PAD_TIGHT`, `TOKEN_GAP`, `TOKEN_GAP_TIGHT`, `TOKEN_BORDER`, `TOKEN_SCROLLBAR`, `TOKEN_CORNER_RADIUS`

**Screen:** `SCREEN_WIDTH` (default 1900), `SCREEN_HEIGHT` (default 900), `FONT_SCALE` (default 0.369)

---

## Debug Tools

IPUI ships with built-in developer tools so you never have to guess what the layout engine is doing.

**F12 — Professional Grade Debug Tools**

Press F12 to open the IPUI X-Ray. Tabs include:

- **Tree** — Live view of every widget: flex settings, minimum sizes, actual rects. Click any row to inspect all properties. Copy the full tree to clipboard for sharing.
- **Magic** — Live view of all reactive pipeline keys, values, and registered derives.
- **Reference** — Searchable framework documentation with table of contents, built from the source code itself.
- **Layout** — Layout debugging surface (under active development).
- **Overlay** — Diagnostic overlay controls.

<!-- SCREENSHOT: ipui/assets/images/widget_tree_debug.png — F12 debug mode showing the live widget tree inspector -->

**F11 — Layout Overlay**

Press F11 to toggle a translucent overlay that draws every widget's rect directly on your running app. Instantly see padding, gaps, and alignment without opening the inspector.

<!-- SCREENSHOT: ipui/assets/images/layout_overlay.png — F11 layout overlay showing widget rects -->

Both tools work on any IPUI app with zero setup — no flags, no config, no imports.

---

## Launching Your App

```python
import ipui
from myapp import MyApp

ipui.show(MyApp, "My Application")
```

`ipui.show()` starts the Pygame loop on the first call. On subsequent calls (from within a running app) it switches the active form — letting you navigate between entirely different screens. Use `ipui.back()` to return to the previous form.

---

## API Reference

### BaseForm Class Attributes

| Attribute            | Type   | Description                                         |
|----------------------|--------|-----------------------------------------------------|
| `TAB_LAYOUT`         | dict   | Tab name → list of pane method names                |
| `PIPELINE_DEFAULTS`  | dict   | Initial pipeline keys/values seeded at form creation |
| `tab_early_load`     | list   | Tab names to pre-build at startup                   |
| `tab_on_change`      | str    | Name of method on this form to call before every tab switch. Signature: `method(name, current)`. Return `False` to veto the switch. |
| `tab_hidden`         | list   | Tab names initially hidden                          |
| `tab_border`         | int    | Tab strip border override                           |
| `pipeline_debug`     | bool   | Log all pipeline activity to console                |

### BaseForm Methods

| Method                                                          | Description                                |
|-----------------------------------------------------------------|--------------------------------------------|
| `pipeline_set(key, value)`                                      | Write to pipeline; triggers derived updates |
| `pipeline_read(key)`                                            | Read current pipeline value                |
| `switch_tab(name)`                                              | Switch to named tab                        |
| `set_pane(index, builder, *args, tab_name=None, weight=None, **kwargs)` | Replace pane content at runtime |
| `refresh_pane(index)`                                           | Rebuild current pane from its existing builder |
| `hide_tab(name)`                                                | Hide a tab button                          |
| `show_tab(name)`                                                | Show a hidden tab button                   |
| `get_tab(name)`                                                 | Return cached _BaseTab instance            |
| `prepare(name)`                                                 | Force-load a tab's _BaseTab                |
| `show_modal(msg, min_seconds=2, work_func=None)`                | Show modal message; optionally run `work_func` while displayed for at least `min_seconds` |
| `ip_think(ip)`                                                  | Per-frame logic hook (override for app-wide state) |
| `ip_draw(ip)`                                                   | Pre-render hook (override for backgrounds) |
| `ip_draw_hud(ip)`                                               | Post-render hook (override for overlays)   |

### _BaseWidget Constructor Parameters

All widgets accept these parameters:

| Parameter        | Type     | Default      | Description                                   |
|------------------|----------|--------------|-----------------------------------------------|
| `parent`         | widget   | —            | Parent widget (auto-attaches on construction) |
| `text`           | str      | None         | Display text                                  |
| `name`           | str      | None         | Registers widget in `form.widgets`            |
| `width_flex`     | int      | 0            | Flex weight horizontal (0 = natural size)     |
| `height_flex`    | int      | 0            | Flex weight vertical (0 = natural size)       |
| `pad`            | int      | TOKEN_PAD    | Internal padding                              |
| `gap`            | int      | TOKEN_GAP    | Gap between children                          |
| `border`         | int      | TOKEN_BORDER | Chrome border thickness                       |
| `justify_center` | bool     | False        | Center children in available space            |
| `justify_spread` | bool     | False        | Spread children evenly                        |
| `visible`        | bool     | True         | Show/hide widget                              |
| `enabled`        | bool/str | True         | False or reason string to disable             |
| `font`           | Font     | None         | Override font                                 |
| `text_align`     | str      | LEFT         | LEFT, RIGHT, CENTER                           |
| `color_bg`       | tuple    | None         | Background RGB tuple                          |
| `glow`           | bool     | False        | Molten-orange glow effect                     |
| `data`           | any      | None         | Arbitrary data payload                        |
| `single_select`  | bool     | False        | Enforce single selection (lists/dropdowns)    |
| `placeholder`    | str      | None         | TextBox placeholder text                      |
| `initial_value`  | any      | None         | Starting value                                |
| `on_submit`      | callable | None         | Submit callback                               |
| `on_change`      | callable | None         | Change callback                               |
| `on_click`       | callable | None         | Click callback                                |
| `on_double_click`| callable | None         | Double-click callback                         |
| `wrap`           | bool     | False        | Allow text wrapping when width-constrained    |
| `tab_order`      | int      | None         | Focus order for keyboard navigation           |
| `early_load`     | bool     | None         | Pre-build at startup instead of on-demand     |
| `pipeline_key`   | str      | None         | Pipeline read/write key                       |
| `tooltip_class`  | class    | None         | Custom tooltip class                          |
| `scrollable`     | bool     | False        | Enable scrolling for this container           |
| `scroll_glow`    | float    | 0.369        | Scrollbar bevel intensity (0 = flat)          |
| `start`          | str      | None         | CodeBox: start-of-range marker                |
| `end`            | str      | None         | CodeBox: end-of-range marker                  |
| `fit_content`    | bool     | False        | Size to content width instead of stretching   |
| `border_radius`  | int      | None         | Rounded corner radius (pixels)                |

### _BaseWidget Methods

| Method                    | Description                                       |
|---------------------------|---------------------------------------------------|
| `set_text(text)`          | Update text and rebuild layout                    |
| `set_disabled(reason="")` | Disable with optional hover-tooltip reason        |
| `set_enabled()`           | Re-enable widget                                  |
| `clear_children()`        | Remove all child widgets                          |
| `on_click_me(callback)`   | Register validated click handler (zero-arg)       |
| `tap(func)`               | Run `func(self)` and return self — inline post-construction helper |
| `display_name`            | Property: human-readable identity (name → text → type) |

### _BaseTab

| Attribute             | Type   | Description                                  |
|-----------------------|--------|----------------------------------------------|
| `BINDINGS` | dict   | Reactive derive declarations (see below)     |
| `THINK_ALWAYS`        | bool   | If True, `ip_think` fires even when this pane isn't visible |

**Lifecycle hooks** (override on your pane):

| Method                | Description                                            |
|-----------------------|--------------------------------------------------------|
| `ip_setup(ip)`        | One-time setup (runs once when pane is first created)  |
| `ip_activated(ip)`    | Each time the pane becomes visible                     |
| `ip_think(ip)`        | Per-frame logic. State, physics, AI.                   |
| `ip_draw(ip)`         | Draw before UI. Game worlds, backgrounds.              |
| `ip_draw_hud(ip)`     | Draw after UI. Overlays, cursors, effects.             |

**BINDINGS entry format:**
```python
"widget_name": {
    "property": "text",          # or "enabled", or any widget attribute
    "compute":  "method_name",   # method on this _BaseTab
    "triggers": ["key1", "key2"] # pipeline keys that trigger recompute
}
```

### SelectionList Methods

| Method                | Description                              |
|-----------------------|------------------------------------------|
| `get_selected()`      | List of selected item names              |
| `get_selected_data()` | Dict of selected items with their data   |
| `set_filter(text)`    | Filter visible items by text             |
| `sync_from_pipeline()`| Sync selection state from pipeline       |
| `selected_count`      | Property: number of selected items       |

### DropDown Methods

| Method                | Description                              |
|-----------------------|------------------------------------------|
| `get_selected()`      | List of selected item names              |
| `get_selected_data()` | Dict of selected items with their data   |
| `set_filter(text)`    | Filter visible items                     |
| `set_max_visible(n)`  | How many rows show when dropped down     |
| `sync_from_pipeline()`| Sync from pipeline and update textbox    |

### Chart Methods

| Method                              | Description                           |
|-------------------------------------|---------------------------------------|
| `set_data(lines, x_label, y_label)` | Update chart data (dirty-flag render) |

### PowerGrid Methods

| Method                                  | Description                                            |
|-----------------------------------------|--------------------------------------------------------|
| `set_data(data, columns=None)`          | Set grid data (list of lists, list of dicts, or dict of lists) |
| `set_data(path, query="...")`           | Load from SQLite database with a query                 |
| `set_data(path, table="...")`           | Load an entire SQLite table                            |
| `set_column_max(col, max_width)`        | Cap a column's pixel width (accepts index or column name) |
| `set_page_size(n)`                      | Set rows per page (0 = no pagination)                  |
| `on_row_click(callback, column=None)`   | Register row click. `column=None` → dict of row, `"name"` → that value, `int` → that index |

---

## Dependencies

- Python 3.10+
- pygame-ce
- matplotlib (for Chart)

---

## Appendix A: Detail of Single Pass Cycle
══════════════════════════════════════════════════════════════════
IPUI WIDGET LIFECYCLE — SINGLE-PASS: BUILD → MEASURE → LAYOUT → DRAW
══════════════════════════════════════════════════════════════════

Every frame, the widget tree executes four phases top-down:

1. BUILD    Constructor calls build(). Each widget creates its own
            content (surfaces, child widgets). Runs once at creation,
            and again on set_text() or other state changes.

2. MEASURE  Parent asks each child: "how big do you want to be?"
            Returns (width, height) based on the surface built in step 1.
            Flex children (width_flex/height_flex > 0) skip this —
            their size comes from leftover space, not intrinsic content.

3. LAYOUT   Parent assigns each child a rect. For vertical stacks:
            width = parent's inner width, height = measured or flex.
            This is where measure_constrained() enables text wrapping —
            the ONLY place a child learns its actual width. See the
            text wrapping comment block below for details.

4. DRAW     Each widget draws itself into its assigned rect, then
            recurses into children. Clipping ensures nothing leaks.

This is NOT a virtual DOM. There's no need for diffing, no reconciliation.
Each phase runs once per frame in a single top-down pass.
State changes (set_text, pipeline updates) just re-run build() on
the affected widget. The next frame's layout pass picks up the new
measurements automatically.
══════════════════════════════════════════════════════════════════

## Appendix B: The Game Loop

IPUI manages the pygame loop. Each frame executes in this order:

```
1. Snapshot input state     ( ip.dt, ip.mouse_*, ip.key_*)
2. Process pygame events    → UI consumes what it needs
3. ip_think(ip)             → Form, then all panes
4. Layout pass              → Measure, flex solve, assign rects
5. Screen clear
6. ip_draw(ip)              → Form, then active pane only
7. UI render                → Widget tree draws
8. ip_draw_hud(ip)          → Form, then active pane only
9. Display flip
```

<!-- SCREENSHOT: ipui/assets/images/widget_tree_debug.png — F12 debug mode showing the live widget tree inspector -->

---

## Appendix C: Tab Switch Lifecycle

Two form-level features can run during a tab switch: `tab_on_change` (the **gate**) and `ip_activated` (the **welcome mat**). They have similar-sounding names but completely different jobs. This appendix lays out exactly what fires when, and why you'd reach for one over the other.

### Workflow

When the user clicks a tab — say, switching from `Home` to `Forge`:

```
User clicks tab "Forge"
  │
  ▼
TabStrip.switch_tab("Forge")
  │
  ├─► allow_switch("Forge")               ◄── tab_on_change handler fires
  │     │
  │     └─► guard_tab_switch("Forge", "Home")
  │           returns False  → ABORT switch (vetoed; tab strip stays on "Home")
  │           returns True / None → continue
  │
  ├─► cache_active_content()              ◄── snapshot Home's widgets
  ├─► self.active_tab = "Forge"
  ├─► update_button_visuals()             ◄── tab strip highlight moves
  ├─► ensure_content("Forge")             ◄── may run ip_setup() on first visit
  │
  └─► notify_activated("Forge")           ◄── Forge.ip_activated(ip) fires
```

If `tab_on_change` returns `False`, the workflow stops at the gate. Nothing else happens — no caching, no `ip_activated`, no visual change. If it returns anything else (or doesn't return at all), the switch proceeds and `ip_activated` fires on the destination tab at the end.

### How They Differ

| | `tab_on_change` | `ip_activated` |
|---|---|---|
| **Lives on** | `_BaseForm` (one handler for the whole form) | `_BaseTab` (per-tab) — also `_BaseForm` for tabless / form-level activation |
| **Fires** | *Before* the switch happens | *After* the switch happens |
| **Signature** | `handler(name, current)` — destination and current tab names (strings) | `ip_activated(self, ip)` — receives the service portal |
| **Can veto?** | **Yes** — return `False` to block the switch | No — by the time it runs, the switch is done |
| **Use case** | "Don't let user leave Home until they pick a project" | "I'm now visible — refresh data, restart animations, sync from pipeline" |

### When to Reach for Which

**Use `tab_on_change` when** you need to *prevent* a tab switch. Common cases:

- The user has unsaved changes in the current tab.
- A required prerequisite hasn't been met (no project loaded, no model selected, etc.).
- A confirmation dialog needs to gate the switch.
- App-wide policy: e.g. during training, don't allow leaving the training tab.

**Use `ip_activated` when** the switch is fine to proceed and you just need to *react* to becoming visible:

- Refresh data that may have changed while the tab was off-screen.
- Restart an animation or particle effect.
- Sync UI state from the pipeline (e.g. update a label to reflect the current project).
- Reset positions, counters, or scroll offsets on each visit.

**Both can coexist on the same form.** `tab_on_change` runs first; if it allows the switch, `ip_activated` runs on the destination tab afterwards. They aren't redundant — they're sequential checkpoints in the same lifecycle.

### Form-Level Activation

`ip_activated` also fires at the form level when `IPUI.show()` brings a form to the front (or `IPUI.back()` returns to a previous one). The framework sets up the service portal — `ip.form`, `ip.tab`, `ip.tab_name`, `ip.is_active_tab`, and the geometry rects — *before* calling the hook, so they're correct when your code runs. Per-frame fields (`ip.dt`, `ip.events`, `ip.surface`) reflect the last completed frame.

---

*IPUI — Because life's too short for layout bugs.*