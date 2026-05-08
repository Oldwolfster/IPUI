# Build Brief: A Mini Trello-Style Board

## Goal

Build a single-page app called **MiniBoard** using IPUI. Use *only* what is documented in the README. Do not invent APIs or guess at undocumented features — if the README does not show something, work around it.

## What it does

A simple kanban-style board with three columns side by side: **To Do**, **Doing**, and **Done**.

- **One tab with three panes**, one pane per column.
- Each pane is a vertical list of **cards** (just text, one short string per card).
- A card can be **moved** between columns. Any expression works — explicit "→" / "←" buttons on each card are fine, a click-to-cycle button is fine, drag is bonus but not required.
- The **first pane (To Do)** has an input box and an **"Add"** button at the top to create a new card.
- Each pane shows a small **count above its list** (e.g. "To Do (3)"), updating live as cards move.
- The **third pane (Done)** has a **"Clear Done"** button at the bottom that removes all its cards.

## Constraints

- One file only. Name it `MiniBoard.py`.
- Use `_BaseForm` with `TAB_LAYOUT`. One tab, three panes.
- All state lives in pipeline keys or instance attributes. No global variables.
- Use the framework's reactivity where it fits naturally. Don't force it; don't avoid it.
## What we're testing (don't optimize for this — just be honest)

When you're done, briefly note:

1. Any places where you weren't sure which IPUI feature to reach for
2. Any places where you wrote more boilerplate than felt right
3. Any places where the README didn't quite answer your question and you had to guess
4. Any places where IPUI made something easier than you expected

## What you have

The IPUI README (provided). That's it. Treat it as the single source of truth.

## What you don't need to do

- Persist anything to disk
- Edit card text after creation
- Reorder cards within a column
- Style anything beyond what comes for free
- Handle errors elegantly
- Write tests