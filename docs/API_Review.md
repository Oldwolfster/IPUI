# IPUI v0.1 — API Surface Review

Concise catalog of every public name a user can touch.  
**⚠️** = naming concern or inconsistency.

---

## 1. Module Entry Point

| Name | What |
|------|------|
| `show(FormClass, title)` | Launch app or switch form |
| `back()` | Return to previous form |

```python
from ipui import *
show(MyForm, "My App")
```

---

## 2. Base Classes (user inherits from these)

| Class | File | Purpose |
|-------|------|---------|
| `_BaseForm` | `_BaseForm.py` | App root. Manages tabs, pipeline, modals |
| `_BaseWidget` | `_BaseWidget.py` | All widgets inherit from this |
| `_BaseTab` | `_BaseTab.py` | Tab content builder |

**⚠️ CASING INCONSISTENCY:** `_BaseForm`, `_BaseWidget` are PascalCase.  
`_BaseTab` is camelCase. Docs and code are mixed. NamingConventions.md says `_Base` prefix for all three.

---

## 3. _BaseForm — Class Attributes (user declares)

| Name | Type | What |
|------|------|------|
| `TAB_LAYOUT` | dict | Tab name → pane method list |
| `tab_early_load` | list | Tabs to pre-build at startup |
| `tab_hidden` | list | Tabs initially hidden |
| `tab_on_change` | str | Method name called on tab switch |
| `tab_border` | int | Tab strip border override |
| `pipeline_debug` | bool | Log pipeline activity |

---

## 4. _BaseForm — Methods

| Method | What |
|--------|------|
| `pipeline_set(key, value)` | Write to reactive pipeline |
| `pipeline_read(key)` | Read from pipeline |
| `switch_tab(name)` | Switch to named tab |
| `hide_tab(name)` | Hide a tab |
| `show_tab(name)` | Show a hidden tab |
| `get_tab(name)` | Get cached pane instance |
| `prepare(name)` | Force-load a tab's pane |
| `set_pane(index, builder)` | Replace pane content at runtime |
| `refresh_pane(index)` | Rebuild current pane |
| `show_modal(msg, func, min_sec)` | Show modal dialog |
| `register_derive(...)` | Register a reactive derivation |
| `ip_think(ip)` | Per-frame logic hook |
| `ip_draw(ip)` | **⚠️** Pre-UI drawing hook |
| `ip_draw_hud(ip)` | **⚠️** Post-UI drawing hook |

**⚠️ `ip_draw` / `ip_draw_hud`:** You flagged these as names you hate.

---

## 5. _BaseTab — Attributes & Hooks

| Name | Type | What |
|------|------|------|
| `DECLARATION_UPDATES` | dict | Reactive derive declarations |
| `form` | ref | Parent form (auto-set) |
| `ip` | ref | IP service portal (set each frame) |

| Hook | When |
|------|------|
| `ip_setup_pane()` | One-time setup |
| `ip_think(ip)` | Every frame — logic |
| `ip_draw(ip)` | **⚠️** Before UI draws |
| `ip_draw_hud(ip)` | **⚠️** After UI draws |

| Helper | What |
|--------|------|
| `swap_pane(index, builder)` | Returns a lambda for pane swapping |
| `hide_extra_panes(keep_count)` | **⚠️** Hides panes beyond keep_count. Unclear name. |

**⚠️ NamingConventions.md says `hook_` prefix** for lifecycle hooks.  
Actual code uses `ip_` prefix. The doc is stale or the decision changed.

---

## 6. _BaseWidget — Constructor Parameters

Every widget accepts:

| Param | Default | What |
|-------|---------|------|
| `parent` | — | Parent widget (required, auto-attaches) |
| `text` | None | Display text |
| `name` | None | Registers in `form.widgets[name]` |
| `width_flex` | 0 | Horizontal flex weight (0 = natural) |
| `height_flex` | 0 | Vertical flex weight (0 = natural) |
| `pad` | TOKEN_PAD | Internal padding |
| `gap` | TOKEN_GAP | Gap between children |
| `border` | TOKEN_BORDER | Border thickness |
| `justify_center` | False | Center children |
| `justify_spread` | False | Spread children evenly |
| `visible` | True | Show/hide |
| `enabled` | True | False or reason string |
| `font` | None | Override font |
| `text_align` | `'l'` | `'l'`, `'c'`, `'r'` |
| `color_bg` | None | Background RGB |
| `glow` | False | Molten glow effect |
| `wrap` | False | Word wrap |
| `data` | None | Arbitrary payload |
| `single_select` | False | Enforce single selection |
| `placeholder` | None | TextBox placeholder |
| `initial_value` | None | Starting value |
| `on_click` | None | Click callback |
| `on_change` | None | Change callback |
| `on_submit` | None | Submit callback |
| `pipeline_key` | None | Pipeline read/write key |
| `tooltip_class` | None | Custom tooltip class |
| `scrollable` | False | Enable scrolling |
| `scroll_glow` | 0.369 | Scrollbar bevel intensity |
| `start` | None | CodeBox range marker |
| `end` | None | CodeBox range marker |
| `early_load` | None | **⚠️** On the base constructor but only used by tabs? |

