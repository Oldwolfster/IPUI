# Settings.py  Update: Replace reactive demo with ParticleLife sim settings

from ipui import *


class Settings(_basePane):

    def settings(self, parent):
        root = CardCol(parent, scrollable=True)
        Heading(root, "Simulation Settings", glow=True)
        Body(root, "Tweak these while the sim runs — changes apply immediately.")
        self.build_distances(root)
        self.build_dynamics(root)
        self.build_visuals(root)

    def build_distances(self, root):
        card = Card(root)
        Heading(card, "Distance Zones")
        Body(card, "Control the three interaction radii.\nSmaller r_min = tighter clusters. Larger r_max = longer-range influence.")
        row = CardRow(card, width_flex=True)
        TextBox(row, placeholder="r_min",  pipeline_key="pl.sim.r_min",  width_flex=1)
        TextBox(row, placeholder="r_mid",  pipeline_key="pl.sim.r_mid",  width_flex=1)
        TextBox(row, placeholder="r_max",  pipeline_key="pl.sim.r_max",  width_flex=1)

    def build_dynamics(self, root):
        card = Card(root)
        Heading(card, "Dynamics")
        Body(card, "How particles move and interact.\nHigher damping = calmer system. Higher force_scale = stronger attractions/repulsions.")
        row = CardRow(card, width_flex=True)
        TextBox(row, placeholder="Damping",            pipeline_key="pl.sim.damping",            width_flex=1)
        TextBox(row, placeholder="Max Velocity",       pipeline_key="pl.sim.v_max",              width_flex=1)
        row2 = CardRow(card, width_flex=True)
        TextBox(row2, placeholder="Force Scale",       pipeline_key="pl.sim.force_scale",        width_flex=1)
        TextBox(row2, placeholder="Collision Strength", pipeline_key="pl.sim.collision_strength", width_flex=1)

    def build_visuals(self, root):
        card = Card(root)
        Heading(card, "Visuals")
        Body(card, "Trail alpha controls motion blur.\n0 = full trails (no fade), 255 = no trails (instant clear).")
        row = CardRow(card, width_flex=True)
        TextBox(row, placeholder="Trail Alpha (0-255)", pipeline_key="pl.sim.trail_alpha", width_flex=1)

    def settings(self, parent):
        root = CardCol(parent, scrollable=True)
        Heading(root, "Simulation Settings", glow=True)
        Body(root, "Tweak these while the sim runs — changes apply immediately.")
        self.build_distances(root)
        self.build_dynamics(root)
        self.build_visuals(root)
