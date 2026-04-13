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

## How i choose names in Python(99% of the time):

### 1. One Class Per File, Named Identically

Every `.py` file contains one public class. The filename matches the class name exactly.

```
Button.py      → class Button        ✓
_baseWidget.py → class _baseWidget   ✓
CardCol.py     → class CardCol       ✓
```

**Exception:** `Row.py` contains `Row`, `Col`, `CardRow`, and `CardCol` — four tightly-related layout primitives that are always used together.

---

### 2. `_Base` Prefix for Abstract Base Classes

Classes meant for subclassing — never direct instantiation — get the `_Base` prefix. The underscore means *structural base*, not "private."

```python
class _BaseWidget:   ...   # Inherit for custom widgets
class _BaseForm:     ...   # Inherit for app screens
class _BaseTab:     ...   # Inherit for tab content
```

---

### 3. `on_` Prefix for Events, `handle_` Prefix for Callbacks and  `hook_` Prefix for Lifecycle hooks

>on_ is reserved strictly for events the widget can fire.
> 
>handle_ is used for the functions you write or override to react to those events (reads naturally as “when this happens…
> 
> hook_ is a prefix meaning IPUI is exposing a hook to the pygame loop for you.

```python
# Constructor callbacks
Button(parent, "Save", on_click=handle_save)
TextBox(parent, on_change=handle_parent_submit, on_submit=handle_parent_submit)

# Lifecycle hooks (override on your Form)
def hook_event(self, event):  ...
def hook_update(self, dt):    ...
def hook_draw(self, surface): ...

# Registration methods
grid.on_row_click(handle_grid_click, "batch_id")
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

No exceptions. Not for "internal" methods, not for abbreviations, not for emphasis.

```python
def measure_tree(self, node):    ...   # ✓
def layout_node(self, node):     ...   # ✓
def pipeline_set(self, key, val):...   # ✓

self.layout_engine = MeasureAndWrap(self)   # ✓
```

---

### 6. No Guido-Style `_private` Underscores

A leading underscore means *structural prefix* (`_base`, `_Hook_`). If the name doesn't fit a structural pattern, it gets no underscore.

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
class FormParticleLife:  ...   # ✓
class MeasureAndLayout: ...  # ✓
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

All `_baseForm` subclasses start with `Form`. No underscores.

```python
class FormShowcase(_baseForm):      ...   # ✓
class FormParticleLife(_baseForm):   ...   # ✓
class FormDebugger(_baseForm):      ...   # ✓
```

---

### 10. Dead Code Gets Deleted, Not Prefixed

Version control is the archive. Ship clean. <- screw that.  i'll trust git when i'm dead.  I'll trust bat files until then.

Before release: delete all `aaa_` methods, `*Old` methods, and duplicates.  Delete all 'Backup' classes After release: use `IPUI_DEPRECATED_` prefix, remove after one minor version.

---

## Quick Reference

| What | Pattern                | Examples                              |
|------|------------------------|---------------------------------------|
| Widget classes | `PascalCase`           | `Button`, `CardCol`, `PowerGrid`      |
| Base classes | `_base` + `PascalCase` | `_baseWidget`, `_baseForm`, `_BaseTab` |
| Service singletons | `Mgr` + `PascalCase`   | `MgrFont`, `MgrColor`, `MgrLog`       |
| Form subclasses | `Form` + `PascalCase`  | `FormShowcase`, `FormParticleLife`    |
| Methods | `snake_case`           | `set_data()`, `pipeline_read()`       |
| Instance variables | `snake_case`           | `layout_engine`, `scroll_offset`      |
| Constants & tokens | `SCREAMING_CASE`       | `COLOR_CARD_BG`, `TOKEN_PAD`          |
| Events (constructor/registration) | on_ + snake_case       | on_click, on_row_click()              |
| Callbacks & handlers              | handle_ + snake_case   | handle_click, handle_update()         |
| Lifecycle hooks                   | hook_ + snake_case     | hook_(), handle_draw()                |
| Files | Match class name       | `Button.py`, `_baseWidget.py`         |

---

## Deferred to v0.2

These names are imperfect but changing them now costs more than it's worth:

| Name | Issue | Why Wait |
|------|-------|----------|
| `my_surface` | Unusual `my_` prefix | Same — deep refactor, low payoff. |
| `do_not_allocate` | Negative boolean | Rarely user-facing. Rename risks subtle bugs. |
| `on_click_me()` | "Temporary" name | Needs design discussion: merge into `on_click`? |

---

<!-- ============================================================ -->
<!-- DELETE BELOW THIS LINE BEFORE PUBLISHING                      -->
<!-- ============================================================ -->

## INTERNAL: API-Breaking Impact Analysis

These 4 changes affect code that users write. Every reference must be updated.

### 1. `Text.py` → `Label.py` (file rename)

**What changes for users:** Import paths.

```python
# OLD
from ipui.widgets.Label import Label, Banner, Title, Heading, Body, Detail

# NEW
from ipui.widgets.Label import Label, Banner, Title, Heading, Body, Detail
```

**Files that reference `Text` by import:**

| File | Import line |
|------|-------------|
| `Overview.py` | `from ipui.widgets.Text import Detail` |
| `Settings.py` | `from ipui.widgets.Text import Detail` |
| `TemplateStarterKit.py` | `from ipui.widgets.Text import Detail` |
| `Iamnothere.py` | `from ipui.widgets.Text import Detail` |
| `Magic.py` | `from ipui.widgets.Text import Detail` |
| `Widgets.py` (EZ_Pane) | (uses `from ipui import *`) |
| `PygameBall.py` / Welcome | `from ipui.widgets.Text import Title, Body, Detail` |
| `Overlay.py` / DebugOverlay | `from ipui.widgets.Text import Title, Body` |
| `Layout.py` / DebugLayout | `from ipui.widgets.Text import Title, Body` |
| `MissingTabUI.py` | `from ipui.widgets.Text import ...` |
| `TabStrip.py` | `from ipui.widgets.Text import Title, Body` |
| `NetworkDiagram.py` | `from ipui.widgets.Text import Detail, Title, Body` |

| `__init__.py` | Likely re-exports (verify) |

**Mitigation:** Add `Text.py` as a one-line re-export shim:
```python
# Text.py — backward compatibility
from ipui.widgets.Label import *
```

### 2. `_BaseTab` → `_BaseTab` (class + file rename)

**What changes for users:** Class they inherit from.

```python
# OLD
class MyTab(_BaseTab):

# NEW
class MyTab(_BaseTab):
```

**Files that reference `_BaseTab`:**

| File | Reference |
|------|-----------|
| `TabStrip.py` | `from ipui.engine._BaseTab import _BaseTab`, `issubclass(obj, _BaseTab)` |
| `Overview.py` | `from ipui import *` (gets _BaseTab) |
| `Settings.py` | same |
| `TemplateStarterKit.py` | same |
| `Iamnothere.py` | same |
| `Magic.py` | same |
| `Widgets.py` | same |
| `Particles.py` | same |
| `Freebies.py` | (likely) |
| `Paradigm.py` | (likely) |
| `Showcase.py` | (likely) |
| `Reference.py` | (likely) |
| `Designer.py` | (likely) |
| `Tree.py` | (likely) |
| `Welcome.py` | explicit import |
| `FormDebugger.py` | (likely via tabs) |
| `MissingTabUI.py` | `from ipui.engine._BaseTab import _BaseTab` |
| `__init__.py` | Re-export |

**Mitigation:** Add alias in `_BaseTab.py`:
```python
_BaseTab = _BaseTab  # backward compat, remove in v0.2
```

### 3. `Form_ParticleLife` → `FormParticleLife` (class + file rename)

**What changes for users:** Import and class name.

**Files that reference:**

| File | Reference |
|------|-----------|
| `FormShowcase.py` | `from forms.ParticleLife.Form_ParticleLife import Form_ParticleLife` |
| `Form_ParticleLife.py` itself | `class Form_ParticleLife` |

Small blast radius — only 2 files.

### 4. `_BaseTab.py` file rename (consequence of #2)

Covered above. Same files as #2.

---

## INTERNAL: Itemized To-Do List

### Ship-Blocking (do before v0.1)

- [x ] **BUG** `Overview.py`: Change `"DECLARATION_UPDATES"` → `"triggers"` in the DECLARATION_UPDATES dict
- [ ] **BUG** `Form_ParticleLife.py`: Change `BaseForm` → `_baseForm`
- [x ] **BUG** `_baseWidget.py`: Delete duplicate `on_click_me()` (keep one copy)
- [x ] **DELETE** `_baseWidget.py`: Remove all 10 `aaa_` prefixed methods
- [ x] **DELETE** `_baseWidget.py`: Remove `draw_childrenOld`
- [x ] **DELETE** `_baseWidget.py`: Remove `smack_nl_on_tuple_of_strings`
- [x ] **DELETE** `_baseForm.py`: Remove `draw_tooltipsOld`
- [x ] **DELETE** `_baseForm.py`: Remove `compute_root_rectHopefullyIamDeprecated`
- [ x] **DELETE** `_IPUI.py`: Remove `pygame_loopPreHook`
- [ x] **DELETE** `_baseHugeTooltip.py`: Remove `ozMOVE_BTN_H` and duplicate `MOVE_BTN_H`

### API Renames (do before v0.1, add backward-compat shims)

- [x ] **RENAME FILE** `Text.py` → `Label.py` (add re-export shim in old path)
- [x ] **RENAME FILE+CLASS** `_BaseTab.py` → `_BaseTab.py`, class `_BaseTab` (add alias)
- [s ] **RENAME FILE+CLASS** `Form_ParticleLife.py` → `FormParticleLife.py`, class `FormParticleLife`
- [ x] **DOCSTRING** `Label`: Change `name: Text` → `name: Label`
- [x ] **DOCSTRING** `Grid`: Change "use DataGrid" → "use PowerGrid"

### Engine Renames (safe, no user impact)

- [x ] **RENAME FILE** `MeasureAndLayout.py` → `MeasureAndLayout.py`
- [ x] **RENAME FILE** `MeasureAndWrap.py` → `MeasureAndWrap.py`
- [ x] **RENAME FILE** `Overlay.py` → `DebugOverlay.py`
- [x ] **RENAME FILE** `Layout.py` → `DebugLayout.py`
- [x ] **RENAME FILE** `PygameBall.py` → `Welcome.py`
- [s ] **RENAME METHOD** `RunLayout()` → `run()` on `MeasureAndLayout` and `MeasureAndWrap`
- [x ] **RENAME METHOD** `init_pygame()` → `init_pygame()` on `_IPUI`
- [ ] **RENAME ATTR** `layout_engine` → `layout_engine` on `_baseForm`
- [ ] **RENAME ATTR** `_active_tab` → `active_tab_name` on `TabStrip`

### Guido Underscore Cleanup (safe, grep-and-replace)

- [ x] `MeasureAndWrap`: `_engine` → `engine`
- [ x] `MeasureAndWrap`: `_is_text_like_leaf` → `is_text_like_leaf`
- [ x] `MeasureAndWrap`: `_render_wrapped_surface` → `render_wrapped_surface`
- [ x] `MeasureAndWrap`: `_wrap_greedy_first_fit` → `wrap_greedy_first_fit`
- [ x] `MgrColor`: `_hover_cache` → `hover_cache`
- [ x] `MgrFont`: `_regular_font_source` → `regular_font_source`
- [x ] `MgrFont`: `_bold_font_source` → `bold_font_source`
- [x ] `MgrFont`: `_light_font_source` → `light_font_source`
- [x ] `MgrFont`: `_mono_font_source` → `mono_font_source`
- [x ] `MgrFont`: `_font_cache` → `font_cache`

### Service Class Renames (safe)

- [ ] `Clipboard` → `MgrClipboard` (file: `MgrClipboard.py`)
- [ ] `FileManager` → `MgrFile` (file: `MgrFile.py`)
- [ ] `Logger` → `MgrLog` (file: `MgrLog.py`, `Log` data class stays in same file)

### Style Constant Fix

- [ ] `Style.FONT_SCALE` → `Style.FONT_SCALE`

### Housekeeping (nice to have before v0.1)

- [ ] Delete or differentiate clone panes: `Settings.py`, `Iamnothere.py` (near-identical to `Overview.py`)
- [ ] Update `__init__.py` re-exports for all renames
- [ ] Verify `TemplateStarterKit.py` `method_1_IPUI_TAB_BUILDER` convention is documented as Designer pattern

---

*End of IPUI Naming Audit.*