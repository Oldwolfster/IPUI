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
BINDINGS = {
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


### 11. C(n) — Code Complexity Notation

Big-O notation measures **runtime cost** as input grows. C(n) measures **code cost** as the system grows.

It is *not* about how much code it took to build a feature the first time. The first write is a one-time tax nobody remembers a week later. C(n) is about the **ongoing friction** of extending the system: once the ETL system exists, what does it cost to add the Nth table? Once the widget system exists, what does it cost to add the Nth widget? Once the form system exists, what does it cost to add the Nth tab?

- **C(1)** — Adding the Nth thing costs the same as adding the 1st. The framework absorbs growth. You write the thing; nothing else changes.
- **C(log n)** — A small, bounded edit somewhere central (registry, dispatcher) per addition. Tolerable, but watch for drift.
- **C(n)** — Every new addition is another paper cut at a call site, a registry, a dispatch table, a migration. The cuts compound. The system gets *harder* to extend the more it grows.

Framework design is the business of trading a one-time cleverness tax (the `scan_methods` machinery, the `TAB_LAYOUT` engine, the `_BaseWidget` capability layer) for a **permanent C(1) extension cost**. That trade is almost always worth it. Cleverness pays off forever; friction compounds forever.

#### Example: ETL Schema Registration

```python
# C(n) — every new table is another edit to build_schema()
def build_schema(self):
    self.create_runs_table()
    self.create_batches_table()
    self.create_metrics_table()
    self.create_checkpoints_table()
    # ...add the next table here, AND here, AND remember the dispatch list...

# C(1) — scan_methods does the registration; adding a table IS registering it
def build_schema(self):
    for name, method in self.scan_methods("schema_"):
        method()

def schema_runs(self):         ...
def schema_batches(self):      ...
def schema_metrics(self):      ...
def schema_checkpoints(self):  ...
# Adding schema_foo() is the entire change. No central edits, ever.
```

#### Example: IPUI's C(1) Bets

- **Adding a widget to `_BaseWidget` capability layer** → every existing widget gains the behavior for free. C(1) on a permanent axis.
- **Adding a tab to a form** → one entry in `TAB_LAYOUT`. C(1).
- **Adding a new style token** → one entry in `Style`. C(1) globally.
- **Adding a custom widget** → subclass `_BaseWidget`. Layout, events, scrolling, styling come free. C(1).
- **Adding a column to a `PowerGrid`** → one entry in the column declaration. C(1).

#### When to Reach For It

C(n) is a **design lens**, not a label to slap on after the fact. The right time to ask it is *before* committing to an API shape:

> "What's the C(n) of adding the Nth X through this interface?"

If the answer is C(n), the design is wrong and the cost will be paid forever. Stop, redesign, push the work down to the framework so users pay C(1).

#### Vocabulary Note

C(n) is distinct from O(n). When the context is ambiguous, say **"code complexity"** or **"extension cost"**. When the context is clear (a design discussion, a commit message about API shape), `C(1)` and `C(n)` read naturally and pattern-match the existing big-O muscle memory.

---






# Dashboard.py  Naming_And_Conventions.md  NEW section: Anti-Rug-Slide Rules
# Lessons from the expected_runs/resolve_total incident, May 14 2026.

## Anti-Rug-Slide Rules (a.k.a. "How To Stop Silent Failures")

These rules exist because silent failures are the opposite of the Sacred Laws.
A column that doesn't exist returning 0 looks identical to a column that exists and is zero.
A `try/except: return None` looks identical to a clean no-result. Loud errors are gifts.

1. **Verify names against live code, not greps.**
   A grep hit can be a comment, a stale variable, or a dead code path.
   Before relying on a name (column, method, attribute), confirm it appears in
   currently-running code, not just somewhere in the source tree.

2. **No `or 0` / `or ""` / `or []` on database results unless NULL is a
   designed-for valid value.**
   A column in the SELECT that returns NULL should be handled by an explicit
   `if x is None:` branch with reasoning. `or 0` collapses three states
   (NULL, 0, missing column) into one, hiding bugs.

3. **No averaging / max-ing / picking between two sources of the same fact.**
   If you don't know which source is authoritative, stop and ask.
   "Take the bigger one" is superstition, not engineering. Exactly one
   source is the truth; the other doesn't exist or is wrong.

4. **No bare `except Exception: return None` in new code.**
   Either catch a specific expected exception, or let it propagate so EZ.err
   reports the real problem with the real location. Bare catches turn a
   3-second fix into a 3-day mystery.

5. **Screenshots of schemas, errors, and UI state are ground truth.**
   If a screenshot shows the schema, use that schema. Don't half-remember
   what columns "probably exist." Re-read the screenshot every time SQL is
   written.
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

