# IPUI.py  Update: process_events returns consumed bool for unhandled tracking

class IPUI:
    screen       = None
    forms        = {}          # {FormClass: instance}
    stack        = []          # history of FormClass keys
    form_count   = 0           # for auto-titling
    debug_target = None
    pulse_widget = None
    pulse_start  = 0
    pulse_return = None
    # ─────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────

    @classmethod
    def show(cls, form_class, title=None, fullscreen=False, width=0, height=0):
        import types
        if isinstance(form_class, types.ModuleType):
            form_class = getattr(form_class, form_class.__name__.split('.')[-1])
        #print(f"IN Show{width}")
        from ipui.engine.GameLoop import GameLoop
        if not GameLoop.screen:
            GameLoop(form_class, title, fullscreen,width,height)
        else:
            cls.switch(form_class, title)

    @classmethod
    def back(cls):
        if len(cls.stack) > 1:
            import pygame
            cls.stack.pop()
            form = cls.forms[cls.stack[-1]]
            pygame.display.set_caption(getattr(form, '_window_title', 'IPUI'))
            cls.notify_activated(form)

    @classmethod
    def destroy(cls, form_class):
        cls.forms.pop(form_class, None)
        cls.stack = [k for k in cls.stack if k is not form_class]

    @classmethod
    def active(cls):
        if cls.stack:
            return cls.forms.get(cls.stack[-1])
        return None

    # ─────────────────────────────────────────────
    # Internal: form switching
    # ─────────────────────────────────────────────

    @classmethod
    def switch(cls, form_class, title=None):
        import pygame
        if form_class not in cls.forms:
            cls.forms[form_class] = form_class()
        cls.stack.append(form_class)
        t = title or cls.auto_title()
        cls.forms[form_class]._window_title = t
        pygame.display.set_caption(t)
        cls.notify_activated(cls.forms[form_class])



    @classmethod
    def notify_activated(cls, form):
        ip = cls.ip
        ip.set_tab_context(form, type(form).__name__, True, form)
        form.ip_activated(ip)
        if form.tab_strip:
            name = form.tab_strip.active_tab
            tab  = form.tab_strip.tab_cache.get(name)
            if tab:
                ip.set_tab_context(tab, name, True, form.tab_strip.content)
                tab.ip_activated(ip)

    @classmethod
    def auto_title(cls):
        cls.form_count += 1
        if cls.form_count == 1:
            return "IPUI"
        return f"IPUI {cls.form_count - 1}"

    # ─────────────────────────────────────────────
    # Routing (formerly MgrUI)
    # ─────────────────────────────────────────────

    @classmethod
    def render(cls, surface):
        form = cls.active()
        if form: form.render(surface)

    #@classmethod
    #def update(cls):
    #    form = cls.active()
    #    if form: form.update()
