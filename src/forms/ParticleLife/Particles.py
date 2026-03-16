import ipui
from ipui import *
import random

class Particles(_basePane):

    def _ensure_defaults(self):
        ids = self.form.pipeline_read("pl.particle_ids")
        if ids:
            return

        self.form.pipeline_set("pl.particle_ids", ["A", "B"])

        # A defaults
        self.form.pipeline_set("pl.p.A.name" , "A")
        self.form.pipeline_set("pl.p.A.r"    , 255)
        self.form.pipeline_set("pl.p.A.g"    , 120)
        self.form.pipeline_set("pl.p.A.b"    , 0)
        self.form.pipeline_set("pl.p.A.count", 250)

        # B defaults
        self.form.pipeline_set("pl.p.B.name" , "B")
        self.form.pipeline_set("pl.p.B.r"    , 0)
        self.form.pipeline_set("pl.p.B.g"    , 170)
        self.form.pipeline_set("pl.p.B.b"    , 255)
        self.form.pipeline_set("pl.p.B.count", 250)


    def _next_id(self, ids):
        # Simple: A, B, C... (good enough for v0.1)
        n = len(ids)
        return chr(ord("A") + n)


    def _add_particle(self):
        ids = self.form.pipeline_read("pl.particle_ids") or []
        pid = self._next_id(ids)
        ids = ids + [pid]
        self.form.pipeline_set("pl.particle_ids", ids)

        # sensible defaults
        self.form.pipeline_set(f"pl.p.{pid}.name" , pid)
        self.form.pipeline_set(f"pl.p.{pid}.r"    , 180)
        self.form.pipeline_set(f"pl.p.{pid}.g"    , 180)
        self.form.pipeline_set(f"pl.p.{pid}.b"    , 180)
        self.form.pipeline_set(f"pl.p.{pid}.count", 200)

        # Rebuild THIS pane (pane index 0 inside "Particles" tab)
        # self.form.set_pane(0, self.particles)   # particles defined in TAB_LAYOUT as a method (pane) of the tab
        # Rebuild Matrix
        # self.form.set_pane(1, self.matrix)      # matrix defined in TAB_LAYOUT as a method (pane) of the tab

        self.form.refresh_pane(0)
        self.form.refresh_pane(1)

    def _delete_particle(self, pid):
        ids = self.form.pipeline_read("pl.particle_ids") or []
        ids = [x for x in ids if x != pid]
        self.form.pipeline_set("pl.particle_ids", ids)
        self.form.refresh_pane(0)
        self.form.refresh_pane(1)


    def particles(self, parent):
        self._ensure_defaults()

        root = Card(parent, scrollable=True)

        header = CardRow(root, width_flex=True, justify_spread=True)
        Heading(header, "Particles", glow=True)
        Button(header, "Add",
               color_bg=Style.COLOR_PAL_GREEN_DARK,
               on_click=self._add_particle)

        ids = self.form.pipeline_read("pl.particle_ids") or []



        for pid in ids:  self.add_particle(pid,root)

    def add_particle(self,pid,root):
        row = Card(root)



        top = CardRow(row, width_flex=True, justify_spread=True)
        Heading(top, f"Type {pid}")

        Button(top, "Delete",
               color_bg=Style.COLOR_PAL_RED_DARK,
               on_click=lambda pid=pid: self._delete_particle(pid))

        fields = CardRow(row, width_flex=True)

        TextBox(fields, placeholder="Name",
                pipeline_key=f"pl.p.{pid}.name",
                width_flex=2)

        TextBox(fields, placeholder="R",
                pipeline_key=f"pl.p.{pid}.r",
                width_flex=1)

        TextBox(fields, placeholder="G",
                pipeline_key=f"pl.p.{pid}.g",
                width_flex=1)

        TextBox(fields, placeholder="B",
                pipeline_key=f"pl.p.{pid}.b",
                width_flex=1)

        TextBox(fields, placeholder="Count",
                pipeline_key=f"pl.p.{pid}.count",
                width_flex=1)


    # ===========================================
    # End of paritcles - matrix below
    # ===========================================





    # -------------------------
    # Matrix helpers
    # -------------------------
    def _g_key(self, a, b):
        return f"pl.G.{a}.{b}"

    def _ensure_matrix_defaults(self, ids):
        # Ensure every cell exists so TextBoxes can populate deterministically
        for a in ids:
            for b in ids:
                k = self._g_key(a, b)
                if self.form.pipeline_read(k) is None:
                    self.form.pipeline_set(k, 0.0)

    def _matrix_zero(self):
        ids = self.form.pipeline_read("pl.particle_ids") or []
        for a in ids:
            for b in ids:
                self.form.pipeline_set(self._g_key(a, b), 0.0)
        self.form.set_pane(1,  self.matrix)

    def _matrix_invert(self):
        ids = self.form.pipeline_read("pl.particle_ids") or []
        for a in ids:
            for b in ids:
                k = self._g_key(a, b)
                v = self.form.pipeline_read(k)
                if v is None:
                    v = 0.0
                self.form.pipeline_set(k, -float(v))
        self.form.set_pane(1, self.matrix)

    def _matrix_random(self):
        ids = self.form.pipeline_read("pl.particle_ids") or []
        for a in ids:
            for b in ids:
                # keep it readable for humans
                self.form.pipeline_set(self._g_key(a, b), round(random.uniform(-1.0, 1.0), 2))
        self.form.set_pane(1, self.matrix)

    def _matrix_symmetrize(self):
        ids = self.form.pipeline_read("pl.particle_ids") or []
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a = ids[i]
                b = ids[j]
                v = self.form.pipeline_read(self._g_key(a, b))
                if v is None:
                    v = 0.0
                self.form.pipeline_set(self._g_key(b, a), float(v))
        self.form.set_pane(1,  self.matrix)

    def _preset_loop(self):
        """
        Cyclic ecosystem:
          each type strongly attracted to the next type,
          mildly repelled by itself,
          mildly repelled by others.
        """
        ids = self.form.pipeline_read("pl.particle_ids") or []
        n = len(ids)
        if n < 2:
            return

        # baseline
        for a in ids:
            for b in ids:
                self.form.pipeline_set(self._g_key(a, b), -0.3)

        # self
        for a in ids:
            self.form.pipeline_set(self._g_key(a, a), -0.2)

        # chase next
        for i, a in enumerate(ids):
            b = ids[(i + 1) % n]
            self.form.pipeline_set(self._g_key(a, b), 0.8)

        self.form.set_pane(1,  self.matrix)

    # -------------------------
    # Matrix pane
    # -------------------------
    def matrix(self, parent):
        root = CardCol(parent, scrollable=True)

        # Header + buttons
        header = CardRow(root, width_flex=True, justify_spread=True)
        Heading(header, "Interaction Matrix", glow=True)

        btns = CardRow(header)
        Button(btns, "Zero",       on_click=self._matrix_zero)
        Button(btns, "Random",     on_click=self._matrix_random)
        Button(btns, "Invert",     on_click=self._matrix_invert)
        Button(btns, "Symmetrize", on_click=self._matrix_symmetrize)
        Button(btns, "Preset: Loop", color_bg=Style.COLOR_PAL_GREEN_DARK, on_click=self._preset_loop)

        Body(root, "Row reacts to column:  G[row][col]  in [-1, +1]")

        ids = self.form.pipeline_read("pl.particle_ids") or []
        self._ensure_matrix_defaults(ids)

        # Grid container card
        grid = Card(root)

        # Column headers
        top = CardRow(grid, width_flex=True)
        Body(top, "")  # top-left corner spacer (row labels column)
        for col_id in ids:
            Body(top, col_id)

        # Rows
        for row_id in ids:
            r = CardRow(grid, width_flex=True)

            # Row label
            Body(r, row_id)

            # Cells
            for col_id in ids:
                TextBox(
                    r,
                    pipeline_key=self._g_key(row_id, col_id),
                    width_flex=1
                )