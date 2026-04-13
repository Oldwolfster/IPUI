# IPUI.py  Update: process_events returns consumed bool for unhandled tracking

class IPUI:
    screen      = None
    forms       = {}          # {FormClass: instance}
    stack       = []          # history of FormClass keys
    form_count  = 0           # for auto-titling
    debug_target = None
    # ─────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────

    @classmethod
    def show(cls, form_class, title=None):
        # IPUI.py  method: show  Update: auto-resolve module to class
        import types  # NEW
        if isinstance(form_class, types.ModuleType):  # NEW
            form_class = getattr(form_class, form_class.__name__.split('.')[-1])

        from ipui.engine._IPUI import _IPUI
        if not _IPUI.screen:
            _IPUI(form_class, title)
        else:
            cls.switch(form_class, title)

    @classmethod
    def back(cls):
        if len(cls.stack) > 1:
            import pygame
            cls.stack.pop()
            form = cls.forms[cls.stack[-1]]
            pygame.display.set_caption(getattr(form, '_window_title', 'IPUI'))

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

    @classmethod
    def update(cls):
        form = cls.active()
        if form: form.update()
