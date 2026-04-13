# StateMachine.py  New: Delegate-based state machine for IPUI

class StateMachine:
    """Delegate-based state machine accessible via ip.state.

    Usage:
        ip.state.add("DEMO",      self.state_demo)
        ip.state.add("READY",     self.state_ready)
        ip.state.add("PLAYING",   self.state_playing)
        ip.state.add("GAME_OVER", self.state_game_over, "DEMO")
        ip.state.go("DEMO")

    Named machines:
        ip.state("combat").add("IDLE", self.combat_idle)
    """

    def __init__(self):
        self.current         = None
        self.private_states  = {}
        self.private_order   = []
        self.private_timer   = 0.0
        self.private_named   = {}
        self.private_debug   = False

    def __call__(self, name=None):
        if name is None:
            return self
        if name not in self.private_named:
            self.private_named[name] = StateMachine()
        return self.private_named[name]


    def add(self, name, delegate, next_state=None, duration=0.0):
        self.private_states[name] = {"delegate": delegate, "next": next_state, "duration": duration}
        self.private_order.append(name)


    def go(self, name, duration=None):
        old                = self.current
        self.current       = name
        entry              = self.private_states.get(name, {})
        self.private_timer = duration if duration is not None else entry.get("duration", 0.0)
        if self.private_debug:
            dur = f" (duration={self.private_timer})" if self.private_timer > 0 else ""
            print(f"[STATE] {old} → {name}{dur}")

    def next(self):
        entry = self.private_states.get(self.current)
        if not entry:
            return
        explicit = entry["next"]
        if explicit:
            if self.private_debug:
                print(f"[STATE] {self.current} → {explicit} (timer expired)")
            self.go(explicit)
            return
        order = self.private_order
        idx   = order.index(self.current) if self.current in order else -1
        if idx >= 0 and idx + 1 < len(order):
            if self.private_debug:
                print(f"[STATE] {self.current} → {order[idx + 1]} (timer expired)")
            self.go(order[idx + 1])

    def tick(self, dt):
        self.tick_self(dt)
        for sm in self.private_named.values():
            sm.tick_self(dt)

    def tick_self(self, dt):
        if self.private_timer > 0:
            self.private_timer -= dt
            if self.private_timer <= 0:
                self.private_timer = 0
                self.next()
                return
        entry = self.private_states.get(self.current)
        if entry and entry["delegate"]:
            entry["delegate"]()

    def is_(self, name):
        return self.current == name

    def debug(self, enabled=True):
        pass
        #self.private_debug = enabled

