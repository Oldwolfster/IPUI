import pygame
from ipui.Style import Style
from ipui.engine.Log import Logger
from ipui.engine.IPUI import IPUI
from ipui.engine.MgrFont import MgrFont
from ipui.engine.MgrColor import MgrColor


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
        #self    .MgrUI      . show(form_class)
        self    .clock      = pygame.time.Clock()
        self    .run_loop()
        pygame  .quit()

    def run_loop(self):
        while _IPUI.is_running: self.pygame_loop()

    def pygame_loopPreHook(self):
        for event in pygame.event.get():
            if      event.type == pygame.QUIT:      _IPUI.is_running = False
            elif(   event.type == pygame.KEYDOWN
            and     event.key  == pygame.K_ESCAPE): self.handle_escape()
            else:                                IPUI.process_events(event)
        IPUI.update()
        _IPUI.screen.fill(Style.COLOR_BACKGROUND)
        IPUI.render(_IPUI.screen)
        pygame.display.flip()
        self.clock.tick(60)


    def pygame_loop(self):
        dt = self.clock.tick(60) / 1000.0
        form = IPUI.active()
        for event in pygame.event.get():
            if      event.type == pygame.QUIT:      _IPUI.is_running = False
            elif(   event.type == pygame.KEYDOWN
            and     event.key  == pygame.K_ESCAPE): self.handle_escape()
            else:                                IPUI.process_events(event)
            if form: form.on_event(event)
        if form: form.on_update(dt)                                         
        IPUI.update()
        _IPUI.screen.fill(Style.COLOR_BACKGROUND)
        IPUI.render(_IPUI.screen)
        if form: form.on_draw(_IPUI.screen)                                 # NEW
        pygame.display.flip()



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
        else:   self.__class__.screen = pygame.display.set_mode((Style.SCREEN_WIDTH, Style.SCREEN_HEIGHT))
        pygame.scrap.init()