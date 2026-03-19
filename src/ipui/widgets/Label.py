from ipui.Style import Style
from ipui.engine._BaseWidget import _BaseWidget
from ipui.utils.EZ import EZ


class Label(_BaseWidget):
    """
    desc:        Base text renderer. Handles multiline, alignment, and the molten glow effect.
    when_to_use: When you need raw text control. Usually prefer Banner/Title/Heading/Body/Detail.
    best_for:    Custom font or alignment scenarios.
    example:     Label(parent, "Hello", font=my_font, text_align='c', glow=True)
    api:         set_text(text)
    """
    def build(self):
        EZ.warn_scroll  ( self)
        self.font       = self.font or Style.FONT_BODY
        self.color_txt  = Style.COLOR_MOLTEN if self.glow else Style.COLOR_TEXT
        self.pad        = 0
        self.gap        = 0
        self.border     = 0
        self.wrap       = True #Set default for label to be wrap=true
        if self.glow:   self.my_surface = self.composite_glow()
        else:           self.my_surface = self.render_multiline(self.text)


    def compute_intrinsic(self) -> None:
        """For wrapped text, intrinsic width is the longest word."""
        if not self.wrap or not self.text or self.glow:
            super().compute_intrinsic()
            return
        frame                 = self.frame_size
        self.width_intrinsic  = max(
            (self.font.size(word)[0] for word in self.text.split()),
            default=0
        ) + frame
        self.height_intrinsic = self.font.get_height() + frame

    def measure_constrained(self, max_width: int) -> tuple[int, int]:
        """If wrap enabled, rebuild surface at constrained width and re-measure."""
        if not self.wrap:       return self.measure()
        if self.glow:           self.my_surface = self.composite_glow_wrapped(max_width)
        else:                   self.my_surface = self.render_multiline_wrapped(self.text or "", max_width)
        return self.measure_self_no_children()


    def composite_glow_line(self, line):
        import pygame
        hot_surf   = self.font.render(line, True, Style.COLOR_PAL_ORANGE_BRIGHT)
        core_surf  = self.font.render(line, True, Style.COLOR_MOLTEN)
        bloom_surf = self.font.render(line, True, Style.COLOR_PAL_ORANGE_DEEP)

        w    = hot_surf.get_width() + 4
        h    = hot_surf.get_height() + 4
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        surf.blit(bloom_surf, (2, 2))
        surf.blit(core_surf,  (1, 1))
        surf.blit(hot_surf,   (0, 0))
        return surf

    def composite_glow(self):
        import pygame
        lines  = self.text.split("\n")
        surfs  = [self.composite_glow_line(l) for l in lines]
        w      = max(s.get_width()  for s in surfs)
        h      = sum(s.get_height() for s in surfs)
        surf   = pygame.Surface((w, h), pygame.SRCALPHA)
        y      = 0
        for s in surfs:
            surf.blit(s, (0, y))
            y += s.get_height()
        return surf

    def composite_glow_wrapped(self, max_width):
        import pygame
        lines = self.wrap_lines(self.text or "", max_width)
        surfs = [self.composite_glow_line(l) for l in lines]
        w     = max(s.get_width()  for s in surfs)
        h     = sum(s.get_height() for s in surfs)
        surf  = pygame.Surface((w, h), pygame.SRCALPHA)
        y     = 0
        for s in surfs:
            surf.blit(s, (0, y))
            y += s.get_height()
        return surf

##################################################
# Readability Classes - Text Hierarchy
##################################################
class Banner(Label):
    """
    desc:        The biggest voice in the room. One per screen, max.
    when_to_use: App title, hero text.
    best_for:    The thing you see from across the room.
    example:     Banner(parent, "NeuroForge", glow=True)
    api:         set_text(text)
    """
    def build(self):
        self.font = Style.FONT_BANNER
        super().build()

class Title(Label):
    """
    desc:        Section header. Starts a new topic.
    when_to_use: Top of every pane or major section.
    best_for:    Pane headers, card titles, dialog headings.
    example:     Title(parent, "Match Setup", glow=True)
    api:         set_text(text)
    """
    def build(self):
        self.font = Style.FONT_TITLE
        super().build()

class Heading(Label):
    """
    desc:        Subsection label. Groups related content below it.
    when_to_use: Logical groupings within a pane.
    best_for:    Field group labels, list headers, settings categories.
    example:     Heading(parent, "Hyperparams:", glow=True)
    api:         set_text(text)
    """
    def build(self):
        self.font = Style.FONT_HEADING
        super().build()

class Body(Label):
    """
    desc:        The workhorse. Most text on screen is this.
    when_to_use: Any readable content that isn't a label or title.
    best_for:    Descriptions, instructions, data display, multiline content.
    example:     Body(parent, "Select a project or create a new one.")
    api:         set_text(text)
    """
    def build(self):
        self.font = Style.FONT_BODY
        super().build()

class Detail(Label):
    """
    desc:        Fine print. Small but still readable.
    when_to_use: Secondary info, timestamps, counts, footnotes.
    best_for:    Status bars, metadata, supplementary labels.
    example:     Detail(parent, "Last run: 2 min ago")
    api:         set_text(text)
    """
    def build(self):
        self.font = Style.FONT_DETAIL
        super().build()