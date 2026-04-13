import ipui
from ipui import *

class Rules(_BaseTab):

    def world_rules(self, parent):
        root = CardCol(parent, scrollable=True)

        Heading(root, "World: Space & Boundaries", glow=True)

        c1 = Card(root)
        Heading(c1, "Topology")
        Body(c1, "• The universe is a 2D rectangle.")
        Body(c1, "• Edges wrap around (toroidal world): exiting one side re-enters on the opposite side.")

        c2 = Card(root)
        Heading(c2, "Locality")
        Body(c2, "• Interactions are local: particles only “see” others within range.")
        Body(c2, "• Think: no long-distance telepathy.")

        c3 = Card(root)
        Heading(c3, "Key Distances")
        Body(c3, "r_min  = collision bubble (too close)")
        Body(c3, "r_mid  = preferred interaction distance (strongest influence)")
        Body(c3, "r_max  = interaction limit (too far = ignored)")

        c4 = Card(root)
        Heading(c4, "Segue")
        Body(c4, "Next pane: three interaction zones.")
        Body(c4, "Close = repel, mid-range = attract/repel by type, far = ignore.")


    def interaction_rules(self, parent):
        root = CardCol(parent, scrollable=True)

        Heading(root, "Interactions: Influence Zones", glow=True)

        c1 = Card(root)
        Heading(c1, "Zone 1 — Collision Bubble (d < r_min)")
        Body(c1, "• Strong repulsion to prevent stacking / overlap.")
        Body(c1, "• Think: personal space / hard-core avoidance.")

        c2 = Card(root)
        Heading(c2, "Zone 2 — Interaction Ring (r_min ≤ d ≤ r_max)")
        Body(c2, "• Force comes from type-to-type table: G[type_i][type_j] ∈ [-1, +1].")
        Body(c2, "  + attraction, - repulsion, 0 ignore.")
        Body(c2, "• Influence fades smoothly with distance (peak around r_mid).")
        Body(c2, "• Think: species relationships.")

        c3 = Card(root)
        Heading(c3, "Zone 3 — Beyond Range (d > r_max)")
        Body(c3, "• No force at all.")
        Body(c3, "• Think: out of range = irrelevant.")


    def dynamics_rules(self, parent):
        root = CardCol(parent, scrollable=True)

        Heading(root, "Dynamics: How Time Advances", glow=True)

        c1 = Card(root)
        Heading(c1, "Per Tick (dt)")
        Body(c1, "1) Sum interaction forces → acceleration")
        Body(c1, "2) vel += accel * dt")
        Body(c1, "3) Apply damping: vel *= (1 - damping)")
        Body(c1, "4) Clamp speed to v_max")
        Body(c1, "5) pos += vel * dt")
        Body(c1, "6) Wrap position around edges")

        c2 = Card(root)
        Heading(c2, "Stability Guards")
        Body(c2, "• Damping prevents energy blow-ups.")
        Body(c2, "• Speed clamp prevents particle bullets.")
        Body(c2, "• Wrap-around prevents wall pileups.")

        c3 = Card(root)
        Heading(c3, "Common Defaults (typical)")
        Body(c3, "dt       = 1.0   (simulation step)")
        Body(c3, "damping  = 0.05  (energy bleed)")
        Body(c3, "v_max    = 3.0   (speed limit)")
        Body(c3, "r_min    = 6     (collision bubble)")
        Body(c3, "r_mid    = 24    (peak influence)")
        Body(c3, "r_max    = 60    (interaction range)")