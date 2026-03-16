# IP.py  The IPUI Service Portal
#
# ╔══════════════════════════════════════════════════════════════╗
# ║  ip is the canonical access path for pane authors.          ║
# ║                                                             ║
# ║  Type ip. and your IDE shows you everything you can         ║
# ║  know and everything you can do. No hunting.                ║
# ║                                                             ║
# ║  Attributes = current state / facts                         ║
# ║  Methods    = actions / derived queries                     ║
# ║                                                             ║
# ║  DRAW IN ip_think AT YOUR OWN RISK.                         ║
# ╚══════════════════════════════════════════════════════════════╝

import pygame


class IP:
    """IPUI Service Portal — one object, everything you need.

    Passed to ip_think(ip), ip_renderpre(ip), ip_renderpost(ip).
    Type ip.help() for a guided tour.

    ═══════════════════════════════════════════
    FAMILIES: identity, timing, geometry, mouse,
              keyboard, rendering, cache, discovery
    ═══════════════════════════════════════════
    """

    def __init__(self):
        # ── Identity (set per-dispatch by framework) ──────────
        self.form               = None      # active Form instance
        self.form_name          = ""        # name of active form
        self.pane               = None      # active _basePane instance
        self.pane_name          = ""        # name of active pane/tab
        self.is_active_pane     = False     # is the current pane the visible one?

        # ── Timing ────────────────────────────────────────────
        self.dt                 = 0.0       # seconds since last frame
        self.fps                = 0         # current frames per second
        self.frame              = 0         # monotonically increasing frame counter
        self.elapsed            = 0.0       # total seconds since app start

        # ── Geometry (set per-dispatch by framework) ──────────
        self.rect_pane          = None      # the canvas — None pane rect, or single pane rect
        self.rect_tab_area      = None      # the whole tab content row
        self.rect_screen        = None      # the full pygame surface rect

        # ── Mouse — one snapshot per frame ────────────────────
        self.mouse_x            = 0
        self.mouse_y            = 0
        self.mouse_pos          = (0, 0)
        self.private_mouse_prev = (0, 0)    # previous frame for delta
        self.private_buttons    = [False, False, False]  # left, middle, right held
        self.private_prev_btns  = [False, False, False]  # previous frame buttons
        self.mouse_wheel        = 0

        # ── Keyboard — one snapshot per frame ─────────────────
        self.private_keys       = set()     # keys held this frame
        self.private_prev_keys  = set()     # keys held last frame
        self.mod_shift          = False
        self.mod_ctrl           = False
        self.mod_alt            = False

        # ── Rendering ─────────────────────────────────────────
        self.surface            = None      # pygame draw surface
        self.events             = []        # all pygame events this frame
        self.unhandled          = []        # events UI did not consume

        # ── Cache (local scratch pad — NOT pipeline) ──────────
        self.private_cache      = {}

    # ══════════════════════════════════════════════════════════════
    # FRAME UPDATE — called by _IPUI each frame, NOT by user code
    # ══════════════════════════════════════════════════════════════

    def frame_begin(self, dt, fps, frame, surface, form):
        """Called once per frame by the loop. Snapshots all input state."""
        # Timing
        self.dt              = dt
        self.fps             = fps
        self.frame           = frame
        self.elapsed         += dt
        self.surface         = surface
        self.rect_screen     = surface.get_rect() if surface else None
        self.events          = []
        self.unhandled       = []

        # Identity — form level
        self.form            = form
        self.form_name       = type(form).__name__ if form else ""

        # Mouse snapshot
        self.private_mouse_prev = self.mouse_pos
        self.mouse_pos       = pygame.mouse.get_pos()
        self.mouse_x         = self.mouse_pos[0]
        self.mouse_y         = self.mouse_pos[1]
        self.mouse_wheel     = 0

        # Mouse buttons — save previous, snapshot current
        self.private_prev_btns = list(self.private_buttons)
        btns                 = pygame.mouse.get_pressed(3)
        self.private_buttons = [btns[0], btns[1], btns[2]]

        # Keyboard — save previous, snapshot current
        self.private_prev_keys = set(self.private_keys)
        pressed              = pygame.key.get_pressed()
        self.private_keys    = {i for i in range(len(pressed)) if pressed[i]}
        mods                 = pygame.key.get_mods()
        self.mod_shift       = bool(mods & pygame.KMOD_SHIFT)
        self.mod_ctrl        = bool(mods & pygame.KMOD_CTRL)
        self.mod_alt         = bool(mods & pygame.KMOD_ALT)

    # ══════════════════════════════════════════════════════════════
    # PANE CONTEXT — called before dispatching to each pane's hook
    # ══════════════════════════════════════════════════════════════

    def set_pane_context(self, pane, pane_name, is_active, pane_widget=None):
        """Called before dispatching to each pane's hook."""
        self.pane            = pane
        self.pane_name       = pane_name
        self.is_active_pane  = is_active
        if pane_widget and pane_widget.rect:
            self.rect_tab_area = pane_widget.rect
        else:
            self.rect_tab_area = None
        self.rect_pane         = self.find_canvas_rect()

    def find_canvas_rect(self):
        """Locate the None pane's rect for the active tab.
        Falls back to rect_tab_area if no None pane exists."""
        if not self.form or not hasattr(self.form, 'tab_strip'):
            return None
        strip = self.form.tab_strip
        if not strip or not strip.active_tab:
            return None
        entries = strip.tab_layout.get(strip.active_tab, [])
        for i, entry in enumerate(entries):
            if entry[0] is None and i < len(strip.panes):
                pane = strip.panes[i]
                if pane and pane.rect:
                    return pane.rect
        return self.rect_tab_area

    # ══════════════════════════════════════════════════════════════
    # GEOMETRY — coordinate transforms
    # ══════════════════════════════════════════════════════════════
    def to_screen(self, nx, ny):
        """Convert normalized (0-1) coords to screen pixels within rect_pane."""
        r = self.rect_pane
        if not r:
            return (int(nx), int(ny))
        return (r.left + int(nx * r.width), r.top + int(ny * r.height))

    def to_local(self, sx, sy):
        """Convert screen pixels to normalized (0-1) coords within rect_pane."""
        r = self.rect_pane
        if not r or r.width == 0 or r.height == 0:
            return (float(sx), float(sy))
        return ((sx - r.left) / r.width, (sy - r.top) / r.height)
    def local_to_screen(self, x, y):
        """Convert pane-local coords to screen coords."""
        r = self.rect_pane
        if r:
            return (x + r.left, y + r.top)
        return (x, y)

    def screen_to_local(self, x, y):
        """Convert screen coords to pane-local coords."""
        r = self.rect_pane
        if r:
            return (x - r.left, y - r.top)
        return (x, y)



    def scale_x(self, n):
        """Convert normalized width (0-1) to pixels within rect_pane."""
        r = self.rect_pane
        return int(n * r.width) if r else int(n)

    # IP.py method: scale_y  New: normalized height to pixels
    def scale_y(self, n):
        """Convert normalized height (0-1) to pixels within rect_pane."""
        r = self.rect_pane
        return int(n * r.height) if r else int(n)


    # ══════════════════════════════════════════════════════════════
    # MOUSE — methods (derived queries, explicit targets)
    # ══════════════════════════════════════════════════════════════

    BUTTON_MAP = {"left": 0, "middle": 1, "right": 2}

    def mouse_down(self, button="left"):
        """Is the button held this frame?"""
        idx = self.BUTTON_MAP.get(button, 0)
        return self.private_buttons[idx]

    def mouse_pressed(self, button="left"):
        """Was the button just pressed this frame? (edge: not held last frame)"""
        idx = self.BUTTON_MAP.get(button, 0)
        return self.private_buttons[idx] and not self.private_prev_btns[idx]

    def mouse_released(self, button="left"):
        """Was the button just released this frame?"""
        idx = self.BUTTON_MAP.get(button, 0)
        return not self.private_buttons[idx] and self.private_prev_btns[idx]

    def mouse_inside(self, widget):
        """Is the mouse inside this widget's rect?"""
        return widget.rect and widget.rect.collidepoint(self.mouse_pos)

    def mouse_inside_pane(self):
        """Is the mouse inside the current pane?"""
        return self.rect_pane and self.rect_pane.collidepoint(self.mouse_pos)

    def mouse_inside_content(self):
        """Is the mouse inside the tab content area?"""
        return self.rect_tab_area and self.rect_tab_area.collidepoint(self.mouse_pos)

    def mouse_hits(self, rect):
        """Is the mouse inside this arbitrary rect?"""
        return rect and rect.collidepoint(self.mouse_pos)

    def mouse_local_pos(self, widget=None):
        """Mouse position relative to widget's top-left, or pane if no widget given."""
        if widget and widget.rect:
            return (self.mouse_x - widget.rect.left,
                    self.mouse_y - widget.rect.top)
        if self.rect_pane:
            return (self.mouse_x - self.rect_pane.left,
                    self.mouse_y - self.rect_pane.top)
        return (self.mouse_x, self.mouse_y)

    def mouse_local_x(self, widget=None):
        """Mouse x relative to widget or pane left edge."""
        ref = widget.rect if widget and widget.rect else self.rect_pane
        return self.mouse_x - ref.left if ref else self.mouse_x

    def mouse_local_y(self, widget=None):
        """Mouse y relative to widget or pane top edge."""
        ref = widget.rect if widget and widget.rect else self.rect_pane
        return self.mouse_y - ref.top if ref else self.mouse_y

    # ══════════════════════════════════════════════════════════════
    # KEYBOARD — methods
    # ══════════════════════════════════════════════════════════════

    def key_down(self, key):
        """Is this key held this frame? Accepts pygame key constant or string."""
        k = self.resolve_key(key)
        return k in self.private_keys

    def key_pressed(self, key):
        """Was this key just pressed this frame?"""
        k = self.resolve_key(key)
        return k in self.private_keys and k not in self.private_prev_keys

    def key_released(self, key):
        """Was this key just released this frame?"""
        k = self.resolve_key(key)
        return k not in self.private_keys and k in self.private_prev_keys

    @staticmethod
    def resolve_key(key):
        """Accept pygame constant (int) or string like 'space', 'a', 'left'."""
        if isinstance(key, int):
            return key
        return getattr(pygame, f"K_{key}", None)

    # ══════════════════════════════════════════════════════════════
    # CACHE — local scratch pad, NOT pipeline
    # ══════════════════════════════════════════════════════════════
    #
    # ip.cache is a simple key-value store for pane-local data.
    # It persists across frames but has NO connection to the
    # reactive pipeline. It does NOT trigger derives or update
    # widgets. For that, use self.form.pipeline_set/read.
    #
    # Use cache for: animation counters, drag state, accumulators,
    # temporary values that don't need to drive UI updates.
    # ══════════════════════════════════════════════════════════════

    def cache_get(self, key, default=None):
        """Read from local cache. NOT pipeline — no side effects."""
        return self.private_cache.get(key, default)

    def cache_set(self, key, value):
        """Write to local cache. NOT pipeline — no derives triggered."""
        self.private_cache[key] = value

    def cache_has(self, key):
        """Check if key exists in cache."""
        return key in self.private_cache

    def cache_del(self, key):
        """Remove key from cache."""
        self.private_cache.pop(key, None)

    # ══════════════════════════════════════════════════════════════
    # INVALIDATION — scaffolded for future optimization
    # ══════════════════════════════════════════════════════════════
    #
    # Currently IPUI renders every frame. These methods exist so
    # pane authors write code that will work when we optimize.
    # For now they are no-ops. When dirty-flag rendering lands,
    # these will start mattering — and your code won't change.
    # ══════════════════════════════════════════════════════════════

    def request_redraw(self):
        """Mark pane as needing repaint. (Currently renders every frame.)"""
        if self.form:
            self.form.mark_dirty()

    def request_layout(self):
        """Mark pane as needing layout recalc. (Currently layouts every frame.)"""
        if self.form:
            self.form.mark_dirty()

    # ══════════════════════════════════════════════════════════════
    # DISCOVERY — find and explain
    # ══════════════════════════════════════════════════════════════

    def find(self, name):
        """Locate a widget by name. Returns widget or None."""
        if self.form and hasattr(self.form, 'widgets'):
            return self.form.widgets.get(name)
        return None

    def help(self, topic=None):
        """Print what ip can do. Pass a topic for focused help."""
        if topic:
            return self.help_topic(topic)
        return self.help_all()

    def help_all(self):
        """Print the full service portal guide."""
        sections = [
            self.help_section_identity(),
            self.help_section_timing(),
            self.help_section_geometry(),
            self.help_section_mouse(),
            self.help_section_keyboard(),
            self.help_section_rendering(),
            self.help_section_cache(),
            self.help_section_invalidation(),
            self.help_section_discovery(),
        ]
        text = "\n".join(sections)
        print(text)
        return text

    def help_topic(self, topic):
        """Print help for a specific topic family."""
        topic = topic.lower()
        lookup = {
            "identity":     self.help_section_identity,
            "form":         self.help_section_identity,
            "pane":         self.help_section_identity,
            "timing":       self.help_section_timing,
            "time":         self.help_section_timing,
            "dt":           self.help_section_timing,
            "fps":          self.help_section_timing,
            "geometry":     self.help_section_geometry,
            "rect":         self.help_section_geometry,
            "rect_pane":    self.help_section_geometry,
            "rect_tab_area":self.help_section_geometry,
            "rect_screen":  self.help_section_geometry,
            "coordinate":   self.help_section_geometry,
            "local":        self.help_section_geometry,
            "mouse":        self.help_section_mouse,
            "click":        self.help_section_mouse,
            "keyboard":     self.help_section_keyboard,
            "key":          self.help_section_keyboard,
            "keys":         self.help_section_keyboard,
            "render":       self.help_section_rendering,
            "surface":      self.help_section_rendering,
            "draw":         self.help_section_rendering,
            "cache":        self.help_section_cache,
            "scratch":      self.help_section_cache,
            "redraw":       self.help_section_invalidation,
            "invalidate":   self.help_section_invalidation,
            "layout":       self.help_section_invalidation,
            "dirty":        self.help_section_invalidation,
            "find":         self.help_section_discovery,
            "help":         self.help_section_discovery,
            "discover":     self.help_section_discovery,
        }
        fn = lookup.get(topic)
        if fn:
            text = fn()
            print(text)
            return text
        msg = f"Unknown topic '{topic}'. Try: identity, timing, geometry, mouse, keyboard, render, cache, redraw, discover"
        print(msg)
        return msg

    @staticmethod
    def help_section_identity():
        return """
═══ IDENTITY ═══════════════════════════════
  ip.form             Active Form instance
  ip.form_name        Name of the active form
  ip.pane             Active Pane instance
  ip.pane_name        Name of the active tab/pane
  ip.is_active_pane   Is this the visible pane?
"""

    @staticmethod
    def help_section_timing():
        return """
═══ TIMING ═════════════════════════════════
  ip.dt               Seconds since last frame
  ip.fps              Current frames per second
  ip.frame            Frame counter (increases every frame)
  ip.elapsed          Total seconds since app started
"""

    @staticmethod
    def help_section_geometry():
        return """
═══ GEOMETRY ═══════════════════════════════
  ip.rect_pane       Rect of the canvas pane (None slot, or whole pane)
  ip.rect_tab_area   Rect of the whole tab content row
  ip.rect_screen     Rect of the full pygame surface

  ip.local_to_screen(x, y)   Pane-local → screen coords
  ip.screen_to_local(x, y)   Screen → pane-local coords

  ip.mouse_inside_pane()     Is mouse inside pane?
  ip.mouse_inside_content()  Is mouse inside tab content area?

  Use rect_pane for custom rendering in ip_renderpre/post.
  All coordinates are pane-relative when using local_to_screen.
"""

    @staticmethod
    def help_section_mouse():
        return """
═══ MOUSE ══════════════════════════════════
  ip.mouse_x          Mouse x position (screen)
  ip.mouse_y          Mouse y position (screen)
  ip.mouse_pos        Mouse (x, y) tuple
  ip.mouse_wheel      Scroll wheel delta this frame

  ip.mouse_down("left")       Is button held?
  ip.mouse_pressed("left")    Just pressed this frame?
  ip.mouse_released("left")   Just released this frame?
  ip.mouse_inside(widget)     Is mouse inside widget?
  ip.mouse_hits(rect)         Is mouse inside rect?

  ip.mouse_local_pos()        Mouse relative to pane
  ip.mouse_local_pos(widget)  Mouse relative to widget
  ip.mouse_local_x()          Mouse x relative to pane
  ip.mouse_local_y()          Mouse y relative to pane

  Buttons: "left", "middle", "right"
"""

    @staticmethod
    def help_section_keyboard():
        return """
═══ KEYBOARD ═══════════════════════════════
  ip.mod_shift        Shift held?
  ip.mod_ctrl         Ctrl held?
  ip.mod_alt          Alt held?

  ip.key_down("space")     Is key held this frame?
  ip.key_pressed("space")  Just pressed this frame?
  ip.key_released("space") Just released this frame?

  Keys: use pygame names without K_ prefix:
    "space", "a", "left", "right", "up", "down",
    "return", "escape", "tab", "backspace", etc.
"""

    @staticmethod
    def help_section_rendering():
        return """
═══ RENDERING ══════════════════════════════
  ip.surface          The pygame draw surface
  ip.events           All pygame events this frame
  ip.unhandled        Events the UI did not consume

  DRAW IN ip_think AT YOUR OWN RISK.
  Use ip_renderpre for backgrounds/game world.
  Use ip_renderpost for overlays/HUD.
"""

    @staticmethod
    def help_section_cache():
        return """
═══ CACHE (local scratch pad) ══════════════
  ip.cache_get(key, default=None)   Read value
  ip.cache_set(key, value)          Write value
  ip.cache_has(key)                 Check existence
  ip.cache_del(key)                 Remove key

  Cache is a simple key-value store. It persists
  across frames but has NO connection to the
  reactive pipeline. It does NOT trigger derives
  or update widgets.

  For reactive state: use self.form.pipeline_set/read
  For scratch data:   use ip.cache_set/get
"""

    @staticmethod
    def help_section_invalidation():
        return """
═══ INVALIDATION ═══════════════════════════
  ip.request_redraw()     Mark pane as needing repaint
  ip.request_layout()     Mark pane as needing layout recalc

  Currently IPUI renders every frame, so these are
  effectively no-ops. They exist so your code will
  work unchanged when dirty-flag optimization lands.
"""

    @staticmethod
    def help_section_discovery():
        return """
═══ DISCOVERY ══════════════════════════════
  ip.find("widget_name")     Find a widget by name
  ip.help()                  Print this guide
  ip.help("mouse")           Help on a specific topic

  Topics: identity, timing, geometry, mouse,
          keyboard, render, cache, redraw, discover
"""