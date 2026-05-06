### Where does the pygame logic go? — `ip_*` hooks (Quick Start)

IPUI sets up the pygame engine and ensures all superclasses get the right parameters. So where does *your* code go?

You've already seen part of the answer: **pane methods** build the widget tree in the panes you defined in `TAB_LAYOUT`. The other half is **`ip_*` hooks** — they're how you talk to the game loop:

- **`ip_setup(self, ip)`** — runs once before the first frame. Initialize state here.
- **`ip_think(self, ip)`** — runs every frame. Update state, run physics, decide things.
- **`ip_draw(self, ip)`** — runs every frame. Custom rendering on the active pane.
- **`ip_draw_hud(self, ip)`** — runs every frame, drawn on top of everything. FPS counters, overlays.

The framework calls these; you override them. Together with pane methods, that's the whole split:

> **If it lays out widgets, it goes in a pane method. If it ticks, decides, animates, or paints custom graphics, it goes in an `ip_*` hook.**

The full set of hooks is covered in [Lifecycle Hooks](#lifecycle-hooks) further down. For now, knowing the four above is enough to read most IPUI code.

---

### Example: BouncingBall

Here's the split in one file. Tab layout, pane method, lifecycle hooks, and a helper, all in one place:

```python
from ipui import *
import pygame

class BouncingBall(_BaseTab):

    def arena(self, parent):                        # ← pane method: builds the UI
        Title(parent, text="Bouncing Ball")
        card = Card(parent, scroll_v=True)
        CodeBox(card, data=__file__)

    def ip_setup(self, ip):                         # ← runs once
        self.ball_x,  self.ball_y  = 0.5, 0.5       # start in the middle
        self.ball_dx, self.ball_dy = 0.4, 0.3       # velocity (normalized units / sec)

    def ip_think(self, ip):                         # ← runs every frame
        self.ball_x += self.ball_dx * ip.dt         # ip.dt = seconds since last frame
        self.ball_y += self.ball_dy * ip.dt
        self.bounce_off_walls()

    def ip_draw_normalized(self, ip):               # ← custom rendering (we'll improve this in a moment)
        arena = self.form.tab_strip.panes[0].rect             # spelunk for the arena rect
        sx    = arena.left + int(self.ball_x * arena.width)   # offset + scale by pixel count
        sy    = arena.top  + int(self.ball_y * arena.height)
        r     = int(0.02 * arena.height)
        pygame.draw.circle(ip.surface, (255, 160, 40), (sx, sy), r)

    def bounce_off_walls(self):
        if self.ball_x < 0: self.ball_dx =  0.4
        if self.ball_x > 1: self.ball_dx = -0.4
        if self.ball_y < 0: self.ball_dy =  0.3
        if self.ball_y > 1: self.ball_dy = -0.3
```

> Notice `ball_x` and `ball_y` are **normalized**: `0` is the left/top edge, `1` is the right/bottom edge. IPUI worries about the real pixel resolution. (Unless you'd rather work in raw pygame coordinates — you have full access to either.)

That works. But `ip_draw_normalized` is doing some manual spelunking — pulling pane rects, computing offsets, scaling by hand. There's a cleaner way.

---

### The `ip` Service Portal

Every lifecycle hook receives a single argument: `ip`. It's the IPUI Service Portal — one object that gives you everything you need. Type `ip.` in your IDE and autocomplete shows every attribute and method, organized by family.

You've already used `ip.dt` (time since last frame). The portal also handles coordinate conversion. Replace the manual draw method with this:

```python
    def ip_draw(self, ip):
        pos = ip.to_screen(self.ball_x, self.ball_y)    # normalized → screen pixels
        r   = ip.scale_y(0.02)                          # scale a normalized radius
        pygame.draw.circle(ip.surface, (255, 160, 40), pos, r)
```

Three lines. No spelunking. No manual math. Resolution-independent. The portal absorbs all the coordinate plumbing so you can focus on what you're actually drawing.

> **Both methods coexist** — IPUI doesn't care which one you keep, and you can flip between them by renaming. We're keeping `ip_draw` going forward; the `_normalized` version is just there to show what the portal saved you.

---

### Updating the UI

Now let's add some widgets that *react* to the ball's position. Show the user which direction the ball is moving, which quadrant it's in, and a label that warns when it's near a wall.

#### Imperative — direct, surgical

Add the widgets in the pane method, store references, update them every frame:

```python
    def arena(self, parent):
        Title(parent, text="Bouncing Ball")
        card = Card(parent, scroll_v=True)
        CodeBox(card, data=__file__)
        self.lbl_quadrant  = Body(parent, "Quadrant: —")
        self.lbl_direction = Body(parent, "Direction: —")
        self.lbl_warning   = Body(parent, "")

    def ip_think_imperative(self, ip):
        self.ball_x += self.ball_dx * ip.dt
        self.ball_y += self.ball_dy * ip.dt
        self.bounce_off_walls()

        # update every consumer by hand
        q = self.compute_quadrant(self.ball_x, self.ball_y)
        d = self.compute_direction(self.ball_dx, self.ball_dy)
        w = self.compute_warning (self.ball_x, self.ball_y)
        self.lbl_quadrant .set_text(f"Quadrant: {q}")
        self.lbl_direction.set_text(f"Direction: {d}")
        self.lbl_warning  .set_text(w)

    def compute_quadrant(self, x, y):
        return ("NW" if y < 0.5 else "SW") if x < 0.5 else ("NE" if y < 0.5 else "SE")

    def compute_direction(self, dx, dy):
        h = "→" if dx > 0 else "←"
        v = "↓" if dy > 0 else "↑"
        return f"{h}{v}"

    def compute_warning(self, x, y):
        edge = min(x, y, 1 - x, 1 - y)
        return "⚠ near wall" if edge < 0.05 else ""
```

This works. It's clear. Every widget update is an explicit line you can grep for and breakpoint on.

But notice what `ip_think` has become: three lines of physics followed by six lines of widget plumbing. And every time you add a fourth widget, `ip_think` grows. The physics is fine; the dispatching is doing all the talking.

#### Reactive — declare relationships, let the framework propagate

Replace the imperative `ip_think_imperative` with the original `ip_think` (just the physics) and add a `BINDINGS` dict. The compute methods stay as-is.

```python
class BouncingBall(_BaseTab):

    BINDINGS = {
        "lbl_quadrant":  {
            "property": "text",
            "compute":  "compute_quadrant_text",
            "triggers": ["ball_x", "ball_y"],
        },
        "lbl_direction": {
            "property": "text",
            "compute":  "compute_direction_text",
            "triggers": ["ball_dx", "ball_dy"],
        },
        "lbl_warning":   {
            "property": "text",
            "compute":  "compute_warning_text",
            "triggers": ["ball_x", "ball_y"],
        },
    }

    def ip_think(self, ip):
        self.ball_x += self.ball_dx * ip.dt
        self.ball_y += self.ball_dy * ip.dt
        self.bounce_off_walls()
        self.form.pipeline_set("ball_x",  self.ball_x)
        self.form.pipeline_set("ball_y",  self.ball_y)
        self.form.pipeline_set("ball_dx", self.ball_dx)
        self.form.pipeline_set("ball_dy", self.ball_dy)

    def compute_quadrant_text (self, ball_x, ball_y):           return f"Quadrant: {('NW' if ball_y<0.5 else 'SW') if ball_x<0.5 else ('NE' if ball_y<0.5 else 'SE')}"
    def compute_direction_text(self, ball_dx, ball_dy):         return f"Direction: {'→' if ball_dx>0 else '←'}{'↓' if ball_dy>0 else '↑'}"
    def compute_warning_text  (self, ball_x, ball_y):           return "⚠ near wall" if min(ball_x, ball_y, 1-ball_x, 1-ball_y) < 0.05 else ""
```

The framework now watches the four pipeline keys. When any change, the matching compute method runs and the widget updates. Add a fourth widget that depends on `ball_x`? Add one entry to `BINDINGS`. `ip_think` doesn't grow.

#### Which one should you use?

> Honest answer: this example is roughly a tie. You have four pipeline_set calls vs. six set_text calls — neither version is obviously cleaner. Reactive starts to win when state drives many widgets, or when several places update the same state. Imperative stays clearer when one widget reflects one piece of state and you want a single named method everyone calls. **Mix them in the same tab.** IPUI doesn't have an opinion on which paradigm is "correct" — only that you should have the choice and that both should be cheap.

---