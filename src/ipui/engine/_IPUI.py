# _IPUI.py  Update: ip service portal replaces ctx
import pygame
from ipui.Style import Style
from ipui.engine.Log import Logger
from ipui.engine.IPUI import IPUI
from ipui.engine.MgrFont import MgrFont
from ipui.engine.MgrColor import MgrColor
from ipui.engine.IP import IP
#import gc
import time

class _IPUI:
    screen      = None
    is_running  = True
    def __init__(self, form_class, title=None):

        Logger()
        pygame  .init()
        pygame.key.set_repeat(350, 35)  # delay ms, interval ms (enables KEYDOWN repeats)
        print("pygame loop constructor")

        self    .init_pygame    ( title)
        IPUI    .screen     = _IPUI.screen
        IPUI    .switch     ( form_class, title)
        self    .clock      = pygame.time.Clock()
        self    .ip         = IP()
        self    .frame_count= 0
        #gc      .disable()
        self    .run_loop()
        pygame  .quit()

    def run_loop(self):
        while _IPUI.is_running: self.pygame_loop()

    # ══════════════════════════════════════════════════════════════
    # THE LOOP — one frame
    # ══════════════════════════════════════════════════════════════

    def pygame_loop_no_time(self):
        dt   = self.clock.tick(60) / 1000.0
        form = IPUI.active()
        self.frame_count += 1

        # ── Snapshot all input state ──────────────────────────
        ip = self.ip
        ip.frame_begin(dt, int(self.clock.get_fps()), self.frame_count, _IPUI.screen, form)

        # ── Events ────────────────────────────────────────────
        for event in pygame.event.get():
            if      event.type == pygame.QUIT:      _IPUI.is_running = False
            elif(   event.type == pygame.KEYDOWN
            and     event.key  == pygame.K_ESCAPE): self.handle_escape()
            else:
                ip.events.append(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                    ip.mouse_wheel += (-1 if event.button == 4 else 1)
                consumed = IPUI.process_events(event)
                if not consumed:
                    ip.unhandled.append(event)

        # ── THINK ─────────────────────────────────────────────
        if form: form.ip_think(ip)

        # ── Layout ────────────────────────────────────────────
        IPUI.update()

        # ── RENDER PRE ────────────────────────────────────────
        _IPUI.screen.fill(Style.COLOR_BACKGROUND)
        if form: form.ip_renderpre(ip)

        # ── UI Draw ───────────────────────────────────────────
        IPUI.render(_IPUI.screen)

        # ── RENDER POST ───────────────────────────────────────
        if form: form.ip_renderpost(ip)

        # ── Flip ──────────────────────────────────────────────
        pygame.display.update()



    def pygame_loop(self):
        t_start = time.perf_counter()                # NEW
        gap = t_start - getattr(self, 'last_frame_end', t_start)  # NEW
        if gap > 0.1:                                # NEW
            print(f"*** GAP BETWEEN FRAMES: {gap:.3f}s ***")      # NEW
        dt   = self.clock.tick(60) / 1000.0
        t_tick = time.perf_counter()                 # NEW
        form = IPUI.active()
        self.frame_count += 1

        # ── Snapshot all input state ──────────────────────────
        ip = self.ip
        ip.frame_begin(dt, int(self.clock.get_fps()), self.frame_count, _IPUI.screen, form)

        # ── Events ────────────────────────────────────────────
        for event in pygame.event.get():
            if      event.type == pygame.QUIT:      _IPUI.is_running = False
            elif(   event.type == pygame.KEYDOWN
            and     event.key  == pygame.K_ESCAPE): self.handle_escape()
            else:
                ip.events.append(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                    ip.mouse_wheel += (-1 if event.button == 4 else 1)
                consumed = IPUI.process_events(event)
                if not consumed:
                    ip.unhandled.append(event)

        t_mid = time.perf_counter()                  # NEW
        if form: form.ip_think(ip)
        IPUI.update()
        _IPUI.screen.fill(Style.COLOR_BACKGROUND)
        if form: form.ip_renderpre(ip)
        IPUI.render(_IPUI.screen)
        if form: form.ip_renderpost(ip)
        t_pre_flip = time.perf_counter()             # NEW
        pygame.display.flip()
        t_end = time.perf_counter()                  # NEW

        total = t_end - t_start                      # NEW
        if total > 0.03:                              # NEW
            print(f"SLOW FRAME {self.frame_count}: "             # NEW
                  f"tick={t_tick-t_start:.3f} "                  # NEW
                  f"work={t_pre_flip-t_tick:.3f} "               # NEW
                  f"flip={t_end-t_pre_flip:.3f} "                # NEW
                  f"TOTAL={total:.3f}")                          # NEW

        self.last_frame_end = time.perf_counter()    # NEW

        if self.frame_count % 60 == 0:               # NEW
            print(f"heartbeat frame={self.frame_count}")


    def handle_escape(self):
        _IPUI.is_running = False  # For now; later: if forge, switch to lab

    def init_pygame(self, title: str, fullscreen=False ):
        if title is None: title = "IPUI Framework"
        if Style.SCREEN_HEIGHT==0 or Style.SCREEN_WIDTH==0:fullscreen=True
        pygame.display.set_caption(title)

        MgrFont.init()
        MgrColor.init()
        if fullscreen:
                info              = pygame.display.Info()
                Style.SCREEN_WIDTH, Style.SCREEN_HEIGHT = info.current_w, info.current_h
                self.__class__.screen = pygame.display.set_mode((Style.SCREEN_WIDTH, Style.SCREEN_HEIGHT), pygame.FULLSCREEN)
        #else:   self.__class__.screen = pygame.display.set_mode((Style.SCREEN_WIDTH, Style.SCREEN_HEIGHT))

        else:
            self.__class__.screen = pygame.display.set_mode((Style.SCREEN_WIDTH, Style.SCREEN_HEIGHT),pygame.DOUBLEBUF | pygame.HWSURFACE)  # REPLACE

        pygame.scrap.init()
