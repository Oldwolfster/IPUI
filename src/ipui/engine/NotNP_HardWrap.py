from __future__ import annotations

from typing import List, Optional, Tuple
import pygame


class MeasureAndWrap:
    """
    Pass 2 of 4: text-wrap pass.

    Bottom-up walk over the tree. For leaf text widgets whose rendered surface
    overflows their allocated rect width, re-render the surface wrapped to that
    width. Returns True if any surface changed size, signaling the orchestrator
    to re-run MeasureAndLayout so mins/rects/scrollbars reflect the new surfaces.

    Scope:
        - Only touches my_surface on text-like leaves with wrap=True.
        - Does NOT modify rects, flex math, or scrollbar state directly.
        - MeasureAndLayout remains the single source of truth for mins, flex,
          rect assignment, and scrollbar math.

    Orchestration (calling RunLayout before/after this pass) lives in
    _BaseForm.sane_layout, not here.
    """
    def __init__(self, trunk) -> None:
        self.trunk = trunk
        #self.engine = MeasureAndLayout(trunk)

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
            print("WTF HOW?")
            self.engine.RunLayout()


    def RunLayout(self) -> bool:
        """
        Wrap-only pass. Walks tree bottom-up, re-renders text leaves whose
        surfaces overflow their allocated rect width. Returns True if any
        surface changed size, signaling the caller to re-run MeasureAndLayout.
        """
        return self.measure_after_wrap_and_scroll(self.trunk)

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
                   #print(f"[WRAP] {type(node).__name__} '{getattr(node, 'text', '')[:40]}' "
                   #      f"surface {before_size} → {after_size}, allocated_w={allocated_w}")
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

        Side-effect: writes node.display_lines and node.display_line_starts so widgets
        like TextArea can map cursor positions back to flat-text offsets.

        If node.glow is True and it has composite_glow_line(), we reuse that line renderer
        (rendering glow is *rendering*, not "old measure logic").
        """
        text = getattr(node, "text", "") or ""
        font = getattr(node, "font", None)
        if font is None:
            return None

        frame  = int(getattr(node, "frame_size", 0))
        wrap_w = max(0, int(max_width) - frame)

        lines, line_starts = self.wrap_greedy_first_fit(text=text, font=font, max_width=wrap_w)

        # Hand the authoritative wrapped layout back to the widget for cursor/click math.
        node.display_lines       = lines if lines else [""]
        node.display_line_starts = line_starts if line_starts else [0]

        # Render each line surface
        glow = bool(getattr(node, "glow", False))
        if glow and hasattr(node, "composite_glow_line"):
            line_surfs = [node.composite_glow_line(line) for line in lines]
        else:
            color      = getattr(node, "color_txt", (255, 255, 255))
            line_surfs = [font.render(line, True, color) for line in lines]

        if not line_surfs:
            return None

        w = max(s.get_width() for s in line_surfs)
        h = sum(s.get_height() for s in line_surfs)

        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        align = (getattr(node, "text_align", "l") or "l").lower()
        y = 0
        for s in line_surfs:
            if   align == "c": x = (w - s.get_width()) // 2
            elif align == "r": x =  w - s.get_width()
            else             : x =  0
            surf.blit(s, (x, y))
            y += s.get_height()

        return surf

    def wrap_greedy_first_fit(self, text: str, font, max_width: int) -> Tuple[List[str], List[int]]:
        """
        Greedy first-fit word wrap. Returns (lines, line_starts) where
        line_starts[i] is the flat-text offset in `text` where lines[i] begins.

        - honors existing newlines as paragraph breaks
        - splits paragraphs into words
        - packs as many words per line as fit within max_width

        If max_width <= 0: returns original paragraphs (no wrapping possible)
        with offsets matching the paragraph boundaries.
        """
        text = text or ""

        if max_width <= 0:
            paragraphs = text.split("\n") if text else [""]
            starts     = []
            offset     = 0
            for p in paragraphs:
                starts.append(offset)
                offset += len(p) + 1   # +1 for the \n that split consumed
            return paragraphs, starts

        result_lines:  List[str] = []
        result_starts: List[int] = []
        cursor = 0                       # flat offset into `text`
        paragraphs = text.split("\n")

        for p_idx, paragraph in enumerate(paragraphs):
            if not paragraph:
                result_lines.append("")
                result_starts.append(cursor)
                cursor += 1              # the \n that ended this empty paragraph (skipped on last)
                if p_idx == len(paragraphs) - 1:
                    cursor -= 1
                continue

            line_start = cursor          # this wrapped line starts at the paragraph's first char
            current    = ""              # accumulated visible chars
            consumed   = 0               # chars consumed from paragraph (including spaces between words)

            i = 0
            while i < len(paragraph):
                # skip leading spaces only when starting a fresh wrapped line
                if not current:
                    while i < len(paragraph) and paragraph[i] == ' ':
                        i        += 1
                        consumed += 1
                    line_start = cursor + consumed - (1 if consumed and paragraph[consumed-1] == ' ' else 0)
                    line_start = cursor + consumed   # leading spaces dropped; line begins at first visible char
                    if i >= len(paragraph):
                        break

                # grab next word
                w_start = i
                while i < len(paragraph) and paragraph[i] != ' ':
                    i += 1
                word = paragraph[w_start:i]

                test = word if not current else f"{current} {word}"
                if font.size(test)[0] <= max_width:
                    current   = test
                    consumed  = i
                else:
                    result_lines.append(current)
                    result_starts.append(line_start)
                    current    = word
                    line_start = cursor + w_start
                    consumed   = i

                # consume one trailing space if present (it's the separator before the next word)
                if i < len(paragraph) and paragraph[i] == ' ':
                    i        += 1
                    consumed  = i

            if current or not result_lines or result_starts[-1] != line_start:
                result_lines.append(current)
                result_starts.append(line_start)

            cursor += len(paragraph) + 1   # +1 for the \n that separated paragraphs

        # last paragraph had no trailing \n; back off the extra increment
        if paragraphs:
            cursor -= 1

        return result_lines, result_starts

    def layout_node(self, node, rect):
        self.engine.measure_tree(node)
        self.engine.layout_node(node, rect)