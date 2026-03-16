# IPUI - Idiot Proof UI - Because we've all spent 3 hours debugging a button!

A Python/Pygame UI framework

>**Easy to get right, hard to get wrong.**

![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)
![Pygame-ce](https://img.shields.io/badge/pygame--ce-2.x-orange)
![License](https://img.shields.io/badge/license-MIT-green)

**Actively developed • First public release — March 2026**

```bash
pip install ipui
```

---
## Table of Contents

- [The IPUI Advantage](#-the-ipui-advantage)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [The ip Service Portal](#the-ip-service-portal)
- [Lifecycle Hooks](#using-hooks-on-a-pane)
- [Widget Catalog](#widget-catalog)
- [Layout System](#layout-system)
- [Tabs and Panes](#tabs-and-basepanes)
- [Reactive Pipeline](#reactive-pipeline)
- [Imperative Approach](#imperative-approach)
- [Construction-Time Safety](#construction-time-safety)
- [Styling and Theming](#styling-and-theming)
- [Launching Your App](#launching-your-app)
- [API Reference](#api-reference)
- [Dependencies](#dependencies)
- [Appendix A: Single Pass Cycle](#appendix-a-detail-of-single-pass-cycle)
- [Appendix B: The Game Loop](#appendix-b-the-game-loop)

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
- 🎮 **Pygame Lifecycle Hooks:** `ip_think`, `ip_renderpre`, and `ip_renderpost` give you full access to the game loop without fighting the framework.
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

Tabs, banner, label, and a button with a modal message — 11 lines of code:







```python
# --- FormHelloWorld.py                          ( Define your tab structure (Tab Name -> [Pane Methods]))
from ipui import *                               # <======This is the only import you need for framework.
class FormHelloWorld(BaseForm):

    TAB_LAYOUT ={ # If key has a space, python objects can either skip or underscore(HelloWorld or Hello_World)
                  "Hello World": ["world"],            # Dictionary Key is tab name.  Values are panes. 
                  "Tab2" :       ["pane1", "pane2"],    # Ipui scaffolds a file matching tab name Hello.py
                  "Tab3" :       ["pane1", "pane2"],    # Ipui scaffolds a method for each pane. (run and click a tab with no file)
                }                                       # These files don't need import.
                                                        # IPUI searches same folder as FormHelloWorld.py 
                                                        # and all descendant folders automatically) 
# --- Hello.py
from ipui import *
class Hello(_basePane):
    def world(self, parent):                            # Semantic widgets with automatic layout
        Banner(parent, "IPUI", glow=True)       
        Body  (parent, "Because we've all spent 3 hours debugging a button.")
        
        # Interactive modal with a 2-second timer
        Button(parent, "Click Me", 
               color_bg=Style.COLOR_PAL_GREEN_DARK,
               on_click=lambda: self.form.show_modal("Hello World!", 2))

# --- Main.py 
from forms.HelloWorld.FormHelloWorld import FormHelloWorld  # Import your form to main
from ipui import *

if __name__ == "__main__":
    
    show(FormHelloWorld, "IPUI Documentation Guide")
```

No event loop setup. No manual sizing. No coordinate math. IPUI handles the Pygame lifecycle, layout, rendering, and event dispatch automatically.

<!-- SCREENSHOT: ipui/assets/images/quick_start.png — the Hello World form with banner, body text, and green button -->

---

## Core Concepts

### The Widget Tree

Every IPUI app is a tree. Construction attaches:

```python
card = CardCol(parent)      # attaches to parent
Title(card, "Settings")     # attaches to card
Body(card, "Change stuff")  # attaches to card
```

No `add()`. No `pack()`. No `grid()`. Construction IS attachment — an entire class of "widget exists but isn't visible" bugs is gone.

### `build()` Not `__init__`

```python
class MyWidget(_BaseWidget):
    def build(self):
        self.font     = Style.FONT_BODY
        self.color_bg = Style.COLOR_CARD_BG
```

By the time `build()` runs, `self.parent`, `self.form`, and `self.children` are already wired. You never need to call `super().__init__()` with a maze of arguments.

### Three Ways to Update the UI

**Reactive** — Declare relationships at the top of your _basePane. The pipeline handles propagation:

```python
class MyPane(_basePane):
    DECLARATION_UPDATES = {
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
class MySimulation(_basePane):
    def ip_think(self, ip):
        self.ball_x += self.ball_dx * ip.dt

    def ip_renderpre(self, ip):
        pos = ip.to_screen(self.ball_x, self.ball_y)
        r   = ip.scale_y(self.ball_r)
        pygame.draw.circle(ip.surface, (255, 160, 40), pos, r)

    def ip_renderpost(self, ip):
        font = Style.FONT_DETAIL
        surf = font.render(f"FPS: {ip.fps}", True, Style.COLOR_TEXT_ACCENT)
        ip.surface.blit(surf, (10, 10))
```

### Identity

| Attribute | Type | Description |
|-----------|------|-------------|
| `ip.form` | BaseForm | Active Form instance |
| `ip.form_name` | str | Name of the active form |
| `ip.pane` | _basePane | Active pane instance |
| `ip.pane_name` | str | Name of the active tab/pane |
| `ip.is_active_pane` | bool | Is this the visible pane? |

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

Use `ip.rect_pane` for all custom rendering in `ip_renderpre` and `ip_renderpost`. No spelunking through the widget tree — the framework finds your canvas for you.

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
| `ip.mouse_down("left")` | bool | Is the button held this frame? |
| `ip.mouse_pressed("left")` | bool | Was the button just pressed this frame? (edge detect) |
| `ip.mouse_released("left")` | bool | Was the button just released this frame? |
| `ip.mouse_inside(widget)` | bool | Is the mouse inside this widget's rect? |
| `ip.mouse_inside_pane()` | bool | Is the mouse inside `rect_pane`? |
| `ip.mouse_inside_content()` | bool | Is the mouse inside `rect_tab_area`? |
| `ip.mouse_hits(rect)` | bool | Is the mouse inside an arbitrary rect? |
| `ip.mouse_local_pos()` | tuple | Mouse position relative to `rect_pane` |
| `ip.mouse_local_pos(widget)` | tuple | Mouse position relative to a widget |
| `ip.mouse_local_x()` | int | Mouse x relative to `rect_pane` |
| `ip.mouse_local_y()` | int | Mouse y relative to `rect_pane` |

Buttons: `"left"`, `"middle"`, `"right"`.

### Keyboard

| Attribute / Method | Type | Description |
|--------------------|------|-------------|
| `ip.mod_shift` | bool | Shift held? |
| `ip.mod_ctrl` | bool | Ctrl held? |
| `ip.mod_alt` | bool | Alt held? |
| `ip.key_down("space")` | bool | Is this key held this frame? |
| `ip.key_pressed("space")` | bool | Was this key just pressed this frame? |
| `ip.key_released("space")` | bool | Was this key just released this frame? |

Keys use pygame names without the `K_` prefix: `"space"`, `"a"`, `"left"`, `"right"`, `"up"`, `"down"`, `"return"`, `"escape"`, `"tab"`, `"backspace"`, etc.

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

## Using Hooks on a Pane

Override any hook directly on your `_basePane` subclass:

```python
class MySimulation(_basePane):
    def initialize(self):
        self.ball_x  = 0.5
        self.ball_y  = 0.5
        self.ball_dx = 0.4
        self.ball_dy = 0.3

    def ip_think(self, ip):
        self.ball_x += self.ball_dx * ip.dt
        self.ball_y += self.ball_dy * ip.dt

    def ip_renderpre(self, ip):
        pos = ip.to_screen(self.ball_x, self.ball_y)
        pygame.draw.circle(ip.surface, (255, 160, 40), pos, 12)

    def ip_renderpost(self, ip):
        font = Style.FONT_DETAIL
        surf = font.render(f"FPS: {ip.fps}", True, Style.COLOR_TEXT_ACCENT)
        ip.surface.blit(surf, (10, 10))
```

### Using Hooks on a Form

Override on your `_BaseForm` subclass for app-wide logic:

```python
class MyApp(_BaseForm):
    def ip_think(self, ip):
        super().ip_think(ip)    # dispatches to panes
        # app-wide logic here
```

### IP_LIFECYCLE — What Happens When the Tab Isn't Active

Each pane can declare a lifecycle policy:

```python
class MySimulation(_basePane):
    IP_LIFECYCLE = "persist"     # default — ip_think keeps running in background
```

| Policy | ip_think when inactive | On return |
|--------|----------------------|-----------|
| `"persist"` | Keeps running | Normal (default) |
| `"pause"` | Stops | Resumes |
| `"restart"` | Stops | Re-runs `initialize()` |
| `"kill"` | Stops, pane destroyed | Rebuilt from scratch |

Render hooks (`ip_renderpre`, `ip_renderpost`) only fire for the **active** tab regardless of policy — no point drawing to a tab nobody can see.

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

All text widgets support `glow=True` (molten-orange forge effect) and `text_align='c'` or `'r'`.

### Layout Containers

| Widget    | Direction  | Chrome          | Usage                                    |
|-----------|------------|-----------------|------------------------------------------|
| `Row`     | Horizontal | None            | `Row(parent, justify_spread=True)`       |
| `Col`     | Vertical   | None            | `Col(parent)`                            |
| `CardRow` | Horizontal | Beveled, filled | `CardRow(parent, width_flex=True)`       |
| `CardCol` | Vertical   | Beveled, filled | `CardCol(parent, scrollable=True)`       |
| `Card`    | Vertical   | Beveled, filled | `Card(parent, height_flex=True)`         |

`Row`/`Col` are invisible structure. `CardRow`/`CardCol`/`Card` have a background and beveled edges.

### Interactive Widgets

**Button**
```python
Button(parent, "Launch",
    color_bg = Style.COLOR_PAL_GREEN_DARK,
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
grid.on_row_click(self.on_row_selected, "Run")
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

**ChartWidget**
```python
chart = ChartWidget(parent, width_flex=True, height_flex=True)
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
CardCol(parent, scrollable=True, height_flex=True)
```
Scrollable containers clip and scroll their children automatically. Scrollbars support both mouse wheel and click-and-drag.

---

## Tabs and _basePanes

Tab layout is declared in one dict on your form:

```python
class MyApp(BaseForm):
    TAB_LAYOUT = {
        "Config":  ["settings", "hyperparams"],
        "Results": ["chart",    "grid"],
        "Log":     ["log"],
    }
```

Each value is a list of method names. IPUI discovers the corresponding `_basePane` subclass by tab name (matching a Python file in the same directory), calls those methods to build each pane, and arranges them side-by-side.

```python
# Config.py
class Config(_basePane):
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

The `None` slot becomes `ip.rect_pane` — your game's arena. Draw in `ip_renderpre`, read mouse position with `ip.mouse_local_x()`, convert coordinates with `ip.to_screen()`. Zero framework spelunking required.

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
class MyApp(BaseForm):
    tab_early_load = ["Config", "Results"]
```

**Hidden tabs** (initially hidden, shown later via `show_tab`):

```python
class MyApp(BaseForm):
    tab_hidden = ["Colosseum"]
```

---

## Reactive Pipeline

The pipeline is a centralized key-value store. Write to it, and any widget that declared a dependency is automatically updated:

```python
# Write
self.form.pipeline_set("training_active", True)

# Read
active = self.form.pipeline_read("training_active")
```

Declare widget reactions in `DECLARATION_UPDATES` at the top of your _basePane:

```python
class TrainingPane(_basePane):
    DECLARATION_UPDATES = {
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

---

## Imperative Approach

Store widget references and drive them yourself:

```python
class MyPane(_basePane):
    def widgets(self, parent):
        self.lbl_count = Body(parent, "0 selected", name="lbl_count")
        self.btn_run   = Button(parent, "Run",
                             color_bg = Style.COLOR_PAL_GREEN_DARK,
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
| `widgets["typo"]`                        | `RuntimeError` listing valid names         |
| `on_click_me(non_callable)`               | `TypeError` at registration                |
| `on_click_me(func_with_params)`           | `ValueError` at registration               |

IPUI Error messages stand out by always starting: `Houston we have a problem!`

---

## Styling and Theming

All styling lives in `Style`. Import and use constants — don't hard-code colors or sizes:

```python
from ipui import Style

Button(parent, "Go", color_bg=Style.COLOR_PAL_GREEN_DARK)
Body(parent,   "Status", font=Style.FONT_BODY)
```

**Color constants:** `COLOR_BACKGROUND`, `COLOR_CARD_BG`, `COLOR_PANEL_BG`, `COLOR_TEXT`, `COLOR_TEXT_SECONDARY`, `COLOR_TEXT_MUTED`, `COLOR_BUTTON_BG`, `COLOR_BORDER`, `COLOR_PAL_GREEN_DARK`, `COLOR_PAL_GREEN_SECOND`, `COLOR_PAL_RED_DARK`, `COLOR_PAL_ORANGE_FORGE`

**Font constants:** `FONT_BANNER`, `FONT_TITLE`, `FONT_HEADING`, `FONT_BODY`, `FONT_DETAIL`, `FONT_MONO`

**Tokens:** `TOKEN_PAD`, `TOKEN_GAP`, `TOKEN_BORDER`, `TOKEN_SCROLLBAR`

**Screen:** `SCREEN_WIDTH` (default 1900), `SCREEN_HEIGHT` (default 900), `FONT_SCALE` (default 0.369)

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

| Attribute         | Type  | Description                                      |
|-------------------|-------|--------------------------------------------------|
| `TAB_LAYOUT`      | dict  | Tab name → list of pane method names             |
| `tab_early_load`  | list  | Tab names to pre-build at startup                |
| `tab_on_change`   | str   | Method name called on every tab switch           |
| `tab_hidden`      | list  | Tab names initially hidden                       |
| `tab_border`      | int   | Tab strip border override                        |
| `pipeline_debug`  | bool  | Log all pipeline activity to console             |

### BaseForm Methods

| Method                               | Description                                |
|--------------------------------------|--------------------------------------------|
| `pipeline_set(key, value)`           | Write to pipeline; triggers derived updates|
| `pipeline_read(key)`                 | Read current pipeline value                |
| `switch_tab(name)`                   | Switch to named tab                        |
| `set_pane(index, builder, *args)`    | Replace pane content at runtime            |
| `refresh_pane(index)`                | Rebuild current pane from its existing builder |
| `hide_tab(name)`                     | Hide a tab button                          |
| `show_tab(name)`                     | Show a hidden tab button                   |
| `get_tab(name)`                      | Return cached _basePane instance           |
| `prepare(name)`                      | Force-load a tab's _basePane               |
| `show_modal(msg, func, min_sec=0)`   | Show modal while running func              |
| `ip_think(ip)`                       | Per-frame logic hook (override for app-wide state) |
| `ip_renderpre(ip)`                   | Pre-render hook (override for backgrounds) |
| `ip_renderpost(ip)`                  | Post-render hook (override for overlays)   |

### _BaseWidget Constructor Parameters

All widgets accept these parameters:

| Parameter        | Type     | Default      | Description                                    |
|-----------------|----------|--------------|------------------------------------------------|
| `parent`        | widget   | —            | Parent widget (auto-attaches on construction)  |
| `text`          | str      | None         | Display text                                   |
| `name`          | str      | None         | Registers widget in `form.widgets`             |
| `width_flex`    | int      | 0            | Flex weight horizontal (0 = natural size)      |
| `height_flex`   | int      | 0            | Flex weight vertical (0 = natural size)        |
| `pad`           | int      | TOKEN_PAD    | Internal padding                               |
| `gap`           | int      | TOKEN_GAP    | Gap between children                           |
| `border`        | int      | TOKEN_BORDER | Border thickness                               |
| `justify_center`| bool     | False        | Center children in available space             |
| `justify_spread`| bool     | False        | Spread children evenly                         |
| `visible`       | bool     | True         | Show/hide widget                               |
| `enabled`       | bool/str | True         | False or reason string to disable              |
| `font`          | Font     | None         | Override font                                  |
| `text_align`    | str      | `'l'`        | `'l'`, `'c'`, or `'r'`                        |
| `color_bg`      | tuple    | None         | Background RGB tuple                           |
| `glow`          | bool     | False        | Molten-orange glow effect                      |
| `data`          | any      | None         | Arbitrary data payload                         |
| `single_select` | bool     | False        | Enforce single selection (lists/dropdowns)     |
| `placeholder`   | str      | None         | TextBox placeholder text                       |
| `initial_value` | any      | None         | Starting value                                 |
| `on_submit`     | callable | None         | Submit callback                                |
| `on_change`     | callable | None         | Change callback                                |
| `on_click`      | callable | None         | Click callback                                 |
| `pipeline_key`  | str      | None         | Pipeline read/write key                        |
| `tooltip_class` | class    | None         | Custom tooltip class                           |
| `scrollable`    | bool     | False        | Enable scrolling for this container            |
| `scroll_glow`   | float    | 0.369        | Scrollbar bevel intensity (0 = flat)           |
| `start`         | str      | None         | CodeBox: start-of-range marker                 |
| `end`           | str      | None         | CodeBox: end-of-range marker                   |

### _BaseWidget Methods

| Method                    | Description                                       |
|---------------------------|---------------------------------------------------|
| `set_text(text)`          | Update text and rebuild layout                    |
| `set_disabled(reason="")` | Disable with optional hover-tooltip reason        |
| `set_enabled()`           | Re-enable widget                                  |
| `clear_children()`        | Remove all child widgets                          |
| `on_click_me(callback)`   | Register validated click handler (zero-arg)       |
| `display_name`            | Property: human-readable identity (name → text → type) |

### _basePane

| Attribute             | Type   | Description                                  |
|-----------------------|--------|----------------------------------------------|
| `DECLARATION_UPDATES` | dict   | Reactive derive declarations (see below)     |
| `IP_LIFECYCLE`        | str    | Tab lifecycle policy: `"persist"` (default), `"pause"`, `"restart"`, `"kill"` |

**Lifecycle hooks** (override on your pane):

| Method | Description |
|--------|-------------|
| `initialize()` | One-time setup (runs once when pane is first created) |
| `ip_think(ip)` | Per-frame logic. State, physics, AI. |
| `ip_renderpre(ip)` | Draw before UI. Game worlds, backgrounds. |
| `ip_renderpost(ip)` | Draw after UI. Overlays, cursors, effects. |

**DECLARATION_UPDATES entry format:**
```python
"widget_name": {
    "property": "text",          # or "enabled", or any widget attribute
    "compute":  "method_name",   # method on this _basePane
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

### ChartWidget Methods

| Method                              | Description                           |
|-------------------------------------|---------------------------------------|
| `set_data(lines, x_label, y_label)` | Update chart data (dirty-flag render) |

### PowerGrid Methods

| Method                              | Description                                 |
|-------------------------------------|---------------------------------------------|
| `set_data(rows, columns=None)`      | Set grid data (list of lists, dicts, or dict of lists) |
| `set_data(path, query=sql)`         | Load from SQLite database with a query      |
| `set_data(path, table=name)`        | Load an entire SQLite table                 |
| `set_column_max(col_name, width)`   | Set max pixel width for a column            |
| `set_page_size(n)`                  | Set rows per page (0 = no pagination)       |
| `on_row_click(callback, key_col)`   | Register row click with key column          |

---

## Dependencies

- Python 3.9+
- pygame-ce
- matplotlib (for ChartWidget)

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

This is NOT a virtual DOM. There's no diffing, no reconciliation.
Each phase runs once per frame in a single top-down pass.
State changes (set_text, pipeline updates) just re-run build() on
the affected widget. The next frame's layout pass picks up the new
measurements automatically.
══════════════════════════════════════════════════════════════════

## Appendix B: The Game Loop

IPUI manages the pygame loop. Each frame executes in this order:

```
1. Snapshot input state (ip.dt, ip.mouse_*, ip.key_*)
2. Process pygame events → UI consumes what it needs
3. ip_think(ip)        → Form, then all panes (per IP_LIFECYCLE)
4. Layout pass         → Measure, flex solve, assign rects
5. Screen clear
6. ip_renderpre(ip)    → Form, then active pane only
7. UI render           → Widget tree draws
8. ip_renderpost(ip)   → Form, then active pane only
9. Display flip
```

<!-- SCREENSHOT: ipui/assets/images/widget_tree_debug.png — F12 debug mode showing the live widget tree inspector -->

*IPUI — Because life's too short for layout bugs.*