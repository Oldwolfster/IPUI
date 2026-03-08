# IPUI Layout Engine — How Your Widgets Get Sized

## The Short Version

You tell IPUI **what** you want. IPUI figures out **where** it goes.

- Set `width_flex` or `height_flex` to request proportional space.  These default to one.
- Don't change the default, all siblings will be sized identical, gapped only by spacing tokens 
- 
- Make a container `scrollable=True` and overflow is handled for you.
- That's it. No `LayoutParams`, no `BoxConstraints`, no `MediaQuery`. Just build.

---

## Two Axes, Two Philosophies

IPUI treats width and height differently — because screens do.

**Width** is assigned **top-down**. Your parent decides how wide you are, usually through flex ratios. Content adapts to fit: text wraps, grids resize, code clips.

**Height** is measured **bottom-up**. Your content decides how tall you are. If there's more content than space, the container scrolls.

This matches how every UI actually works: you know your width (the screen gives it to you), but your height depends on what you're showing. IPUI just makes it explicit.

---

## The Three Layout Rules

Every widget in the tree gets sized by three rules, applied in priority order.

### Rule 1 — Minimum Size Is Sacred

Every widget has an intrinsic minimum: the smallest it can render without losing meaning. A button needs room for its text. A card needs room for its children. This minimum is measured bottom-up — children first, then parents.

**IPUI will never render a widget smaller than its minimum.** If there isn't enough room, something will clip — but the widget that got its space earned it honestly.

### Rule 2 — Flex Distributes the Leftovers

After every widget gets its minimum, the remaining space is distributed proportionally by flex weight.

```python
Row(parent)
Button(row, "Save",   width_flex=1)   # gets 1/3 of leftover
Button(row, "Cancel", width_flex=1)   # gets 1/3 of leftover
Button(row, "Help",   width_flex=1)   # gets 1/3 of leftover
```

Set `width_flex=3` on one and `width_flex=1` on another? The first gets 3× the leftover space. The ratios are relative — `1:1:1` is identical to `5:5:5`.

If a flex widget's minimum exceeds its fair share, it gets locked at its minimum and removed from the pool. The remaining widgets split what's left. This repeats until every widget has a fair deal — or runs out of room trying.

### Rule 3 — Clip If You Must

If the total minimums exceed the available space, there's no magic. Content clips at the container boundary. But Rules 1 and 2 guarantee that the clipping is fair: every widget got at least its minimum before anyone started losing pixels.

---

## Flex In Practice

### Vertical Stacks (the default)

Widgets stack top to bottom. `height_flex` widgets how they share vertical space. Width is inherited from the parent.

```python
card = CardCol(parent, height_flex=1)
Title(card, "Header")                     # intrinsic height — just enough for text
Body(card, "Some content")                # intrinsic height
Spacer(card, height_flex=1)               # absorbs all remaining vertical space
Button(card, "Submit")                    # intrinsic height, pinned to bottom
```

### Horizontal Stacks (Row / CardRow)

Widgets sit side by side. `width_flex` widgets how they share horizontal space. Height is inherited from the parent.

```python
row = Row(parent)
CardCol(row, width_flex=1)    # left pane  — 1/4 of the width
CardCol(row, width_flex=3)    # right pane — 3/4 of the width
```

### Mixing Fixed and Flex

Non-flex children get measured first. Flex children split what's left.

```python
row = Row(parent)
Button(row, "OK")                 # fixed width — measured from text
Spacer(row, width_flex=1)         # eats all the leftover space
Button(row, "Cancel")             # fixed width — measured from text
```

Result: two buttons hugging the edges, empty space in between.

---

## Scrollable Containers

Add `scrollable=True` to any CardCol and overflow is handled automatically.

```python
card = CardCol(parent, scrollable=True)
for i in range(100):
    Body(card, f"Item {i}")
```

That's it. You get a scrollbar, mouse wheel support, and proper clipping. No viewport setup, no scroll controller, no content size calculation.

**How it works under the hood:**

A scrollable container tells the flex solver "I don't need much height — just give me whatever flex says." It stores its full content height separately for scroll math. This means a scrollable card with 1000 items doesn't hog all the vertical space from its siblings.

You don't need to set `height_flex` — `scrollable=True` implies it. One parameter, done.

**One rule:** Don't put `height_flex` on children inside a scrollable container. Flex expands to fill available space; scrollable needs content *bigger* than the viewport. They're contradictory — IPUI will tell you if you try.

---

## Why Your Layout Is Stable

If you set `width_flex=1` on two panes, they stay equal — regardless of content.

A pane with `width_flex` doesn't let its children's width propagate up to the flex solver. It's saying "I'll take whatever proportional space you give me." The content inside adapts: text wraps, grids resize, long lines clip.

This means changing content — clicking a different item, loading new data, resizing text — doesn't cause the pane widths to jump. The layout is stable because flex ratios are honored, not overridden by content.

---

## The Flex Solver — What Actually Happens

For the curious, here's the algorithm. You never need to think about this, but it might help your intuition.

1. **Measure** every child bottom-up. Each widget reports its minimum size.
2. **Lock** non-flex children at their minimum. Subtract from the budget.
3. **Calculate** fair share for each flex child: `(remaining space / total flex weight) × this child's weight`.
4. **Find violators**: any flex child whose minimum exceeds its fair share.
5. **Lock the biggest violator** at its minimum. Remove it from the flex pool.
6. **Repeat** steps 3–5 until no violators remain.
7. **Assign** remaining flex children their (now larger) fair share.
8. **Set rects** and recurse into children.

The solver is greedy-iterative: it locks one violator per pass and never backtracks. This converges in at most N passes for N flex children — typically 1 or 2 for real-world layouts.

The biggest violator gets locked first because it's the one that *can't* flex anyway. Locking it frees up space for the others, giving them the best shot at honoring their ratios.

---

## Quick Reference

| You Want | You Write |
|---|---|
| Equal width panes | `width_flex=1` on each |
| 25/75 split | `width_flex=1` and `width_flex=3` |
| Pin to bottom | `Spacer(card, height_flex=1)` above it |
| Scrollable list | `CardCol(parent, scrollable=True)` |
| Centered content | `Row(parent, justify_center=True)` |
| Spread to edges | `Row(parent, justify_spread=True)` |
| Fixed-size widget | Don't set `width_flex` or `height_flex` |

---

## Common Patterns

**Header + Content + Footer:**
```python
card = CardCol(parent, height_flex=1)
Title(card, "My App")                          # top
content = CardCol(card, height_flex=1)         # fills middle
Button(card, "Done")                           # bottom
```

**Sidebar + Main:**
```python
row = Row(parent, height_flex=1)
CardCol(row, width_flex=1)                     # sidebar
CardCol(row, width_flex=3)                     # main area
```

**Scrollable List with Fixed Header:**
```python
Title(parent, "Items")                          # fixed at top
card = CardCol(parent, scrollable=True)         # scrolls
for item in items:
    Body(card, item)
```

**Dynamic Content That Doesn't Break Layout:**
```python
# Pane widths stay at 1:3 regardless of what's inside
row = Row(parent, height_flex=1)
left  = CardCol(row, width_flex=1)              # always 25%
right = CardCol(row, width_flex=3)              # always 75%
# Content inside wraps, clips, or scrolls — never bulldozes the ratio
```
