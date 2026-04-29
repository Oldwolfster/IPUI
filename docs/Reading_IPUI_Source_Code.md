# Reading IPUI Source

> A guide for anyone reading or contributing to the IPUI codebase.
> Welcome — glad you're here. This page tells you what the bar is.

IPUI is opinionated about how its source code is *written*, not just what it does. The opinions are deliberate, and most of them push against common industry conventions. If something looks unusual, it's almost always on purpose. This doc explains the conventions and the reasoning behind them, so you can read IPUI source fluently and contribute code that fits the style.

The short version: **IPUI optimizes for the human reading the code, not the tool processing it.** Every convention below follows from that one rule.

---

## Names are the API

Names do most of the work in any codebase. Strip away the syntax — the parens, the colons, the `def` and `class` keywords — and what's left is almost entirely names. Names *are* the language the code is written in. IPUI takes naming seriously.

**Long, honest names beat short clever ones.** Modern languages allow ~255 characters; we're nowhere near the limit. A name's job is to eliminate ambiguity at the call site, so the reader never has to check the implementation to know what the function does.

```python
# Acceptable
compute_pane_outer_height()

# Better
compute_pane_outer_height_including_border_and_padding()
```

You type the name once. Autocomplete fills it the next 50 times. You *read* the name 100x for every time you type it. The reading-cost calculation favors length — assuming length buys clarity, which it should.

**The names you reach for reveal the model in your head.** Hooks named `ip_think` / `ip_draw` / `ip_draw_hud` aren't relabeled `update`/`render`/`render_overlay` — they encode a different worldview. `ip_` says "framework lifecycle." `think` says "decisions happen here, not just state mutation." Names enforce the model. People who write IPUI code gradually start thinking the way the names think.

**Public names are promises.** Once `ip.dt` is in someone else's code, you can't rename it without breaking them. Pre-1.0 is the only window to keep changing public names. Internal names you can refactor forever; public names harden the moment v1.0 ships. When in doubt, don't expose. You can always loosen later. You can never tighten.

---

## Comments are for the writer first, the reader second

Conventional wisdom says comments are charity for some hypothetical future maintainer. That framing is wrong, or at least badly out of order. The real beneficiaries are, in order:

1. **You, ten minutes from now**, debugging the thing you just wrote
2. **You, tomorrow morning**, picking up where you left off
3. **You, next month**, fixing a related bug
4. **You, six months from now**, modifying it
5. *Way down the list:* some future maintainer

When you write a comment, you're forced to articulate intent in a different language than the code itself. That translation step is where bugs surface. You write `# sum content + padding + border` and halfway through typing it you go *"...wait, am I including border? Let me check."* The comment caught the bug before you had one. **It paid for itself in the same sitting, before anyone else ever read it.**

Reframing comments this way completely flips the cost calculation. They're not slowing you down to help someone else — they're saving *you* five minutes of debugging in the next hour, in exchange for fifteen seconds now. That's not generosity. That's *self-interest correctly understood.*

### Comment liberally, including "obvious" lines

The convention "don't restate the obvious" gives lazy developers cover, and it misses two real benefits of restating:

**Scannability.** A column of right-aligned trailing comments creates a parallel reading track. Your eye scans the comment column at 5x the speed of the code, picking up intent without parsing syntax. That's a genuine ergonomic win. The convention dismisses it because it's invisible to anyone who hasn't tried it consistently.

**Confidence.** When a reader scanning unfamiliar code hits `i = i + 1  # increment counter`, the comment isn't teaching them what `i = i + 1` does — it's *confirming* that this is a routine increment, not something subtler that warrants slowing down to investigate. The comment grants permission to skim. Comments reduce cognitive load even when they don't add information.

**Cross-checking.** A small punctuation shift — an extra semicolon, a flipped operator, a missing `not` — can reverse meaning without obvious symptoms. A comment stating intent gives you something to check the code *against.* If the comment and the code disagree, one of them is wrong. Without the comment, you have nothing to cross-reference.

### What this looks like in practice

```python
class Status(_BaseTab):                            # Status (tab) from the dict key
    def mood(self, parent):                        # mood (pane) from Status' list
        Heading(parent, "Filename: Status.py")     # parent parameter is the 'branch'
        Heading(parent, "Method: is_it_growling")  # add widgets to parent
        Heading(parent, "Add content here!")       # whole branch builds from parent
```

A reader scanning the right column gets the entire teaching narrative without reading code. A reader scanning the left gets the mechanical structure. Both at once gives both, fast. Three reading speeds for three different needs, all available simultaneously.

### When *not* to comment

The discipline isn't literally annotating every statement. Pure pass-through lines with no neighbors and no subtlety can stand alone. The rule is closer to: **if the surrounding lines have aligned trailing comments, fill the column on this line too**, even if the comment just confirms the obvious — because preserving the column preserves the scan-the-right-column property.

---

## Vertical alignment

Aligned code reads in columns. IPUI aligns assignment operators, parameter lists, repeated builder calls, and structurally identical adjacent statements:

```python
self.ball_r        = 0.015
self.paddle_w      = 0.15
self.paddle_h      = 0.02
self.paddle_y      = 0.95
self.hitbox_extra  = 0.02
self.auto_paddle   = 0.5
self.base_speed    = 0.5
```

The reader's eye scans the value column without re-parsing the variable names on each line. Repeated structural sections become *visually obvious* as a group. The convention is unusual — most autoformatters strip it, and most IDEs don't help maintain it — but the readability gain is the point. **Don't run autoformatters on IPUI source.**

