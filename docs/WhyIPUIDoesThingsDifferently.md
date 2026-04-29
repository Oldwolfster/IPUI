## Why IPUI Does Things Differently

> IPUI makes choices that look unconventional if you're coming from other UI frameworks. This doc explains the design intent behind choices that may look unusual if you’re coming from other UI frameworks.

### The O(1) Principle

Every framework design decision lives on one side of a line:

- **Framework-side — O(1).** Solved once, inside the framework. Every user gets it for free. Zero defect surface. Zero tech debt.
- **User-side — O(N).** Every user re-solves it for each usage. Each solution carries a fixed build cost, widens the defect attack surface, and accumulates ongoing tech debt.

IPUI pushes as much as possible to the framework side. When something can be handled once — reliably, invisibly — there's no reason to ask every user to handle it themselves, every time, forever.

This principle drives nearly every decision below.

### `build()`, Not `__init__`

Here's how custom widgets work in tkinter:

```python
class ScrolledList(tk.Frame):
    def __init__(self, parent, **options):
        tk.Frame.__init__(self, parent, **options)   # ← you must get this right
        self._list = tk.Listbox(self)
        self._scrollbar = tk.Scrollbar(self)
        self._list.pack(side=tk.LEFT)
        self._scrollbar.pack(side=tk.LEFT)
```

And PyQt:

```python
class PowerBar(QWidget):
    def __init__(self, steps=5, *args, **kwargs):
        super().__init__(*args, **kwargs)             # ← you must get this right
        layout = QVBoxLayout()
        self._bar = _Bar(steps)
        layout.addWidget(self._bar)
        self._dial = QDial()
        layout.addWidget(self._dial)
        self.setLayout(layout)
```

Every subclass must call the parent constructor with the right arguments in the right order. Every user, every widget, every time. Forget it and you get a half-initialized widget that fails in confusing ways later. That's O(N).

Here's the same idea in IPUI:

```python
class PowerBar(_BaseWidget):
    def build(self):
        self.color_bg = Style.COLOR_CARD_BG
        MgrColor.apply_bevel(self, "sunken")
```

No `super().__init__()`. No `*args, **kwargs` forwarding. No `parent` parameter to thread through. The framework handles all of that before `build()` is called — `self.parent`, `self.form`, `self.children`, and every attribute are already wired. You literally cannot forget to pass the framework's parameters because you never see them.

If you try to override `__init__`, you get a clear error at class definition time. Not at runtime. Not in production.

### Construction IS Attachment

```python
card = CardCol(parent)
Title(card, "Settings")
Body(card, "Change stuff")
```

No `add()`. No `pack()`. No `grid()`. When you construct a widget inside a container, it's attached. Period.

This eliminates the entire category of "widget exists but isn't on screen" bugs — O(1). In frameworks where attachment is a separate step, every user must remember to attach every widget every time — O(N).

### `from ipui import *`

IPUI uses a star import deliberately.  Conventional wisdom says they're dangerous because you don't know what you're importing.

IPUI controls `__all__` explicitly. You get exactly the public API — the widgets, the base classes, the style constants — and nothing else. One import line, and you're building. No ceremony, no six-line import blocks to maintain, no "which subpackage was PowerGrid in again?"

The alternative is asking every user to maintain their import list for every file — O(N).

### No "Private" Underscores

IPUI uses underscores for structural meaning, never as 'suggested scope modifiers'. `_BaseWidget` means "structural base class." `private_enabled` means "backing storage." A leading underscore never means "don't touch this."

### One Class Per File (There are a couple of exceptions)

Every `.py` file contains one public class. The filename matches the class name exactly. `Button.py` has `Button`. `PowerGrid.py` has `PowerGrid`.

This makes discovery trivial — in your file browser, in your IDE, in conversation. No hunting through a 2,000-line `widgets.py` to find the class you need. And it's how IPUI's tab discovery system works: a tab named "Settings" automatically finds `Settings.py`.

### All Code Lives in Classes

No loose functions at module level. No executable code outside `if __name__ == "__main__":`.

