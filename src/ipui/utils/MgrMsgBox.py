# MgrMsgBox.py  NEW FILE  Manager for modal message boxes with buttons (msgbox czar's first decree)
# Architecture:
#   - Singleton-style manager (class methods, single active msgbox at a time).
#   - Form calls MgrMsgBox.show(form, text, flags, title, on_result).
#   - GameLoop checks MgrMsgBox.is_active() each frame:
#       * If active: consume events here, skip normal widget dispatch.
#       * Always: call MgrMsgBox.draw(surface) after main render.
#   - User input -> dismiss(result) -> fires on_result callback -> form continues.
#
# Constants (also re-exported from ipui __init__):
#   MSG_BTNS_OK / MSG_BTNS_OK_CANCEL / MSG_BTNS_YES_NO
#   MSG_ICON_INFO / MSG_ICON_QUESTION / MSG_ICON_WARNING / MSG_ICON_CRITICAL
#   MSG_DEFAULT_1 / MSG_DEFAULT_2 / MSG_DEFAULT_3
#   MSG_RESULT_OK / MSG_RESULT_CANCEL / MSG_RESULT_YES / MSG_RESULT_NO

import pygame
from ipui.Style import Style
from ipui.engine.MgrFont import MgrFont


# ══════════════════════════════════════════════════════════════
# CONSTANTS — bitmask flags + result values
# ══════════════════════════════════════════════════════════════

# Button sets (bits 0-3)
MSG_BTNS_OK             = 0
MSG_BTNS_OK_CANCEL      = 1
MSG_BTNS_YES_NO         = 2

# Icons (bits 4-7)
MSG_ICON_INFO           = 16
MSG_ICON_QUESTION       = 32
MSG_ICON_WARNING        = 48
MSG_ICON_CRITICAL       = 64

# Default button focus (bits 8-11)
MSG_DEFAULT_1           = 0
MSG_DEFAULT_2           = 256
MSG_DEFAULT_3           = 512

# Result values — distinct prefix MSG_RESULT_* to avoid VB's collision
MSG_RESULT_OK           = 1
MSG_RESULT_CANCEL       = 2
MSG_RESULT_YES          = 6
MSG_RESULT_NO           = 7


# ══════════════════════════════════════════════════════════════
# BUTTON SET LAYOUTS — maps button-set flag to (labels, results)
# ══════════════════════════════════════════════════════════════

_BUTTON_SETS = {
    MSG_BTNS_OK         : [("OK",     MSG_RESULT_OK)],
    MSG_BTNS_OK_CANCEL  : [("OK",     MSG_RESULT_OK),
                           ("Cancel", MSG_RESULT_CANCEL)],
    MSG_BTNS_YES_NO     : [("Yes",    MSG_RESULT_YES),
                           ("No",     MSG_RESULT_NO)],
}

# Esc dismisses to the "safer/cancel" result for each button set.
_ESC_RESULT = {
    MSG_BTNS_OK         : MSG_RESULT_OK,
    MSG_BTNS_OK_CANCEL  : MSG_RESULT_CANCEL,
    MSG_BTNS_YES_NO     : MSG_RESULT_NO,
}


# ══════════════════════════════════════════════════════════════
# ICON DEFINITIONS — (stripe color, badge color, glyph)
# ══════════════════════════════════════════════════════════════

_ICON_INFO = {
    "stripe":   (60,  130, 220),    # blue
    "badge" :   (80,  160, 240),
    "glyph" :   "i",
}
_ICON_QUESTION = {
    "stripe":   (120, 120, 130),    # neutral gray
    "badge" :   (150, 150, 160),
    "glyph" :   "?",
}
_ICON_WARNING = {
    "stripe":   (230, 180, 40),     # amber
    "badge" :   (250, 200, 60),
    "glyph" :   "!",
}
_ICON_CRITICAL = {
    "stripe":   (220, 60,  60),     # red
    "badge" :   (240, 90,  90),
    "glyph" :   "X",
}
_ICONS = {
    MSG_ICON_INFO       : _ICON_INFO,
    MSG_ICON_QUESTION   : _ICON_QUESTION,
    MSG_ICON_WARNING    : _ICON_WARNING,
    MSG_ICON_CRITICAL   : _ICON_CRITICAL,
}


