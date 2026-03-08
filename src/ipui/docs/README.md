# IPUI - Idiot Proof UI - Because we've all spent 3 hours debugging a button!

A Python/Pygame UI framework

>**Easy to get right, hard to get wrong.**

```bash
pip install ipui
```

---

## 🛠️ The IPUI Advantage

IPUI isn't just a library; it's a structural engine designed to make pygame UIs easy, error resistant, and sharp looking.

* **📱 Resolution Independent**: UI scales automatically to physical screen height—looks perfect on a laptop or a 4K monitor.
* **📐 Declarative Layout**: Simple, flexible syntax that handles the math so you can focus on the logic.
* **🧩 Radical Extensibility**: Custom widgets get layout, events, and styling for free. Standard widgets take 5–10 LOC; even complex tools like "Network Diagram Builders" are under 150 LOC.
* **🗂️ First-Class Tab System**: Define your entire app structure with a single dictionary at the top of your Form.
* **📜 One-Touch Scrolling**: Make any Card scrollable with a single parameter—no complex viewport setup required.
* **🔗 Construction IS Attachment**: No floating widgets or `add()` calls. If you build it inside a container, it's attached. No voids, no leaks.
* **🔄 Hybrid Paradigms**: Mix **Reactive** (DAG-based updates) and **Imperative** (event-driven) styles freely in the same pane.
* **⛓️ Data Pipeline**: Link widgets to keys for automatic initial values and seamless data reading across different tabs.
* **💡 Multi-Tier Tooltips**: Choose between standard hover tips or "Super Tooltips"—pinnable, scrollable windows capable of displaying deep technical data.
* **🗃️ Automatic Widget Registry**: Stop passing references around. Access any widget instantly via the global registry.
* **📚 Self-Documenting**: Documentation that stays accurate by reading the framework source code directly.
* **🐞 Pro Debug Mode**: Includes a live "Widget Tree" and layout overlays to make solving positioning issues a breeze.
* **💻 Beautiful Code Boxes**: Display source code by passing a string or a file path; IPUI handles the formatting.
* **🗺️ Tab Map**: A birds-eye view of your entire application content for quick review and navigation.
* **📊 The "Baddest" DataGrid**: Sortable, filterable, and SQL-ready. Feed it lists, dicts, or databases—it just works.
* **📊 MatPlotLib Graphs**:  Add to your pygame apps with this widget.
---

## Quick Start (tabs, banner, label, and button w/ modal message -  11 lines of code)

```python
import ipui
from ipui import *

class MyApp(BaseForm):
    # 1. Define your tab structure (Tab Name -> [Pane Methods])
    TAB_LAYOUT ={
                  "Start": ["hello"],            # brackets optional for a single pane: "Start": "hello" 
                  "Tab2" : ["pane1", "pane2"]
                }

# --- Start.py (IPUI finds this in any subfolder automatically!) ---
class Start(_basePane):
    def hello(self, parent):
        # 2. Semantic widgets with automatic layout
        Banner(parent, "IPUI", glow=True)
        Body(parent, "Because we've all spent 3 hours debugging a button.")
        
        # 3. Interactive modal with a 2-second timer
        Button(parent, "Click Me", 
               color_bg=Style.COLOR_PAL_GREEN_DARK,
               on_click=lambda: self.form.show_modal("Hello World!", 2))

# 4. Launch the engine
if __name__ == "__main__":
    ipui.show(MyApp, "Idiot Proof UI")
```

No event loop setup. No manual sizing. No coordinate math. IPUI handles the Pygame lifecycle, layout, rendering, and event dispatch automatically.


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
grid.on_row_click(self.on_row_selected, "Run")
```

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
Scrollable containers clip and scroll their children automatically.

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

Each value is a list of method names. IPUI discovers the corresponding `BasePane` subclass by tab name (matching a Python file in the same directory), calls those methods to build each pane, and arranges them side-by-side.

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

**Tab control at runtime:**

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



---

## Construction-Time Safety

IPUI catches mistakes when you make them, not when users hit them:

| Mistake                                   | Error raised                               |
|-------------------------------------------|--------------------------------------------|
| Override `__init__` in a widget           | `TypeError` at class definition            |
| `justify_center` AND `justify_spread`     | `ValueError` at construction               |
| `text_align='x'`                          | `ValueError` at construction               |
| `widgets["typo"]`                        | `RuntimeError` listing valid names         |
| `on_click_me(non_callable)`               | `TypeError` at registration                |
| `on_click_me(func_with_params)`           | `ValueError` at registration               |

Error messages use plain language: `HEY PILGRIM! EZ-FIX ---->` followed by exactly what to change.

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

`ipui.show()` starts the Pygame loop on the first call. On subsequent calls (from within a running app) it switches the active form. Use `ipui.back()` to return to the previous form.

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
| `get_tab(name)`                      | Return cached _basePane instance         |
| `prepare(name)`                      | Force-load a tab's _basePane             |
| `show_modal(msg, func, min_sec=0)`   | Show modal while running func in thread    |

### _BaseWidget Constructor Parameters

All widgets accept these parameters:

| Parameter        | Type     | Default      | Description                                    |
|-----------------|----------|--------------|------------------------------------------------|
| `parent`        | widget   | —            | Parent widget (auto-attaches on construction)  |
| `text`          | str      | None         | Display text                                   |
| `name`          | str      | None         | Registers widget in `form.widgets`            |
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

### _basePane

| Attribute             | Type | Description                                  |
|-----------------------|------|----------------------------------------------|
| `DECLARATION_UPDATES` | dict | Reactive derive declarations (see below)     |

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

| Method                           | Description                           |
|----------------------------------|---------------------------------------|
| `set_data(rows, columns=None)`   | Set grid data (list of lists)         |
| `set_column_max(col_name, width)`| Set max pixel width for a column      |
| `on_row_click(callback, key_col)`| Register row click with key column    |

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

*IPUI — Because life's too short for layout bugs.*