# IPUI UI Wireframes  (UI.md)

A text wireframe for thinking through an IPUI screen *before* writing any code.
**Indentation IS attachment** — the same rule the framework enforces, written in prose.

##
You're the UI design lane for an IPUI app. Your job, right now, is to design a
screen as a TEXT WIREFRAME in the UI.md convention — before any code exists.
The wireframe is a thinking tool: we move lines around until the layout makes
correct usage obvious, THEN code follows. Indentation IS attachment; a region
that morphs is a SPLIT with WHEN: branches. Use the wireframe to find the BEST
UI, not to transcribe a decided one.

Resist opening any other source. Cheap iteration in MD beats spelunking code.
If you need a fact that isn't in those three files, ASK me — don't go reading
for it.

How we work:
- Reflect your understanding back BEFORE you produce, so I can correct it first.
- Design in the UI.md grammar. One question at a time when you're unsure.
- The deliverable is the wireframe, not code. Don't jump to code.
- Standard project conventions still apply.


## Use this to design, not just describe
Rearranging lines here is free; rearranging code is not. Draft the tree, move
things, cut things, find the layout that makes correct usage obvious — *then*
code it. The wireframe earns its keep before a single widget exists.

## Before reading a wireframe, read three things
1. **ToDoBB.md** — the entire Project Summary (the first `##` section). App specifics.
2. **UI.md** — this rules section only (you're in it). The grammar below.
3. **FormBaseball.py** — top of file through the `TAB_LAYOUT` assignment. The roots.

## The grammar — every line starts with a widget type or SPLIT
- `#`   Form          — one per app (the trunk of everything).
- `##`  Tab           — a tab from `TAB_LAYOUT`.
- `###` Root: name    — a pane from that tab's `TAB_LAYOUT` list. `name` is the wiring.
- `Widget`            — nesting = containment. A child line lives *inside* its parent.
- `SPLIT`             — a swap point (see below). May appear at any depth.

The only non-type line is `WHEN:`, and it appears solely as a child of `SPLIT`.
Stacks vertically by default. `Row` is a horizontal container.

## Annotations — only the minimum to express intent
- `"label"`     widget text / identity
- `[behavior]`  opt-in capability      e.g. `[scroll]`
- `→ handler`   event handler          e.g. `→ handle_run_all`
- `← source`    data source / key      e.g. `← registry table`

Everything else is left for code time.

## Swapping content — SPLIT, at any depth
A region can morph based on state or action — and that region can sit *anywhere*
in the tree, not just at a root. Mark the swap point `SPLIT` and give each state
a `WHEN:` branch with its own subtree:

- `SPLIT`                      a swap point (its own line, any depth)
- `WHEN: <state>  (default)`   the state shown first
- `WHEN: <state>`              every other state, each with a subtree below

Optional: `WHEN: <state>  → handler` names the method that flips to it.
The point is to decide which states a region needs — and what flips between them
— here, before coding.

---

# Form: Baseball

## Tab: Workshop

### Root: source
- Row
  - Title  "SOURCE THAT FEEDS TABLE: pull_{table}"
  - Button "Edit View"  → handle_edit_primary
- CardCol
  - CodeScroller  ← primary pull view SQL
- CardCol
  - SPLIT
    - WHEN: browsing mixins  (default)
      - PowerGrid  ← mixin list
    - WHEN: a mixin is selected
      - CodeBox  ← selected mixin SQL
    - WHEN: editing a view
      - TextArea  ← view SQL  [scroll]
    - WHEN: creating a view
      - TextBox "Name"  → update_name
      - Row
        - Button "For Insert"
        - Button "Update After"
      - TextArea "What this view accomplishes"
      - SelectionList  ← target columns