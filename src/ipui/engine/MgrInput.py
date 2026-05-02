# MgrInput.py  All event dispatch in one place.
#
# Called once per frame by GameLoop after ip.frame_begin().
# One file replaces five. No recursive widget methods.
#
# Framework walks, widgets declare.
# ─ on_click        → any widget becomes a button
# ─ focusable       → any widget receives text input
# ─ scroll_v      → any widget scrolls
# ─ toggle_selected → any widget toggles
#
# Widgets carry ZERO event methods. Behavior lives here.

import time
import pygame

from ipui.engine.Key import Key
from ipui._forms.Debugger.FormDebugger import FormDebugger


class MgrInput:
    """All event dispatch in one place."""

    # ── Focus ─────────────────────────────────────────────
    focused_widget      = None

    # ── Press ─────────────────────────────────────────────
    pressed_widget      = None

    # ── Scrollbar drag ────────────────────────────────────
    drag_widget         = None
    drag_anchor         = 0

    # ── Generic Scrollbar drag ────────────────────────────
    press_widget   = None

    # ── Text drag-select ──────────────────────────────────
    text_dragging       = False

    # ── Double-click ──────────────────────────────────────
    last_click_time     = 0
    last_click_widget   = None
    DOUBLE_CLICK_TIME   = 0.4

    # ── Form tracking (clear state on form switch) ────────
    last_form           = None

    # ══════════════════════════════════════════════════════════════
    # ENTRY POINT — called once per frame by GameLoop
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def process_frame(cls, ip, form):
        """Called once per frame after ip.frame_begin()."""
        if not form:
            return
        if form is not cls.last_form:
            cls.reset_state()
            cls.last_form = form
        cls.update_hover(form, ip.mouse_pos)
        cls.process_events(ip, form)

    @classmethod
    def reset_state(cls):
        """Clear all transient state (form switch, etc.)."""
        cls.clear_focus()
        cls.pressed_widget  = None
        cls.drag_widget     = None
        cls.text_dragging   = False

    # ══════════════════════════════════════════════════════════════
    # HOVER — one walk per frame, updates ALL widgets
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def update_hover(cls, widget, pos):
        """Recursively update is_hovered on the entire tree."""
        was              = widget.is_hovered
        widget.is_hovered = widget.rect.collidepoint(pos) if widget.rect else False
        if widget.is_hovered and not was:
            widget.hover_start_time = time.time()
        if widget.is_hovered != was and widget.on_hover:
            widget.on_hover(widget.is_hovered)
        for child in widget.visible_children:
            cls.update_hover(child, pos)

    # ══════════════════════════════════════════════════════════════
    # EVENT PROCESSING — iterates ip.events once
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def process_events(cls, ip, form):
        """Process all collected events for this frame."""
        for event in ip.events:
            consumed = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                consumed = cls.on_mouse_down(ip, form, event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                cls.on_mouse_up(ip, form, event.pos)
                consumed = True
            elif event.type == pygame.MOUSEMOTION:
                cls.on_mouse_move(ip, form, event.pos)
                consumed = False  # MOUSEMOTION always unhandled (game loops use it)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                consumed = cls.on_scroll(ip, form, event.pos, event.button)
            elif event.type == pygame.KEYDOWN:
                consumed = cls.on_keydown(ip, form, event)
            if not consumed:
                ip.unhandled.append(event)

    # ══════════════════════════════════════════════════════════════
    # MOUSE DOWN — tooltip check → scrollbar drag → click dispatch
    # ══════════════════════════════════════════════════════════════



    @classmethod
    def on_mouse_down(cls, ip, form, pos):
        if form.handle_tooltip_click(pos):          return True  # Tooltip absorbs click
        if cls.scrollbar_drag_start(form, pos):     return True  # Scrollbar drag begun
        if cls.press_drag_start(form, pos):         return True  # Generic scrolling
        target = cls.find_click_target(form, pos)                # Deepest clickable widget
        cls.manage_focus(target, pos)                            # Transfer focus if needed
        if target is None:                          return False # Nothing clicked
        if target.enabled is not True:              return True  # Disabled eats the click
        target.is_pressed  = True                                # Visual press state
        cls.pressed_widget = target                              # Track for mouse-up
        cls.fire_clicks(target)                                  # Double-click, toggle, click
        return True


    @classmethod
    def manage_focus(cls, target, pos):
        """Transfer focus to target, or clear if unfocusable."""
        if target and target.focusable:
            if target is not cls.focused_widget:
                cls.clear_focus()
                cls.focused_widget = target
                target.is_focused  = True
            cls.text_dragging = True
        else:
            cls.clear_focus()


    @classmethod
    def fire_clicks(cls, target):
        """Double-click detection, toggle, and click dispatch."""
        now            = time.time()
        double_clicked = False
        elapsed        = now - cls.last_click_time
        same_widget    = target is cls.last_click_widget

        if (now - cls.last_click_time < cls.DOUBLE_CLICK_TIME
                and target is cls.last_click_widget):
            if target.on_double_click:
                target.on_double_click()
                double_clicked = True
            cls.text_dragging = False
        cls.last_click_time   = now
        cls.last_click_widget = target
        if hasattr(target, 'toggle_selected'):
            target.toggle_selected()
        if target.on_click and not double_clicked:
            target.on_click()

    @classmethod
    def scrollbar_drag_start(cls, form, pos):
        target          = cls.find_scrollbar_hit(form, pos)
        if not target   : return False
        cls.drag_widget = target
        cls.drag_anchor = pos[1] - target.private_handle_rect.top
        return True

    @classmethod
    def press_drag_start(cls, form, pos):
        target = cls.find_press_target(form, pos)
        if not target: return False
        cls.press_widget = target
        return True
    # ══════════════════════════════════════════════════════════════
    # MOUSE UP — release press state, end drags
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def on_mouse_up(cls, ip, form, pos):
        if cls.pressed_widget:
            cls.pressed_widget.is_pressed = False
            cls.pressed_widget = None
        if cls.drag_widget:
            cls.drag_widget = None
        if cls.press_widget:                                    # NEW
            cls.press_widget.on_release()                       # NEW
            cls.press_widget = None
        if cls.text_dragging:
            cls.text_dragging = False
            if cls.focused_widget and hasattr(cls.focused_widget, 'handle_drag_end'):
                cls.focused_widget.handle_drag_end()

    # ══════════════════════════════════════════════════════════════
    # MOUSE MOVE — scrollbar drag or text drag-select
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def on_mouse_move(cls, ip, form, pos):
        # Scrollbar drag
        if cls.drag_widget:
            w      = cls.drag_widget
            usable = w.private_track_h - w.private_handle_h
            if usable > 0:
                relative = pos[1] - w.private_track_top - cls.drag_anchor
                ratio    = max(0.0, min(1.0, relative / usable))
                w.scroll_offset = int(ratio * w.private_max_scroll)
            return

        # Generic press drag                                   # NEW
        if cls.press_widget:                                    # NEW
            cls.press_widget.on_drag(pos)                       # NEW
            return

        # Text drag-select
        if cls.text_dragging and cls.focused_widget:
            if hasattr(cls.focused_widget, 'handle_drag_move'):
                cls.focused_widget.handle_drag_move(pos)

    # ══════════════════════════════════════════════════════════════
    # SCROLL — tooltip scroll → deepest scroll_v under mouse
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def on_scroll(cls, ip, form, pos, button):
        # Tooltip scroll first
        if form.handle_tooltip_scroll(pos, button):
            return True

        # Find deepest scroll_v
        target = cls.find_scroll_v(form, pos)
        if target is None:
            return False

        direction = -1 if button == 4 else 1
        target.scroll_offset += direction * 30

        # Clamp
        if target.rect:
            frame      = target.frame_size
            inner      = target.rect.inflate(-frame, -frame)
            content    = getattr(target, 'content_size', target.height_minimum)
            if content is not None and inner is not None:
                max_scroll = max(0, content - inner.height)
                target.scroll_offset = max(0, min(target.scroll_offset, max_scroll))
                at_end = (direction > 0 and target.scroll_offset >= max_scroll) or \
                         (direction < 0 and target.scroll_offset <= 0)  # NEW
                if at_end and hasattr(target.parent, 'handle_scroll_overflow'):  # NEW
                    target.parent.handle_scroll_overflow(direction)


        return True


    @classmethod
    def find_press_target(cls, widget, pos):
        """Walk tree depth-first; return the deepest widget whose on_press(pos) returns True."""
        for child in widget.interactive_children:
            result = cls.find_press_target(child, pos)
            if result is not None:
                return result
        if hasattr(widget, 'on_press') and widget.on_press(pos):
            return widget
        return None

    # ══════════════════════════════════════════════════════════════
    # KEYDOWN — framework keys → focused widget → unhandled
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def on_keydown(cls, ip, form, event):
        # F11 — diagnostics toggle
        if event.key == Key.F11:
            form.show_diagnostics = not getattr(form, 'show_diagnostics', False)
            return True

        # F12 — debugger toggle
        if event.key == Key.F12:

            from ipui.engine.IPUI import IPUI
            if isinstance(form, FormDebugger):
                IPUI.back()
            else:
                IPUI.debug_target = form
                IPUI.switch(FormDebugger, "IPUI X-Ray and Diagnostic Tools")
            return True

        # ESC — cascade: tooltip → focus → quit
        if event.key == Key.ESCAPE:
            if form.pinned_tooltip:
                form.pinned_tooltip.unpin()
                form.pinned_tooltip = None
                return True
            if cls.focused_widget:
                cls.clear_focus()
                return True
            from ipui.engine.GameLoop import GameLoop
            GameLoop.is_running = False
            return True

        # Route to focused widget
        if cls.focused_widget and hasattr(cls.focused_widget, 'handle_text_input'):
            key  = event.key
            char = event.unicode if event.unicode and event.unicode.isprintable() else None
            if cls.focused_widget.handle_text_input(key, char, ip.mod_ctrl, ip.mod_shift):
                return True

        return False

    # ══════════════════════════════════════════════════════════════
    # FOCUS — framework-managed, not widget-managed
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def clear_focus(cls):
        """Clear focus on the current widget."""
        if cls.focused_widget:
            cls.focused_widget.is_focused = False
            cls.focused_widget = None

    # ══════════════════════════════════════════════════════════════
    # TREE WALKS — find targets (all in one place, nowhere else)
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def find_click_targetOLD(cls, widget, pos):
        """Deepest visible widget under pos that wants a click."""
        pos = cls.translate_pos_into(widget, pos)
        for child in widget.interactive_children:
            result = cls.find_click_target(child, pos)
            if result is not None:
                return result
        if widget.rect and widget.rect.collidepoint(pos):
            if (widget.on_click
                    or widget.focusable
                    or widget.on_double_click
                    or hasattr(widget, 'toggle_selected')):
                return widget
        return None

    @classmethod
    def find_scroll_vOLD(cls, widget, pos):
        """Deepest scroll_v widget under pos."""
        for child in widget.interactive_children:
            result = cls.find_scroll_v(child, pos)
            if result is not None:
                return result
        if widget.scroll_active and widget.rect and widget.rect.collidepoint(pos):
            return widget
        return None

    @classmethod
    def find_scrollbar_hitOLD(cls, widget, pos):
        """Widget whose scrollbar handle was clicked."""
        for child in widget.interactive_children:
            result = cls.find_scrollbar_hit(child, pos)
            if result is not None:
                return result
        if widget.private_handle_rect and widget.private_handle_rect.collidepoint(pos):
            return widget
        return None

    @classmethod
    def find_click_target(cls, widget, mouse_coord):
        """Deepest visible widget under mouse_coord that wants a click."""
        child_coord = widget.translate_mouse_coord_for_horizontal_scroll(mouse_coord)
        for child in widget.interactive_children:
            result = cls.find_click_target(child, child_coord)
            if result is not None:
                return result
        if widget.rect and widget.rect.collidepoint(mouse_coord):
            if (widget.on_click
                    or widget.focusable
                    or widget.on_double_click
                    or hasattr(widget, 'toggle_selected')):
                return widget
        return None

    @classmethod
    def find_scroll_v(cls, widget, mouse_coord):
        """Deepest scroll_v widget under mouse_coord."""
        child_coord = widget.translate_mouse_coord_for_horizontal_scroll(mouse_coord)
        for child in widget.interactive_children:
            result = cls.find_scroll_v(child, child_coord)
            if result is not None:
                return result
        if widget.scroll_active and widget.rect and widget.rect.collidepoint(mouse_coord):
            return widget
        return None

    @classmethod
    def find_scrollbar_hit(cls, widget, mouse_coord):
        """Widget whose scrollbar handle was clicked."""
        child_coord = widget.translate_mouse_coord_for_horizontal_scroll(mouse_coord)
        for child in widget.interactive_children:
            result = cls.find_scrollbar_hit(child, child_coord)
            if result is not None:
                return result
        if widget.private_handle_rect and widget.private_handle_rect.collidepoint(mouse_coord):
            return widget
        return None

    @classmethod
    def find_press_target(cls, widget, mouse_coord):
        """Walk tree depth-first; return the deepest widget whose on_press(mouse_coord) returns True."""
        child_coord = widget.translate_mouse_coord_for_horizontal_scroll(mouse_coord)
        for child in widget.interactive_children:
            result = cls.find_press_target(child, child_coord)
            if result is not None:
                return result
        if hasattr(widget, 'on_press') and widget.on_press(mouse_coord):
            return widget
        return None