The diff cost is real. Changing one line means realigning several. We accept that cost. The minutes lost to alignment maintenance are dwarfed by the hours saved scanning aligned code over the lifetime of the codebase.

---

## Method size

| Length | Verdict |
|--------|---------|
| 5 lines | Target |
| 20 lines | Rare exception |
| 40 lines | Throwing the laptop out the window |

Small methods aren't an aesthetic preference. They're a **structural forcing function** on the entire codebase. A 5-line method is forced to be either pure logic or pure orchestration — it can't be both. Which means the codebase is forced to layer itself. Which means it stays readable as it grows.

### Listing-only methods are encouraged

A method whose body is just calls to other named methods is *executable prose*:

```python
def render_frame(self):
    compute_layout_for_dirty_panes()
    propagate_pipeline_updates()
    fill_panes_with_widgets()
    draw_widgets_to_screen()
    draw_hud_overlays()
```

You read the body and you have a complete summary of what happens, in order, without skimming logic. The names *are* the documentation. Each step is named, so each step is testable, mockable, and extractable. Reordering steps is a one-line change. Removing one is a one-line change.

The orchestration layer ("what we do") and the implementation layer ("how we do each step") live at different altitudes. When you're trying to understand the flow, you read the orchestrator. When you're fixing a bug in step 2, you read step 2. You're never reading the wrong altitude.

If a method gets long, the fix is usually to **extract a named sub-step**, not to add comments inside the long version.

---

## File and class organization

- **One class per file**, named identically. Locating any class is `class_name.py`. No grep required.
- **All code lives in classes.** This protects against import-order surprises and accidentally-executed module-level code.
- **`private_` prefix** for backing storage attributes (e.g. `private_enabled`). The Python convention of leading underscore is *not* used in IPUI — `private_` is more searchable, more honest, and forward-compatible with a future `public_` prefix.
- **`SCREAMING_CASE`** for structural class-level declaration dicts (`TAB_LAYOUT`, `DECLARATION_UPDATES`).
- **`ip_` prefix** is reserved for per-frame pane lifecycle hooks (`ip_setup`, `ip_think`, `ip_draw`, `ip_draw_hud`). Don't prefix anything else with `ip_`.
- **`on_` prefix** is reserved for event properties (`on_click`, `on_change`) — things you assign callbacks to.
- **`handle_` prefix** for handler methods that respond to events.

---

## Philosophy

These conventions all flow from a few framework-level commitments. Knowing the commitments helps you make consistent calls in cases the conventions don't cover.

### Pit of success

The API tries to shove the caller toward correct usage. Defaults and structure should make correct usage *easier* than incorrect usage. If a user can do something wrong, eventually a user will. Better to make wrong usage impossible than to document the right way.

### Construction IS attachment

If you build a widget inside a container, it's attached to that container. No `add()` calls, no `manager=manager` parameters, no orphaned widgets. The framework already has the parent context — it doesn't need the user to pass it again.

This is the most quotable instance of a deeper principle: **the framework knows what it knows.** When the framework already has information, the user shouldn't have to provide it. This shows up everywhere — tab discovery from filenames, the global widget registry, the `ip` service portal, the reactive pipeline DAG. Each one is the same move: notice that the answer is already in the system, and stop asking the user for it.

### O(1), not O(N)

Every framework decision lives on one side of a line:

- **Framework-side — O(1).** Solved once, inside the framework. Every user gets it for free. Zero defect surface for the user. Zero tech debt for the user.
- **User-side — O(N).** Every user re-solves it for each usage. Each solution carries a fixed build cost, widens the defect attack surface, and accumulates ongoing tech debt.

IPUI pushes as much as possible to the framework side. When something can be handled once — reliably, invisibly — there's no reason to ask every user to handle it themselves, every time, forever.

### Sit with awkwardness before papering over it

When something feels awkward in IPUI, don't immediately add a convenience method to smooth it. Sit with the awkwardness for a while. Sometimes it's just awkward and the convenience method is the right answer. But sometimes the awkwardness is telling you that you're modeling the wrong thing, and the next "construction IS attachment" insight is on the other side of that pause.

The cleanest features are the ones where the implementation is *"stop pretending this isn't already true."* They cost nothing to add because they're not really features — they're just the framework being honest about what it already does.

---

## Things to do, things not to do

**Do:**
- Write docstrings on every method. Always.
- Comment liberally. Use trailing comments aligned in columns.
- Use long, honest names. Autocomplete handles the typing.
- Keep methods at 5 lines. Extract named sub-steps when they grow.
- Align assignments, parameter columns, and adjacent structural code.
- Use `private_` for backing storage. `_BaseClass` only for the deliberate user-facing bases.
- Sit with awkwardness before adding convenience methods.

**Don't:**
- Don't use leading underscores on methods (Guido's convention is not used here).
- Don't strip existing comments. Comment-removal decisions belong to the maintainer.
- Don't run autoformatters that strip alignment.
- Don't shorten names for typing convenience. The reader pays, not you.
- Don't expose new names in the public API casually. Pre-1.0 flexibility is finite.
- Don't add convenience methods to paper over awkward APIs without first asking whether the awkwardness is structural.

---

## A note on conventions vs. rules

These are conventions, not laws. They exist because over time, code that follows them is dramatically easier to read, maintain, and extend than code that doesn't. If you find yourself fighting one of them in a specific case, that's worth a conversation — sometimes the convention has an edge case worth carving out, and sometimes the fight reveals that the code is doing the wrong thing.

But the default is: **follow the conventions, even when they look unconventional.** The whole codebase reads as one voice precisely because everyone holds to the same shape. That coherence is part of what makes IPUI worth contributing to.

Welcome aboard.