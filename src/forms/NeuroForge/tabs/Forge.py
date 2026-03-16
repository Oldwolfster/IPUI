# Workbench.py  NEW FILE  (replaces frmArchitecture.py — _basePane migration)

from ipui.Style              import Style
from ipui.engine._BasePane import _basePane
from ipui.widgets.Button     import Button
from ipui.widgets.Row        import Row, CardCol
from ipui.widgets.Spacer     import Spacer
from ipui.widgets.Label       import Title, Heading, Body
from ipui.widgets.NetworkDiagram import NetworkDiagram


PERCY_STORY = (
    "Imagine you have a tiny robot friend named Percy.",
    "Percy has one job — look at something and say YES or NO.",
    "That's it. One neuron. One decision.",
    "",
    "Percy is really good at his job.",
    "If you draw a line on the ground and ask",
    "'is the ball on the left or the right?'",
    "Percy nails it. Every. Single. Time.",
    "Not 99%. Not close enough. Perfect.",
    "",
    "Now some people came along and said",
    "'Percy is useless because he can't solve hard puzzles.'",
    "And they were so loud that everyone stopped",
    "talking to Percy for TWENTY YEARS.",
    "",
    "But here's the thing —",
    "Percy never claimed to solve hard puzzles.",
    "He just draws a line and tells you which side you're on.",
    "And at that job, nobody beats him.",
)