For one, this eliminates order dependency

Also, module-level code runs on import, in whatever order Python resolves dependencies. That's a source of subtle, order-dependent bugs that are painful to diagnose. Wrapping everything in classes eliminates this entirely — O(1) structural protection instead of O(N) discipline from every developer on every file.

### Resolution Independence — No Pixel Math

IPUI scales to the physical screen automatically. You work in semantic sizes (`FONT_BODY`, `TOKEN_PAD`) and normalized coordinates (`ip.to_screen(0.5, 0.5)`). The framework does the pixel math.

The alternative is every user doing coordinate math for every element, then redoing it when someone runs the app on a different monitor — O(N).

### `TAB_LAYOUT` — Single Source of Truth

Your entire app structure is one dictionary at the top of your form:

```python
TAB_LAYOUT = {
    "Config":  ["settings", "hyperparams"],
    "Results": ["chart",    "grid"],
}
```

No router. No navigation stack. No registration calls. The dictionary *is* the structure, and IPUI builds everything from it — tab buttons, pane slots, file discovery, hot-reload.

### Pygame as Foundation

"Why not tkinter? Why not Qt? Why not web?"

Because IPUI was built for applications that think every frame — neural network experimentation, simulations, games. The pygame loop gives you `ip_think`, `ip_draw`, and `ip_draw_hud` as first-class hooks. You get 60fps rendering, real-time input, and a game-loop architecture that widget-tree frameworks can't offer without bolting on a separate threading model.

And thanks to the `ip` service portal, you never touch the raw pygame API for layout, input, or coordinate math unless you want to.

### Behaviors, Not Classifications

This is the design choice that pays the biggest compound dividend.

Most UI frameworks divide the world into container widgets and leaf widgets. Containers can hold children. Leaves cannot. If you want a widget that's *mostly* a leaf but needs to hold one child in one situation, you're subclassing, wrapping, or fighting the type system.

IPUI doesn't classify widgets this way. There are no "container" or "leaf" types. Every widget inherits from `_BaseWidget`, which handles children, layout, scrolling, events, and drawing. Whether a widget *actually has* children is just a runtime fact, not a type-level constraint.

The analogy is security entitlement management: never grant permissions directly to a user. Instead, grant permissions to groups, and add users to groups. In IPUI: never hard-code capabilities into specific widget subclasses. Instead, put behaviors on `_BaseWidget`, and let widgets opt in through attributes.

Scrolling is a perfect example. There is no `ScrollableContainer` class. There is no `ScrollView`, `ScrollPane`, or `ScrollArea`. There's `scrollable=True` — a parameter on any widget. The scrolling behavior lives once, on `_BaseWidget`, tested once, debugged once. Any widget that sets the flag gets it for free.

The effect is easy to see in the codebase.  Look at `CardCol` — the most-used container in IPUI:

```python
class CardCol(_BaseWidget):
    def build(self):
        if self.color_bg is None: self.color_bg = Style.COLOR_CARD_BG
        MgrColor.apply_bevel(self, "sunken")
```

Two lines of behavior. It's not a special container subclass. It's `_BaseWidget` with a background color and a bevel. That's it. And yet it can hold any number of children, scroll them, clip them, lay them out — because those are behaviors on the base, not features of a special container type.

`Row` is three lines. `Button` is about ten. `Banner` is two. Across 36+ widget classes, there is almost zero behavioral drift, near-perfect DRY, and total consistency — because the behaviors live in one place and widgets simply declare which ones they want.

Every time a capability gets baked into a specific widget subclass instead of the base, it's a small tax on the entire system: one more place that can drift, one more thing to test separately, one more special case to document. IPUI treats those exceptions like technical debt — always looking to eliminate them, always pushing behavior back to the base where it's solved once.

O(1).

### See for Yourself

The best evidence isn't an argument — it's the code. Run the smoke test, open F12, and browse the widget tree. Check the Widget Catalog tab and see 36+ widgets built on a single, uniform foundation. Read `CardCol.py` and count the lines.

Then try building something. If the approach works for you, you'll feel it in the first ten minutes.