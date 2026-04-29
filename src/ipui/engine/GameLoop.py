import pygame
from ipui.Style import Style
from ipui._forms.NeuroForge.custom_widgets.Logger import Logger
from ipui.engine.IPUI import IPUI
from ipui.engine.MgrFont import MgrFont
from ipui.engine.MgrColor import MgrColor
from ipui.engine.IP import IP
from ipui.engine.MgrInput import MgrInput
import time

class GameLoop:
    screen      = None
    is_running  = True
    def __init__(self, form_class, title=None,fullscreen=False, width=0, height=0):
        Logger()
        pygame  .init()
        pygame.key.set_repeat(350, 35)  # delay ms, interval ms (enables KEYDOWN repeats)

        self.last_wall_time = time.perf_counter() #fix lag issue
        self    .init_pygame( title, fullscreen=fullscreen, width=width, height=height)
        IPUI    .screen     = GameLoop.screen
        self    .ip         = IP()
        IPUI    .ip         = self.ip
        self    .clock      = pygame.time.Clock()
        IPUI    .switch     ( form_class, title)
        self    .frame_count= 0
        self    .run_loop()
        pygame  .quit()

    def run_loop(self):
        while GameLoop.is_running: self.pygame_loop()

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
        ip.frame_begin(dt, int(self.clock.get_fps()), self.frame_count, GameLoop.screen, form)

        # ── Collect events ────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameLoop.is_running = False
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
        GameLoop.screen.fill(Style.COLOR_BACKGROUND)
        if form: form.dispatch_ip_render(ip, "ip_draw")

        # ── UI Draw ───────────────────────────────────────────
        IPUI.render(GameLoop.screen)

        # ── RENDER POST ───────────────────────────────────────
        if form: form.dispatch_ip_render(ip, "ip_draw_hud")

        # ── Flip ──────────────────────────────────────────────
        pygame.display.flip()

    def init_pygame(self, title, fullscreen=False, width=0, height=0):
        if title is None: title = "IPUI Framework"
        pygame.display.set_caption(title)
        MgrFont.init()
        MgrColor.init()
        info = pygame.display.Info()
        if fullscreen:


            self.__class__.screen = pygame.display.set_mode(
                ( info.current_w, info.current_h),
                pygame.FULLSCREEN | pygame.SCALED)
        else:
            if width  == 0: width  = info.current_w
            if height == 0: height = int(info.current_h * 0.85)
            self.__class__.screen = pygame.display.set_mode(
                (width, height),
                pygame.SCALED)
        pygame.scrap.init()