---

## 7. _BaseWidget — Public Methods

| Method | What |
|--------|------|
| `set_text(text)` | Update text, rebuild |
| `set_disabled(reason="")` | Disable with optional tooltip reason |
| `set_enabled()` | Re-enable |
| `clear_children()` | Remove all children |
| `on_click_me(callback)` | **⚠️** Register click handler. Awkward name. |
| `tap(func)` | **⚠️** Inline post-construction helper. Undocumented in README. |

---

## 8. _BaseWidget — Public Properties

| Property | What |
|----------|------|
| `display_name` | Human-readable identity (name → text → type) |
| `frame_size` | Total inset: `(pad + border) * 2` |
| `visible_children` | Children that participate in layout |
| `enabled` | Property with setter that triggers rebuild |

---

## 9. Widget Catalog

### Text Hierarchy (all inherit from Label)

| Widget | Font | Purpose |
|--------|------|---------|
| `Label` | FONT_BODY | Base text renderer |
| `Banner` | FONT_BANNER | App title |
| `Title` | FONT_TITLE | Section header |
| `Heading` | FONT_HEADING | Subsection label |
| `Body` | FONT_BODY | Workhorse text |
| `Detail` | FONT_DETAIL | Fine print |

All support: `set_text()`, `glow=True`, `text_align`, word wrap.

### Layout Containers

| Widget | Direction | Chrome | Key Feature |
|--------|-----------|--------|-------------|
| `Row` | Horizontal | None | Pure structure |
| `Col` | Vertical | None | Pure structure |
| `CardRow` | Horizontal | Beveled bg | Visual container |
| `CardCol` | Vertical | Beveled bg | `scrollable=True` |
| `Card` | Vertical | Beveled bg | Simple wrapper |
| `Spacer` | — | None | Flex filler |

### Interactive Widgets

**Button**
- `set_disabled(reason)`, `set_enabled()`
- `set_radiate()` — hot bevel + bottom glow
- `on_click_me(callback)` **⚠️**
- Auto hover/press/disabled color math

**TextBox** (extends Label)
- `set_text(text)`, `set_focus()`, `submit()`
- `sync_from_pipeline()`
- Cursor, selection, clipboard, click-to-position

**TextArea** (extends TextBox)
- Multi-line, wrapping, vertical cursor nav
- Same API as TextBox

**SelectionList**
- `get_selected()` → list of names
- `get_selected_data()` → dict of name:data
- `set_filter(text)`
- `sync_from_pipeline()`
- `selected_count` property

**DropDown**
- `get_selected()`, `get_selected_data()`
- `set_filter(text)`
- `set_max_visible(n)`
- `sync_from_pipeline()`

**PowerGrid**
- `set_data(rows, columns=None)` — lists/dicts
- `set_data(path, query=sql)` — SQLite query
- `set_data(path, table=name)` — SQLite table
- `set_column_max(col_name, width)`
- `set_page_size(n)`
- `on_row_click(callback, key_col)`

**ChartWidget**
- `set_data(lines, x_label, y_label)`

**CodeBox**
- Read-only. Pass `data=method_ref`, optional `start`/`end` markers.

**NetworkDiagram**
- `set_layers(layers)`, `set_selected(index)`
- `on_layer_selected` callback

**RecordSelector** (pagination)
- `set_data(total_rows, page_size)`
- `go_to_page(n)`

**SelectableListItem** (internal, used by SelectionList)
- `toggle_selected()`, `apply_selection_visual()`

---

## 10. `ip` — Service Portal

Passed to `ip_think(ip)`, `ip_draw(ip)`, `ip_draw_hud(ip)`.

### Identity
`ip.form`, `ip.form_name`, `ip.pane`, `ip.pane_name`, `ip.is_active_pane`

### Timing
`ip.dt`, `ip.fps`, `ip.frame`, `ip.elapsed`

### Geometry
`ip.rect_pane`, `ip.rect_tab_area`, `ip.rect_screen`

### Coordinate Helpers
`ip.to_screen(nx, ny)`, `ip.to_local(sx, sy)`,
`ip.scale_x(n)`, `ip.scale_y(n)`,
`ip.local_to_screen(x, y)`, `ip.screen_to_local(x, y)`

### Mouse
`ip.mouse_x`, `ip.mouse_y`, `ip.mouse_pos`, `ip.mouse_wheel`
`ip.mouse_down(btn)`, `ip.mouse_pressed(btn)`, `ip.mouse_released(btn)`
`ip.mouse_inside(widget)`, `ip.mouse_inside_pane()`, `ip.mouse_inside_content()`
`ip.mouse_hits(rect)`, `ip.mouse_local_pos()`, `ip.mouse_local_x()`, `ip.mouse_local_y()`