# ══════════════════════════════════════════════════════════════
# MGRMSGBOX — class-level state, no instances
# ══════════════════════════════════════════════════════════════

class MgrMsgBox:
    """Manager for modal message boxes. Single active msgbox at a time.
       Czar of the msgbox domain. First decree: bitmask flags + async callback."""

    # Active msgbox state (None when no msgbox is up)
    private_active      = None      # dict with: text, btns, icon, default_idx, title, callback, button_rects, focused_idx, form
    private_hovered_idx = -1

    # ───────────────────────────── PUBLIC API ─────────────────────────────

    @classmethod
    def is_active(cls) -> bool:
        """Returns True while a msgbox is up. GameLoop uses this to gate input."""
        return cls.private_active is not None

    @classmethod
    def show(cls, form, text, flags=0, title="", on_result=None):
        """Display a modal msgbox. Decodes flags, stores state. Returns immediately;
           callback fires when user dismisses the box."""
        btns_flag, icon_flag, default_flag = cls.decode_flags(flags)
        cls.private_active = {
            "form"          : form,
            "text"          : str(text),
            "title"         : str(title),
            "btns_flag"     : btns_flag,
            "icon_flag"     : icon_flag,
            "buttons"       : _BUTTON_SETS.get(btns_flag, _BUTTON_SETS[MSG_BTNS_OK]),
            "default_idx"   : cls.clamp_default(btns_flag, default_flag),
            "callback"      : on_result,
            "button_rects"  : [],   # populated each draw
            "focused_idx"   : cls.clamp_default(btns_flag, default_flag),
        }
        cls.private_hovered_idx = -1

    # ───────────────────────────── FLAG DECODING ─────────────────────────────

    @staticmethod
    def decode_flags(flags):
        """Extract (button_set, icon, default_button) from bitmask. Each lives in its own nibble."""
        btns    = flags & 0x0F
        icon    = flags & 0xF0
        default = flags & 0xF00
        return btns, icon, default

    @staticmethod
    def clamp_default(btns_flag, default_flag):
        """Convert MSG_DEFAULT_N flag to a 0-indexed button position, clamped to button set size."""
        max_idx = len(_BUTTON_SETS.get(btns_flag, [("OK", MSG_RESULT_OK)])) - 1
        idx     = default_flag >> 8         # 0, 1, or 2
        return max(0, min(idx, max_idx))

    # ───────────────────────────── EVENT HANDLING ─────────────────────────────

    @classmethod
    def handle_events(cls, events):
        """Consume events while msgbox is up. Called by GameLoop instead of normal dispatch."""
        if cls.private_active is None:                          return
        for event in events:
            if   event.type == pygame.MOUSEMOTION:              cls.handle_mouse_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:          cls.handle_mouse_click(event.pos, event.button)
            elif event.type == pygame.KEYDOWN:                  cls.handle_key(event.key)

    @classmethod
    def handle_mouse_move(cls, pos):
        """Update hovered button index for visual feedback."""
        cls.private_hovered_idx = cls.button_at(pos)

    @classmethod
    def handle_mouse_click(cls, pos, button):
        """Dispatch click to button under cursor (left button only)."""
        if button != 1:                                         return
        idx = cls.button_at(pos)
        if idx < 0:                                             return
        _, result = cls.private_active["buttons"][idx]
        cls.dismiss(result)

    @classmethod
    def handle_key(cls, key):
        """Enter activates focused button. Esc returns the cancel-equivalent.
           Left/Right arrows move focus between buttons. Tab cycles focus."""
        act = cls.private_active
        if   key == pygame.K_RETURN:                            cls.activate_focused()
        elif key == pygame.K_ESCAPE:                            cls.dismiss(_ESC_RESULT.get(act["btns_flag"], MSG_RESULT_CANCEL))
        elif key == pygame.K_LEFT:                              cls.move_focus(-1)
        elif key in (pygame.K_RIGHT, pygame.K_TAB):             cls.move_focus( 1)

    @classmethod
    def activate_focused(cls):
        """Activate whichever button currently has focus."""
        act       = cls.private_active
        _, result = act["buttons"][act["focused_idx"]]
        cls.dismiss(result)

    @classmethod
    def move_focus(cls, delta):
        """Shift focus by delta, wrapping around."""
        act     = cls.private_active
        count   = len(act["buttons"])
        act["focused_idx"] = (act["focused_idx"] + delta) % count

    @classmethod
    def button_at(cls, pos):
        """Return index of button rect under pos, or -1 if none."""
        if cls.private_active is None: return -1  # NEW
        for i, rect in enumerate(cls.private_active["button_rects"]):
            if rect.collidepoint(pos):                          return i
        return -1

    # ───────────────────────────── DISMISSAL ─────────────────────────────

    @classmethod
    def dismiss(cls, result):
        """Close msgbox and fire callback (if any) with the result constant."""
        active             = cls.private_active
        cls.private_active = None
        cls.private_hovered_idx = -1
        if active and active["callback"]:
            active["callback"](result)

    # ───────────────────────────── RENDERING ─────────────────────────────

    @classmethod
    def draw(cls, surface):
        """Draw the active msgbox on top of everything. Called by GameLoop after main render."""
        if cls.private_active is None:                          return
        cls.draw_dim_background(surface)
        box_rect = cls.compute_box_rect(surface)
        cls.draw_box_chrome(surface, box_rect)
        cls.draw_icon_stripe(surface, box_rect)
        cls.draw_title(surface, box_rect)
        cls.draw_message(surface, box_rect)
        cls.draw_buttons(surface, box_rect)

    @classmethod
    def draw_dim_background(cls, surface):
        """Semi-transparent black overlay to dim everything behind the box."""
        sw, sh  = surface.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

    @classmethod
    def compute_box_rect(cls, surface):
        """Calculate the centered box rect based on text content."""
        act      = cls.private_active
        sw, sh   = surface.get_size()
        pad      = Style.TOKEN_PAD * 3
        font     = Style.FONT_BODY
        lines    = act["text"].split("\n")
        line_h   = font.get_linesize()
        text_w   = max((font.size(l)[0] for l in lines), default=0)
        text_h   = line_h * len(lines)
        # Box must fit: title row + text + button row, plus pads.
        box_w    = max(text_w + pad * 2 + 80, 380)               # 80 = icon column reserve
        title_h  = Style.FONT_HEADING.get_linesize() if act["title"] else 0
        btn_h    = Style.FONT_BODY.get_linesize() + pad
        box_h    = title_h + text_h + btn_h + pad * 4
        box_x    = (sw - box_w) // 2
        box_y    = (sh - box_h) // 2
        return pygame.Rect(box_x, box_y, box_w, box_h)

    @classmethod
    def draw_box_chrome(cls, surface, box_rect):
        """Card background + border."""
        pygame.draw.rect(surface, Style.COLOR_CARD_BG,     box_rect)
        pygame.draw.rect(surface, Style.COLOR_BEVEL_LIGHT, box_rect, 2)

    @classmethod
    def draw_icon_stripe(cls, surface, box_rect):
        """Colored top stripe + icon badge on the left. Subtle visual signature per icon type."""
        act  = cls.private_active
        icon = _ICONS.get(act["icon_flag"])
        if not icon:                                            return
        # Top stripe across the whole box width.
        stripe_h = 6
        pygame.draw.rect(surface, icon["stripe"],
                         pygame.Rect(box_rect.x, box_rect.y, box_rect.width, stripe_h))
        # Icon badge — circle with glyph, in the upper-left of the content area.
        pad        = Style.TOKEN_PAD * 2
        badge_size = 36
        badge_x    = box_rect.x + pad
        badge_y    = box_rect.y + stripe_h + pad
        center     = (badge_x + badge_size // 2, badge_y + badge_size // 2)
        pygame.draw.circle(surface, icon["badge"], center, badge_size // 2)
        glyph_surf = Style.FONT_HEADING.render(icon["glyph"], True, (255, 255, 255))
        glyph_rect = glyph_surf.get_rect(center=center)
        surface.blit(glyph_surf, glyph_rect)

    @classmethod
    def draw_title(cls, surface, box_rect):
        """Title text at top of box, offset right if icon is present."""
        act = cls.private_active
        if not act["title"]:                                    return
        pad         = Style.TOKEN_PAD * 2
        stripe_h    = 6 if act["icon_flag"] else 0
        x_offset    = (36 + pad * 2) if act["icon_flag"] else pad
        title_surf  = Style.FONT_HEADING.render(act["title"], True, Style.COLOR_TEXT)
        surface.blit(title_surf, (box_rect.x + x_offset, box_rect.y + stripe_h + pad))

    @classmethod
    def draw_message(cls, surface, box_rect):
        """Multi-line message body, offset right if icon is present."""
        act       = cls.private_active
        pad       = Style.TOKEN_PAD * 2
        stripe_h  = 6 if act["icon_flag"] else 0
        title_h   = Style.FONT_HEADING.get_linesize() if act["title"] else 0
        x_offset  = (36 + pad * 2) if act["icon_flag"] else pad
        y_start   = box_rect.y + stripe_h + pad + title_h + (pad if act["title"] else 0)
        font      = Style.FONT_BODY
        line_h    = font.get_linesize()
        for i, line in enumerate(act["text"].split("\n")):
            surf = font.render(line, True, Style.COLOR_TEXT)
            surface.blit(surf, (box_rect.x + x_offset, y_start + i * line_h))

    @classmethod
    def draw_buttons(cls, surface, box_rect):
        """Render button row across the bottom of the box, populates button_rects for hit-testing."""
        act       = cls.private_active
        pad       = Style.TOKEN_PAD * 2
        font      = Style.FONT_BODY
        btn_pad_x = pad
        btn_pad_y = pad // 2
        btn_h     = font.get_linesize() + btn_pad_y * 2
        gap       = pad
        # Measure each button label.
        sizes     = [font.size(label)[0] + btn_pad_x * 2 for label, _ in act["buttons"]]
        total_w   = sum(sizes) + gap * (len(sizes) - 1)
        # Right-align button row inside the box.
        x         = box_rect.right - pad - total_w
        y         = box_rect.bottom - pad - btn_h
        rects     = []
        for i, (label, _) in enumerate(act["buttons"]):
            rect = pygame.Rect(x, y, sizes[i], btn_h)
            cls.draw_one_button(surface, rect, label, i)
            rects.append(rect)
            x += sizes[i] + gap
        act["button_rects"] = rects

    @classmethod
    def draw_one_button(cls, surface, rect, label, idx):
        """Draw a single button with hover + focus visual states."""
        act       = cls.private_active
        is_focus  = (idx == act["focused_idx"])
        is_hover  = (idx == cls.private_hovered_idx)
        # Background: focus > hover > normal.
        if   is_focus:   bg = Style.COLOR_BUTTON_CTA
        elif is_hover:   bg = Style.COLOR_BUTTON_SECONDARY
        else:            bg = Style.COLOR_TAB_BG
        pygame.draw.rect(surface, bg, rect)
        pygame.draw.rect(surface, Style.COLOR_BEVEL_LIGHT, rect, 1)
        # Label centered.
        label_surf = Style.FONT_BODY.render(label, True, Style.COLOR_TEXT)
        label_rect = label_surf.get_rect(center=rect.center)
        surface.blit(label_surf, label_rect)