class EZ_Pane(_basePane):
    """Workbench tab — architecture builder with Percy educational content."""

    # ══════════════════════════════════════════════════════════════
    # TAB PANES  (names must match strings in FormNeuroForge.tab_data)
    # ══════════════════════════════════════════════════════════════

    def info(self, parent) -> None:
        """Left pane — Percy intro, educational cards, and navigation."""
        self.card_powerful(parent)
        self.card_learn_more(parent)
        self.card_weight(parent)
        self.card_bias(parent)
        self.card_percy_btn(parent)

    def workbench(self, parent) -> None:
        """Middle pane — layer/neuron editing widgets and saved list."""
        Title(parent, "Workbench", glow=True)

        sub     = CardCol(parent)
        Heading(sub, "Current Design:")
        layers  = self.get_workbench()
        Body(sub, self.format_layers(layers), name="lbl_workbench")

        sub = CardCol(parent)
        Heading(sub, "Layer:")
        row = Row(sub)
        btn_add_layer = Button(row, "Add Layer", color_bg=Style.COLOR_PAL_GREEN_SECOND)
        btn_add_layer.on_click_me(self.add_layer)
        btn_rem_layer = Button(row, "Remove Layer", color_bg=Style.COLOR_PAL_RED_DARK)
        btn_rem_layer.on_click_me(self.remove_layer)

        sub = CardCol(parent)
        Heading(sub, "Neurons:")
        row = Row(sub)
        btn_add_neuron = Button(row, "Add Neuron", color_bg=Style.COLOR_PAL_GREEN_SECOND)
        btn_add_neuron.on_click_me(self.add_neuron)
        btn_rem_neuron = Button(row, "Remove Neuron", color_bg=Style.COLOR_PAL_RED_DARK)
        btn_rem_neuron.on_click_me(self.remove_neuron)

        self.card_saved(parent)

    def preview(self, parent) -> None:
        """Right pane — live network diagram with forge/clear widgets."""
        header = Row(parent, justify_spread=True)
        Title(header, "Neuron Layout", glow=True)  # NEW
        Spacer(header)
        btn_clear = Button(header, "Clear", color_bg=Style.COLOR_TAB_BG)  # NEW
        btn_forge = Button(header, "Forge It!", color_bg=Style.COLOR_PAL_GREEN_DARK)  # NEW
        btn_clear.on_click_me(self.clear_workbench)
        btn_forge.on_click_me(self.save_architecture)

        layers  = self.get_workbench()
        diagram = NetworkDiagram(parent,
            width_flex  = True,
            height_flex = True,
            name        = "net_diagram",
        )
        diagram.on_layer_selected = lambda idx: self.on_layer_clicked(idx)  # TODO: NIP — NetworkDiagram callback
        diagram.set_layers(layers)
        sel = getattr(self.form, 'workbench_selected', 0)
        diagram.set_selected(sel)

    # ══════════════════════════════════════════════════════════════
    # INFO CARDS
    # ══════════════════════════════════════════════════════════════

    def card_powerful(self, parent) -> None:
        """Percy is Powerful — intro card with 'Understand the Power' button."""
        sub = CardCol(parent)
        row = Row(sub, justify_spread=True)
        col = CardCol(row)
        Title(col, "Percy is Powerful.", glow=True)
        Body(col, "Not despite being simple.")
        Heading(col, "Because of it.", glow=True)

        btn = Button(row, "Understand\nthe\nPower", color_bg=Style.COLOR_TAB_BG)
        btn.set_radiate()
        btn.on_click_me(self.swap_pane(0, self.pane_power))

    def card_weight(self, parent) -> None:
        """Weight explanation card."""
        sub = CardCol(parent)
        Body(sub, "For some rare problems Percy is")
        Body(sub, "just a number")
        Body(sub, "called a weight")
        Heading(sub, "STILL PERFECT", glow=True)

    def card_bias(self, parent) -> None:
        """Bias explanation card."""
        sub = CardCol(parent)
        Body(sub, "Add a 2nd number (Bias).")
        Body(sub, "Solve many more")
        Body(sub, "with a 2nd parameter")
        Heading(sub, "ALWAYS PERFECT", glow=True)

    def card_learn_more(self, parent) -> None:
        """Dropdown with lesson topics (coming soon)."""
        from ipui.widgets.DropDown import DropDown

        LESSONS = {
            "What is a Perceptron?":          {"short_desc": "The single neuron that started it all"},
            "Weights: Percy's Knobs":         {"short_desc": "How inputs get amplified or muted"},
            "Bias: Percy's Confidence":       {"short_desc": "The threshold that shifts the decision boundary"},
            "Activation: The Decision Maker": {"short_desc": "How Percy says YES or NO"},
            "The Learning Rule":              {"short_desc": "How Percy adjusts after mistakes"},
            "Linear Separability":            {"short_desc": "What Percy can and cannot solve"},
            "The XOR Problem":                {"short_desc": "The puzzle that silenced Percy for 20 years"},
            "Convergence Theorem":            {"short_desc": "The proof that Percy always finds the answer"},
            "From One to Many":               {"short_desc": "How Percys compose into deep networks"},
            "Percy vs Regression":            {"short_desc": "When a line is all you need"},
        }

        sub = CardCol(parent)
        DropDown(sub,
            placeholder = "Learn More...",
            data        = LESSONS,
            on_change   = lambda sel: self.form.show_modal(  # TODO: NIP — DropDown callback
                f"Coming Soon:    {sel[0]}", lambda: None, 1
            ) if sel else None,
        )

    def card_percy_btn(self, parent) -> None:
        """Button to navigate to Percy's Story pane."""
        sub = CardCol(parent)
        btn = Button(sub, "Percy's Story", color_bg=Style.COLOR_PAL_GREEN_SECOND)
        btn.on_click_me(self.swap_pane(0, self.pane_percy))

    def card_saved(self, parent) -> None:
        """Display saved architecture configurations."""
        sub   = CardCol(parent, height_flex=True, scrollable=True)
        Heading(sub, "Saved Architectures:")
        saved = self.form.pipeline_read("NeuronLayersList") or []
        text  = self.format_saved_list(saved)
        Body(sub, text, name="lbl_saved_architectures")

    # ══════════════════════════════════════════════════════════════
    # SUB-PANES (behind Back buttons)
    # ══════════════════════════════════════════════════════════════

    def pane_power(self, parent) -> None:
        """Understand the Power — sub-pane with Back navigation."""
        header = Row(parent, justify_spread=True)
        Title(header, "The Power", glow=True)
        btn = Button(header, "Back", color_bg=Style.COLOR_TAB_BG)
        btn.on_click_me(self.swap_pane(0, self.info))

        self.card_perfect(parent)
        self.card_transparent(parent)
        self.card_lego(parent)

    def card_perfect(self, parent) -> None:
        """True to his word card."""
        sub = CardCol(parent)
        Title(sub, "True to his word.", glow=True)
        Body(sub, "IF Percy says he can solve it.")
        Heading(sub, "Perfect. Always. Everytime.", glow=True)
        Body(sub, "Just can't do every thing.")
        Body(sub, "Who can?")

    def card_transparent(self, parent) -> None:
        """Spotlight / transparency card."""
        sub = CardCol(parent)
        Heading(sub, "A SPOTLIGHT.", glow=True)
        Body(sub, "One neuron means nothing is hidden.")
        Body(sub, "Watch exactly what learning rate,\nmomentum, and config actually does.")
        Body(sub, "Watch Percy learn.\nPowerful yet simple to understand.")

    def card_lego(self, parent) -> None:
        """LEGO metaphor card."""
        sub = CardCol(parent)
        Heading(sub, "Percy is like a LEGO.", glow=True)
        Body(sub, "Nobody trashes bricks because\none brick can't be a skyscraper.")
        Body(sub, "You appreciate what it is.")
        Body(sub, "Then you compose them\ninto bigger things.")
        Body(sub, "Every giant neural network\nis just a building made of Percys.")

    def pane_percy(self, parent) -> None:
        """Percy's Story — sub-pane with Back navigation."""
        header = Row(parent, justify_spread=True)
        Title(header, "Percy's Story", glow=True)
        btn = Button(header, "Back", color_bg=Style.COLOR_TAB_BG)
        btn.on_click_me(self.swap_pane(0, self.info))
        sub = CardCol(parent, height_flex=True, scrollable=True)
        Body(sub, PERCY_STORY)

    # ══════════════════════════════════════════════════════════════
    # STATE HELPERS
    # ══════════════════════════════════════════════════════════════

    def get_workbench(self) -> list:
        """Return current workbench layers, initializing if needed."""
        if not hasattr(self.form, 'workbench_layers'):
            self.form.workbench_layers = [1]
        return self.form.workbench_layers

    def get_selected(self) -> int:
        """Return clamped selected layer index."""
        layers = self.get_workbench()
        sel    = getattr(self.form, 'workbench_selected', 0)
        if not layers:
            return -1
        return max(0, min(sel, len(layers) - 1))

    # ══════════════════════════════════════════════════════════════
    # ACTIONS
    # ══════════════════════════════════════════════════════════════

    def on_layer_clicked(self, index: int) -> None:
        """Handle click on a layer in the network diagram."""
        self.form.workbench_selected = index
        self.refresh()

    def add_layer(self) -> None:
        """Insert a new layer at the selected position."""
        layers = self.get_workbench()
        sel    = self.get_selected()
        count  = layers[sel] if layers else 4
        insert = sel if layers else 0
        layers.insert(insert, count)
        self.form.workbench_selected = insert
        self.refresh()

    def remove_layer(self) -> None:
        """Remove the selected layer (minimum 1 layer)."""
        layers = self.get_workbench()
        if len(layers) <= 1:
            return
        sel = self.get_selected()
        layers.pop(sel)
        self.form.workbench_selected = min(sel, len(layers) - 1)
        self.refresh()

    def add_neuron(self) -> None:
        """Add a neuron to the selected layer."""
        layers = self.get_workbench()
        sel    = self.get_selected()
        if sel >= 0:
            layers[sel] += 1
        self.refresh()

    def remove_neuron(self) -> None:
        """Remove a neuron from the selected layer (minimum 1)."""
        layers = self.get_workbench()
        sel    = self.get_selected()
        if sel >= 0 and layers[sel] > 1:
            layers[sel] -= 1
        self.refresh()

    def save_architecture(self) -> None:
        """Save current workbench layout to the neuron layers list."""
        layers  = list(self.get_workbench())
        current = self.form.pipeline_read("NeuronLayersList") or []
        if layers not in current:
            current.append(layers)
        self.form.pipeline_set("NeuronLayersList", current)
        self.refresh_saved()
        self.form.calc_total_runs()

    def clear_workbench(self) -> None:
        """Reset workbench to single perceptron."""
        self.form.workbench_layers   = [1]
        self.form.workbench_selected = 0
        self.refresh()

    # ══════════════════════════════════════════════════════════════
    # REFRESH
    # ══════════════════════════════════════════════════════════════

    def refresh(self) -> None:
        """Refresh both the label and the diagram."""
        self.form.set_pane(2, self.preview)
        #self.refresh_label()
        #self.refresh_diagram()


    def refresh_saved(self) -> None:
        """Update the saved architectures label."""
        lbl = self.form.widgets.get("lbl_saved_architectures")
        if lbl:
            saved = self.form.pipeline_read("NeuronLayersList") or []
            lbl.set_text(self.format_saved_list(saved))

    # ══════════════════════════════════════════════════════════════
    # FORMATTING
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def format_layers(layers) -> str:
        """Format a layer list for display."""
        if not layers:
            return "(empty)"
        desc = " - ".join(str(n) for n in layers)
        if layers == [1]:
            desc += "  —  Perceptron"
        return desc

    @staticmethod
    def format_saved_list(saved) -> str:
        """Format all saved architectures for display."""
        if not saved:
            return "(none saved yet)"
        return "\n".join(EZ_Pane.format_layers(arch) for arch in saved)

    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

    def swap_pane(self, index: int, builder) -> callable:
        """Return a zero-arg callable that swaps a pane. For use with on_click_me."""
        def do_swap():
            self.form.set_pane(index, builder)
        return do_swap