### Keyboard
`ip.mod_shift`, `ip.mod_ctrl`, `ip.mod_alt`
`ip.key_down(key)`, `ip.key_pressed(key)`, `ip.key_released(key)`

### Rendering
`ip.surface`, `ip.events`, `ip.unhandled`

### Cache (scratch pad, NOT reactive)
`ip.cache_get(key, default)`, `ip.cache_set(key, value)`,
`ip.cache_has(key)`, `ip.cache_del(key)`

### Discovery
`ip.find("name")`, `ip.help()`, `ip.help("topic")`

### Invalidation (scaffolded)
`ip.request_redraw()`, `ip.request_layout()`

---

## 11. Style Constants

### Screen
`SCREEN_WIDTH`, `SCREEN_HEIGHT`

### Semantic Colors (what app code should use)
`COLOR_BACKGROUND`, `COLOR_CARD_BG`, `COLOR_PANEL_BG`, `COLOR_MODAL_BG`
`COLOR_TEXT`, `COLOR_TEXT_SECONDARY`, `COLOR_TEXT_MUTED`, `COLOR_TEXT_ACCENT`
`COLOR_BUTTON_BG`, `COLOR_BORDER`, `COLOR_BORDER_SUBTLE`
`COLOR_PAL_GREEN_DARK`, `COLOR_PAL_GREEN_SECOND`
`COLOR_PAL_RED_DARK`, `COLOR_PAL_RED_PRIMARY`
`COLOR_PAL_ORANGE_FORGE`

### Fonts
`FONT_BANNER`, `FONT_TITLE`, `FONT_HEADING`, `FONT_BODY`, `FONT_DETAIL`, `FONT_MONO`

### Tokens
`TOKEN_PAD`, `TOKEN_PAD_TIGHT`, `TOKEN_GAP`, `TOKEN_GAP_TIGHT`
`TOKEN_BORDER`, `TOKEN_SCROLLBAR`, `TOKEN_CORNER_RADIUS`, `TOKEN_MULTIPLIER`

### ⚠️ Casing
`FONT_SCALE` is lowercase. Should be `FONT_SCALE` per naming conventions.

---

## 12. DECLARATION_UPDATES (Reactive Pipeline)

```python
DECLARATION_UPDATES = {
    "widget_name": {
        "property": "text",          # widget attribute to set
        "compute":  "method_name",   # method on this pane
        "triggers": ["key1", "key2"] # pipeline keys
    }
}
```

---

## 13. Naming Concerns & Inconsistencies

| # | Item | Issue |
|---|------|-------|
| 1 | `ip_draw` / `ip_draw_hud` | **You hate these.** Candidates: `ip_draw_before`/`ip_draw_after`, `ip_predraw`/`ip_postdraw`, `ip_background`/`ip_overlay` |
| 2 | `_BaseTab` vs `_BaseForm` / `_BaseWidget` | Casing inconsistency. Should be `_BaseTab` |
| 3 | `on_click_me(callback)` | Awkward. Marked "temporary" in NamingConventions. Merge into `on_click`? |
| 5 | `tool_tip_huge` | Uses `_` separator and "huge". Inconsistent with `tooltip_class` (no separator). `super_tooltip`? |
| 6 | `do_not_allocate` | Negative boolean. `hidden_from_layout`? `excluded`? |
| 7 | `FONT_SCALE` | lowercase instance style, but it's a class-level config. Should be `FONT_SCALE` |
| 8 | `hide_extra_panes(keep_count)` | Unclear name. `hide_extra_panes()`? |
| 9 | `hover_bright` | Unclear purpose from name alone |
| 10 | `locked_to_list` | What does this control? No docs |
| 11 | `tap(func)` | Undocumented in README |
| 12 | `early_load` on _BaseWidget | Seems tab-specific, lives on generic widget constructor |
| 13 | NamingConventions says `hook_` prefix | Actual code uses `ip_` prefix. Doc is stale |
| 14 | `set_radiate()` on Button | Undocumented in README |
| 15 | `layout_engine` | Internal but screaming. `layout_engine` per your own todo |
| 16 | `RunLayout()` | Internal but awful. `run()` per your own todo |
| 17 | `private_build_comp` | Unclear name. `private_build_complete`? |
| 18 | `compute_root_rectHopefullyIamDeprecated` | Still in code. Delete? |
| 19 | `scroll_glow` default `0.369` | Magic number. Consistent with brand but undocumented |
| 20 | `width_flex_actual` | Exposed but internal layout concern |

---

## 14. README vs Code Drift

| README Says | Code Actually Has |
|-------------|-------------------|
| `hook_` prefix (NamingConventions) | `ip_` prefix |
| `_BaseTab` consistent casing | `_BaseTab` (lowercase b) |
| `show_modal(msg, func, min_sec=0)` | `show_modal(msg, work_func=None, min_seconds=0)` |
| Pipeline `fire_all_derives()` | Commented out |
| `register_derive` on _BaseForm | Present but not in README API table |