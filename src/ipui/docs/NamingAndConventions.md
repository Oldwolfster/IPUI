# IPUI v0.1 Naming Convention

**The definitive style guide for the IPUI framework.**

Names that ship on PyPI are permanent. This document defines the rules, rationale, and examples so every contributor — human or AI — writes code that looks like it belongs.

---

## Philosophy

IPUI names follow three principles:

1. **Prefix over suffix.** Grouping like things makes them line up in code, autocomplete, and file listings.
2. **Structure over secrecy.** Underscores signal architectural role, never access control.
3. **Say what you mean.** A name should tell you what something *is*, not make you guess.

---

## How I choose names in Python     (99% of the time)

### 1. One Class Per File, Named Identically

Every `.py` file contains one class. The filename matches the class name exactly.

```
Button.py      → class Button        ✓
_BaseWidget.py → class _BaseWidget   ✓
CardCol.py     → class CardCol       ✓
```

**Exception:** `Row.py` contains `Row`, `Col`, `CardRow`, and `CardCol` — four tightly-related layout primitives that are always used together.
maybe 2 or 3 more exceptions through out the project.
---

### 2. `_Base` Prefix for Abstract Base Classes

Classes meant for subclassing — never direct instantiation — get the `_Base` prefix. The underscore means *structural base*, not "private."

```python
class _BaseWidget:   ...   # Inherit for custom widgets
class _BaseForm:     ...   # Inherit for app screens
class _BaseTab:     ...   # Inherit for tab content
```

---

### 3. Event and Callback Prefixes

Three prefixes carry distinct meanings. Keeping them separate makes intent obvious at the call site.

- **`on_`** is reserved strictly for events a widget can fire. It marks the *attachment point* — `on_click`, `on_change`, `on_submit`. You assign callbacks to these; you do not implement them.
- **`handle_`** is the function *you* write to react when an event fires. It reads naturally: "handle save", "handle row click". Pairs with `on_`.
- **`ip_`** is reserved for lifecycle hooks the framework calls into your code. `ip_setup`, `ip_activated`, `ip_think`, `ip_draw`, `ip_draw_hud`. You override these; the framework invokes them.

```python
# Constructor callbacks — on_ is the attachment, handle_ is your function
Button(parent, "Save", on_click=self.handle_save)
TextBox(parent, on_change=self.handle_change, on_submit=self.handle_submit)

# Lifecycle hooks — override on your _BaseForm or _BaseTab
def ip_setup(self, ip):     ...
def ip_think(self, ip):     ...
def ip_draw(self, ip):      ...

# Registration methods
grid.on_row_click(self.handle_grid_click, "batch_id")
```

---

### 4. `SCREAMING_CASE` for Constants and Declarations

Class-level constants, style tokens, and the reactive declaration dictionary use SCREAMING_CASE. Instance variables never do.

```python
# Constants
Style.COLOR_CARD_BG
Style.TOKEN_PAD
Style.FONT_SCALE

# Reactive declaration
DECLARATION_UPDATES = {
    "lbl_status": {
        "property": "text",
        "compute": "compute_status",
        "triggers": ["score", "level"],
    },
}
```

---

### 5. `snake_case` for All Methods and Instance Variables

Exceptions are rare.


```python
def measure_tree(self, node):    ...   # ✓
def layout_node(self, node):     ...   # ✓
def pipeline_set(self, key, val):...   # ✓

self.layout_engine = NotNP_HardWrap(self)   # ✓
```

---

### 6. Underscores Signal Structure, Not Privacy (Sorry Guido!)

In most OOP languages, a name's scope is declared with an **access modifier** keyword — `public`, `private`, `protected`, and so on. Python has no such keywords. Instead, by convention, a leading underscore (`_engine`, `_hover_cache`) signals "this is private — please don't touch it."

IPUI does not use the underscore for this purpose. We don't try to enforce visibility through naming — that's a job for code review and documentation, not punctuation.

A leading underscore in IPUI means *structural prefix* — and right now there's exactly one: **`_Base`** (for abstract base classes meant to be subclassed but never instantiated directly). If a name doesn't fit a structural pattern like that, it gets no underscore.

```python
self.engine          # ✓  (not self._engine)
def is_text_leaf():  # ✓  (not def _is_text_leaf())
hover_cache = {}     # ✓  (not _hover_cache)
```
---

### 7. `PascalCase` for All Classes

No underscores within the name, except the structural prefix mentioned above.

```python
class PowerGrid:        ...   # ✓
class FormParticleLife:  ...  # ✓
class NotNP_HardLayout: ...   # ✓
```

---

### 8. `Mgr` Prefix for Singleton Service Classes

Classes that manage a cross-cutting concern — all classmethods, no instances — use the `Mgr` prefix.

```python
class MgrFont:      ...   # Font loading and caching
class MgrColor:     ...   # Color computation
class MgrClipboard: ...   # System clipboard
class MgrFile:      ...   # Pane file generation
class MgrLog:       ...   # Logging infrastructure
```

---

### 9. `Form` Prefix for Form Subclasses

All `_BaseForm` subclasses start with `Form`. No underscores.

```python
class FormShowcase(_BaseForm):      ...   # ✓
class FormParticleLife(_BaseForm):   ...  # ✓
class FormDebugger(_BaseForm):      ...   # ✓
```

---

### 10. Dead Code Gets Deleted, Not Prefixed

Version control is the archive. Ship clean. <- screw that.  i'll trust git when i'm dead.  I'll trust bat files until then.

Before release: delete all `aaa_` methods, `*Old` methods, and duplicates.  Delete all 'Backup' classes After release: use `IPUI_DEPRECATED_` prefix, remove after one minor version.

---

## Quick Reference

| What | Pattern                | Examples                                  |
|------|------------------------|-------------------------------------------|
| Widget classes | `PascalCase`           | `Button`, `CardCol`, `PowerGrid`          |
| Base classes | `_Base` + `PascalCase` | `_BaseWidget`, `_BaseForm`, `_BaseTab`    |
| Service singletons | `Mgr` + `PascalCase`   | `MgrFont`, `MgrColor`, `MgrLog`           |
| Form subclasses | `Form` + `PascalCase`  | `FormShowcase`, `FormParticleLife`        |
| Methods | `snake_case`           | `set_data()`, `pipeline_read()`           |
| Instance variables | `snake_case`           | `layout_engine`, `scroll_offset`          |
| Constants & tokens | `SCREAMING_CASE`       | `COLOR_CARD_BG`, `TOKEN_PAD`              |
| Events (constructor/registration) | on_ + snake_case       | on_click, on_row_click()                  |
| Callbacks & handlers              | handle_ + snake_case   | handle_click, handle_update()             |
| Lifecycle hooks                   | ip_ + snake_case       | ip_draw(self, ip), ip_activated(self, ip) |
| Files | Match class name       | `Button.py`, `_BaseWidget.py`             |

---

## Deferred to v0.2

These names are imperfect but changing them now costs more than it's worth:

| Name | Issue | Why Wait |
|------|-------|----------|
| `my_surface` | Unusual `my_` prefix | Same — deep refactor, low payoff. |
| `do_not_allocate` | Negative boolean | Rarely user-facing. Rename risks subtle bugs. |
| `on_click_me()` | "Temporary" name | Needs design discussion: merge into `on_click`? |
