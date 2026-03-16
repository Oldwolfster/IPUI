# Breakout.py  New: Arcade-style demo using None panes and set_pane

import pygame
from ipui.Style import Style
from ipui.engine._BasePane import _basePane
from ipui.widgets.Row import Row
from ipui.widgets.Label import Title, Body, Heading, Banner
from ipui.widgets.Card import Card
from ipui.widgets.Button import Button


class Breakout(_basePane):
    """Arcade demo: press Q or click to start, controls appear on canvas."""

    IP_LIFECYCLE = "persist"

    def initialize(self):
        self.playing = False

    # ══════════════════════════════════════════════════════════════
    # PANE BUILDERS
    # ══════════════════════════════════════════════════════════════

    def greet(self, parent):
        Banner(parent, "BREAKOUT", glow=True,text_align='c')
        Body(parent, "This demo shows how a None pane in TAB_LAYOUT "
                     "creates a transparent canvas for pygame drawing.")

        card = Card(parent)
        Heading(card, "Please insert a quarter", glow=True)
        Body(card, "OR press Q")
        Button(card, "Insert Quarter",
               color_bg=Style.COLOR_PAL_GREEN_DARK,
               on_click=self.start_game)

    def game_controls_option_1(self, parent):
        """Loaded into the None slot via set_pane when game starts."""
        row = Row(parent)
        Button(row, "Pause",
               color_bg=Style.COLOR_TAB_BG,
               on_click=self.pause_game)
        Button(row, "Quit",
               color_bg=Style.COLOR_TAB_BG,
               on_click=self.end_game)


    def game_controls(self, parent):
        """Loaded into the None slot via set_pane when game starts."""
        Title(parent, "GAME ON!", glow=True, text_align='c')
        Body(parent, "That title is centered. No math. No blit. One line.", text_align='c')

        card = Card(parent)
        Heading(card, "Think You Can Build This?", glow=True)
        Body(card, "A real Breakout game. Right here. Right now.\n"
                   "5 minutes if you're fast.\n"
                   "20 minutes if you just learned what a keyboard is.\n"
                   "Either way, you'll be smashing bricks before lunch.")

        card = Card(parent)
        Heading(card, "The Game")
        Body(card, "1. A paddle at the bottom that follows your mouse\n"
                   "2. A ball that bounces off everything it touches\n"
                   "3. Rows of colorful bricks waiting to be smashed\n"
                   "4. A score that goes up every time a brick explodes\n"
                   "5. Miss the ball? Lose a life. Three strikes you're out.")

        card = Card(parent)
        Heading(card, "What You Get For Free")
        Body(card, "6. A big empty space to draw your game in\n"
                   "7. A thinking loop for physics and collisions\n"
                   "8. A drawing loop for painting your world\n"
                   "9. A scoreboard already waiting on the right\n"
                   "10. Pause and Quit already wired up below")

        row = Row(parent)
        Button(row, "Pause",
               color_bg=Style.COLOR_TAB_BG,
               on_click=self.pause_game)
        Button(row, "Quit",
               color_bg=Style.COLOR_TAB_BG,
               on_click=self.end_game)

    def scoreboard(self, parent):
        Title(parent, "Scoreboard", glow=True)
        Body(parent, "Score: 0", name="lbl_score")

    # ══════════════════════════════════════════════════════════════
    # GAME CONTROLS
    # ══════════════════════════════════════════════════════════════

    def start_game(self):
        self.playing = True
        self.form.set_pane(1, self.game_controls)

    def pause_game(self):
        self.playing = not self.playing

    def end_game(self):
        self.playing = False

    # ══════════════════════════════════════════════════════════════
    # LIFECYCLE HOOKS
    # ══════════════════════════════════════════════════════════════

    def ip_think(self, ip):
        if ip.key_pressed("q"):
            self.start_game()

    def ip_renderpre(self, ip):
        self.KeepYourHooksLookingSharp_NoLogicJustCalls (ip)    # MAD BONUS POINTS
        self.anothermethod                              (ip)    # for vertically aligning
        self.BUT_NO_IF_OR_LOOPS                         (ip)    # identical code!!!
        self.just_THE_top                               (ip)    # No drift :)

    def anothermethod       (self, ip): pass                    # No drift P)
    def BUT_NO_IF_OR_LOOPS  (self, ip): pass                    # No drift _)
    def just_THE_top        (self, ip): pass                    # No drift (::)

    def KeepYourHooksLookingSharp_NoLogicJustCalls(self,ip):
        """code is like a pyramid.
            at the top.  just a list of method calls.  no loops no ifs.
            just a list.  Not like this... This is the base of the pyramid.
        """

        if not self.playing:
            return
        arena = self.form.tab_strip.panes[1]
        if not arena or not arena.rect:
            return
        r = arena.rect
        pygame.draw.rect(ip.surface, (20, 20, 40), r)
        font = Style.FONT_TITLE
        surf = font.render("GAME ON!", True, Style.COLOR_PAL_ORANGE_BRIGHT)
        # WTF can blit of course.  should they want to?  Hell no
        ip.surface.blit(surf, (r.centerx - surf.get_width() // 2,           #THIS IS WHAT ARE SUPPOSED TO BE DOING FOR THEM
                               r.centery - surf.get_height() // 2))

    def ip_renderpost(self, ip):
        pass