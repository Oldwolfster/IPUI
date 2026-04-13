# _IPUI.py  Update: ip service portal replaces ctx
import pygame
from ipui.Style import Style
from forms.NeuroForge.custom_widgets.Logger import Logger
from ipui.engine.IPUI import IPUI
from ipui.engine.MgrFont import MgrFont
from ipui.engine.MgrColor import MgrColor
from ipui.engine.IP import IP
from ipui.engine.MgrInput import MgrInput
import time

class _IPUI:
    screen      = None
    is_running  = True
    def __init__(self, form_class, title=None):
        Logger()
        pygame  .init()
        pygame.key.set_repeat(350, 35)  # delay ms, interval ms (enables KEYDOWN repeats)
        print("pygame loop constructor")
        self.last_wall_time = time.perf_counter() #fix lag issue
        self    .init_pygame( title)
        IPUI    .screen     = _IPUI.screen
        self    .ip         = IP()
        IPUI    .ip         = self.ip
        self    .clock      = pygame.time.Clock()
        IPUI    .switch     ( form_class, title)
        self    .frame_count= 0
        self    .run_loop()
        pygame  .quit()

    def run_loop(self):
        while _IPUI.is_running: self.pygame_loop()

    # ══════════════════════════════════════════════════════════════
    # THE LOOP — one frame
    # ══════════════════════════════════════════════════════════════

    def pygame_loop(self):
        #dt   = self.clock.tick(60) / 1000.0
        dt = min(self.clock.tick(60) / 1000.0, 0.05)#Prevent jump when there is lag.
        if dt > 0.1:            print(f"DT SPIKE: {dt:.3f}")


        now = time.perf_counter()           #fix lag issue
        wall_dt = now - self.last_wall_time #fix lag issue
        self.last_wall_time = now#fix lag issue
        if wall_dt > 0.1:            dt = 0.001  # treat stall recovery frame as near-zero #fix lag issue

        form = IPUI.active()
        self.frame_count += 1

        # ── Snapshot all input state ──────────────────────────
        ip = self.ip
        ip.frame_begin(dt, int(self.clock.get_fps()), self.frame_count, _IPUI.screen, form)

        # ── Collect events ────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _IPUI.is_running = False
            else:
                ip.events.append(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                    ip.mouse_wheel += (-1 if event.button == 4 else 1)

        # ── MgrInput — all dispatch in one place ──────────────
        MgrInput.process_frame(ip, form)

        # ── THINK ─────────────────────────────────────────────
        if form: form.dispatch_ip_think(ip)

        # ── Layout ────────────────────────────────────────────
        IPUI.update()

        # ── RENDER PRE ────────────────────────────────────────
        _IPUI.screen.fill(Style.COLOR_BACKGROUND)
        if form: form.dispatch_ip_render(ip, "ip_draw")

        # ── UI Draw ───────────────────────────────────────────
        IPUI.render(_IPUI.screen)

        # ── RENDER POST ───────────────────────────────────────

        #if form: form.ip_draw_hud(ip)
        if form: form.dispatch_ip_render(ip, "ip_draw_hud")
        #ip.state.draw_flash(ip)
        # ── Flip ──────────────────────────────────────────────
        pygame.display.flip()

    def init_pygame(self, title: str, fullscreen=False ):
        if title is None: title = "IPUI Framework"
        if Style.SCREEN_HEIGHT==0 or Style.SCREEN_WIDTH==0:fullscreen=True

        pygame.display.set_caption(title)

        MgrFont.init()
        MgrColor.init()
        # _IPUI.py method: init_pygame  Update: use SCALED to prevent DWM display stalls
        if fullscreen:
            info = pygame.display.Info()
            Style.SCREEN_WIDTH, Style.SCREEN_HEIGHT = info.current_w, info.current_h
            self.__class__.screen = pygame.display.set_mode((Style.SCREEN_WIDTH, Style.SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        else:
            self.__class__.screen = pygame.display.set_mode((Style.SCREEN_WIDTH, Style.SCREEN_HEIGHT), pygame.SCALED)
        pygame.scrap.init()
