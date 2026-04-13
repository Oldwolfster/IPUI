from __future__ import annotations

from typing import List, Optional, Tuple
import pygame

from ipui.engine.MeasureAndLayout import MeasureAndLayout


class MeasureAndWrap:
    """
    Wrapper around MeasureAndLayout that fixes the "text always clipped" problem
    by doing a second, bottom-up pass AFTER the first layout assigns real widths.

    Core rule:
        MeasureAndLayout remains the single source of truth for min sizes, flex,
        rect assignment, and scrollbar math.

    What we do:
        1) Run MeasureAndLayout.RunLayout() once to establish node.rect widths.
        2) Bottom-up pass: for leaf text widgets that overflow horizontally,
           greedily wrap into lines constrained by rect.width (minus frame).
           If wrapping still overflows vertically, and scrollable is enabled,
           allow MeasureAndLayout's existing scrollbar path to handle it.
        3) If anything changed (surface or scrollable state), re-run RunLayout()
           so MeasureAndLayout recomputes mins/rects/scrollbars correctly.
    """

    def __init__(self, trunk) -> None:
        self.trunk = trunk
        self.engine = MeasureAndLayout(trunk)

    def RunLayout(self) -> None:
        """
        Drop-in compatible with MeasureAndLayout.RunLayout().
        """
        # Pass 1: establish rects using trusted engine
        self.engine.RunLayout()

        # Pass 2: post-pass wrap/scroll decisions (bottom-up)
        changed = self.measure_after_wrap_and_scroll(self.trunk)

        # Pass 3: let MeasureAndLayout recompute mins/rects/scrollbars using new surfaces
        if changed:
            self.engine.RunLayout()

    def measure_after_wrap_and_scroll(self, node) -> bool:
        """
        Bottom-up post-pass that:
          - wraps leaf text widgets when they overflow horizontally (prefer wrap),
          - otherwise (or additionally) relies on existing scroll logic when scrollable.

        Returns True if any widget changed surface and/or scrollable state.
        """
        if node is None:
            return False

        changed_any = False

        # Recurse first (bottom-up)
        for child in getattr(node, "visible_children", []):
            if self.measure_after_wrap_and_scroll(child):
                changed_any = True

        # Only act on leaves (your rule: "widget with no children and text longer than width")
        if getattr(node, "visible_children", []):
            return changed_any

        if not self.is_text_like_leaf(node):
            return changed_any

        rect = getattr(node, "rect", None)
        surf = getattr(node, "my_surface", None)
        if rect is None or surf is None:
            return changed_any

        frame = int(getattr(node, "frame_size", 0))
        allocated_w = int(rect.width)
        allocated_h = int(rect.height)

        if allocated_w <= 0 or allocated_h <= 0:
            return changed_any

        # Detect horizontal overflow based on the existing built surface.
        content_w = surf.get_width() + frame
        if content_w <= allocated_w:
            # Not horizontally clipped; let existing scroll logic handle vertical overflow if any.
            return changed_any

        # Prefer wrap if enabled.
        if bool(getattr(node, "wrap", False)):
            before_size = surf.get_size()
            new_surface = self.render_wrapped_surface(node, max_width=allocated_w)

            if new_surface is not None:
                node.my_surface = new_surface
                after_size = new_surface.get_size()
                if after_size != before_size:
                    changed_any = True

            # If after wrap we're still taller than allocated height, scrollbars are a MeasureAndLayout concern.
            # We do not invent new scrollbar logic here; we only ensure scrollable flag exists when user wants it.
            if bool(getattr(node, "scrollable", False)):
                # Keep it scrollable so MeasureAndLayout can cap mins/content_size and draw scrollbars
                # using its existing codepath.
                pass

            return changed_any

        # Wrap not enabled; only scroll if allowed.
        # (Nothing to do here except ensure scrollable stays true if the widget was configured that way.)
        if bool(getattr(node, "scrollable", False)):
            # Leave the surface as-is; MeasureAndLayout will set scroll_active based on content_size.
            # But content_size for scrollables is computed from height_minimum/width_minimum during MEASURE.
            # Since we didn't rebuild surface, nothing else to change here.
            return changed_any

        return changed_any

    # ──────────────────────────────────────────────────────────────
    # Helpers (fresh logic; no reliance on old wrap helpers)
    # ──────────────────────────────────────────────────────────────

    def is_text_like_leaf(self, node) -> bool:
        """
        Conservative detection: treat as "text-like" if it has the basic fields
        used by Text.Label and friends: text, font, my_surface.
        """
        if not hasattr(node, "text"):
            return False
        if not hasattr(node, "font") or getattr(node, "font", None) is None:
            return False
        if not hasattr(node, "my_surface") or getattr(node, "my_surface", None) is None:
            return False
        return True

    def render_wrapped_surface(self, node, max_width: int) -> Optional[pygame.Surface]:
        """
        Greedy first-fit word wrap (paragraph-aware), then render lines into a surface.
        Respects node.text_align ('l'/'c'/'r') and node.color_txt.

        If node.glow is True and it has composite_glow_line(), we reuse that line renderer
        (rendering glow is *rendering*, not "old measure logic").
        """
        text = getattr(node, "text", "") or ""
        font = getattr(node, "font", None)
        if font is None:
            return None

        frame = int(getattr(node, "frame_size", 0))
        wrap_w = max(0, int(max_width) - frame)

        lines = self.wrap_greedy_first_fit(text=text, font=font, max_width=wrap_w)

        # Render each line surface
        glow = bool(getattr(node, "glow", False))
        if glow and hasattr(node, "composite_glow_line"):
            line_surfs = [node.composite_glow_line(line) for line in lines]
        else:
            color = getattr(node, "color_txt", (255, 255, 255))
            line_surfs = [font.render(line, True, color) for line in lines]

        if not line_surfs:
            return None

        w = max(s.get_width() for s in line_surfs)
        h = sum(s.get_height() for s in line_surfs)

        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        align = (getattr(node, "text_align", "l") or "l").lower()
        y = 0
        for s in line_surfs:
            if align == "c":
                x = (w - s.get_width()) // 2
            elif align == "r":
                x = w - s.get_width()
            else:
                x = 0
            surf.blit(s, (x, y))
            y += s.get_height()

        return surf

    def wrap_greedy_first_fit(self, text: str, font, max_width: int) -> List[str]:
        """
        Greedy first-fit word wrap:
            - honors existing newlines as paragraph breaks
            - splits paragraphs into words
            - packs as many words per line as fit within max_width

        If max_width <= 0: returns original paragraphs (no wrapping possible).
        """
        if max_width <= 0:
            return text.split("\n") if text else [""]

        result: List[str] = []
        paragraphs = (text or "").split("\n")

        for paragraph in paragraphs:
            words = paragraph.split()
            if not words:
                result.append("")
                continue

            current = words[0]
            for word in words[1:]:
                test = f"{current} {word}"
                if font.size(test)[0] <= max_width:
                    current = test
                else:
                    result.append(current)
                    current = word
            result.append(current)

        return result

    def layout_node(self, node, rect):
        self.engine.measure_tree(node)
        self.engine.layout_node(node, rect)