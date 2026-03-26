# Armory.py  NEW FILE  (replaces frmMatch.py — _basePane migration)
from ipui.popups.TooltipArena import TooltipArena
from ipui.popups.TooltipGladiator import TooltipGladiator


from ipui import *



# ══════════════════════════════════════════════════════════════
# Shared data — populated by load_legos(), read by other tabs
# ══════════════════════════════════════════════════════════════

GLADIATORS         = {}
ARENAS             = {}
OPTIMIZERS         = {}
HIDDEN_ACTIVATIONS = {}
OUTPUT_ACTIVATIONS = {}
LOSS_FUNCTIONS     = {}
INITIALIZERS       = {}
INPUT_SCALERS      = {}
TARGET_SCALERS     = {}

DIMENSION_MAP = {
    "gladiator":          GLADIATORS,
    "arena":              ARENAS,
    "optimizer":          OPTIMIZERS,
    "hidden_activation":  HIDDEN_ACTIVATIONS,
    "output_activation":  OUTPUT_ACTIVATIONS,
    "loss_function":      LOSS_FUNCTIONS,
    "weight_initializer": INITIALIZERS,
    "input_scalers":      INPUT_SCALERS,
    "target_scaler":      TARGET_SCALERS,
}

CONFIG_CATEGORIES = {
    "Optimizer":         {"data": OPTIMIZERS,         "pipeline_key": "OptimizerList"},
    "Hidden Activation": {"data": HIDDEN_ACTIVATIONS, "pipeline_key": "HiddenActivationList"},
    "Output Activation": {"data": OUTPUT_ACTIVATIONS, "pipeline_key": "OutputActivationList"},
    "Loss Function":     {"data": LOSS_FUNCTIONS,     "pipeline_key": "LossFunctionList"},
    "Initializer":       {"data": INITIALIZERS,       "pipeline_key": "InitializerList"},
    "Input Scaler":      {"data": INPUT_SCALERS,      "pipeline_key": "InputScalerList"},
    "Target Scaler":     {"data": TARGET_SCALERS,     "pipeline_key": "TargetScalerList"},
}

HYPERPARAMS = {
    "Epochs to Run":     {"default": 50},
    "Training Set Size": {"default": 40},
    "Learning Rate":     {"default": 0},
}

HYPERPARAMS_LIST = {
    "Batch Size":    {"pipeline_key": "BatchSizeList",    "parse": "int"},
    "Neuron Layers": {"pipeline_key": "NeuronLayersList", "parse": "layers",
                      "hint": "e.g. 8, 4 = two hidden layers (8 neurons then 4).\n"
                              "Each config is a separate experiment.\n"
                              "Add multiple to sweep architectures.\n"
                              "If not specified here Gladiator will set"},
}


class EZ_Pane(_basePane):
    """Armory tab — configure gladiators, arenas, hyperparams, and seeds."""

    def ip_setup_pane(self):
        self.load_legos(self.form.active_project.path)


    # ══════════════════════════════════════════════════════════════
    # TAB PANES  (names must match strings in FormNeuroForge.tab_data)
    # ══════════════════════════════════════════════════════════════

    def match_hints(self, parent):
        """Left pane — orientation tips for new users."""
        Title(parent, "Match Setup", glow=True)

        sub = CardCol(parent)
        Heading(sub, "Hint if New!")
        Body(sub, "You can hit launch right now!")
        Body(sub, "Or tweak any settings you like!")

        sub = CardCol(parent)
        Heading(sub, "Setting Sources:")
        Body(sub, "Config settings come from 3 places.")
        Body(sub, "Your Settings")
        Body(sub, "Base Gladiator")
        Body(sub, "Auto ML Smart-Config")
        Body(sub, "(for anything not specified above)")

    def match_settings(self, parent):
        """Middle pane — clickable summary of all current settings."""
        Title(parent, "Settings", glow=True)
        row = Row(parent, width_flex=True)
        self.build_settings_left(row)
        self.build_settings_right(row)
        self.build_settings_below(parent)

    # ══════════════════════════════════════════════════════════════
    # SETTINGS SUMMARY — left column (hyperparams + seeds)
    # ══════════════════════════════════════════════════════════════

    def build_settings_left(self, parent: Row) -> None:
        """Render left column of settings summary (hyperparams + RNG)."""
        col  = CardCol(parent, width_flex=True)
        form = self.form

        sub = CardCol(col)
        Heading(sub, "Hyperparams:")
        hp_text = "\n".join(
            f"{name}: {form.pipeline_read(f'HP_{name}') or meta['default']}"
            for name, meta in HYPERPARAMS.items()
        )
        Body(sub, hp_text, name="lbl_hyperparams")
        sub.on_click_me(self.swap_pane(2, self.pane_hyperparams_picker))

        sub = CardCol(col)
        Heading(sub, "Seed List:")
        random_count = form.pipeline_read("SeedCountRandom") or 0
        manual_seeds = form.pipeline_read("SeedListManual")  or []
        manual_count = len(manual_seeds)
        total        = random_count + manual_count
        rng_text     = (f"{total} seeds ({random_count} random + {manual_count} manual)"
                        if total else "configure in RNG Settings")
        Body(sub, rng_text, name="lbl_rng")
        sub.on_click_me(self.swap_pane(2, self.pane_rng_picker))

    # ══════════════════════════════════════════════════════════════
    # SETTINGS SUMMARY — right column (gladiators + arena)
    # ══════════════════════════════════════════════════════════════

    def build_settings_right(self, parent: Row) -> None:
        """Render right column of settings summary (gladiators + arena)."""
        col  = CardCol(parent, width_flex=True, height_flex=True)
        form = self.form

        sub = CardCol(col)
        Heading(sub, "Gladiators:")
        selected = form.pipeline_read("GladiatorList")
        text     = "\n".join(sorted(selected)) if selected else "(none selected)"
        Body(sub, text, name="lbl_gladiators")
        sub.on_click_me(self.swap_pane(2, self.pane_gladiator_picker))

        sub = CardCol(col)
        Heading(sub, "Arena:")
        selected = form.pipeline_read("ArenaList")
        text     = "\n".join(sorted(selected)) if selected else "(none selected)"
        Body(sub, text, name="lbl_arena")
        sub.on_click_me(self.swap_pane(2, self.pane_arena_picker))

    # ══════════════════════════════════════════════════════════════
    # SETTINGS SUMMARY — below (config options)
    # ══════════════════════════════════════════════════════════════

    def build_settings_below(self, parent) -> None:
        """Render config options summary beneath the two columns."""
        form = self.form
        sub  = CardCol(parent, height_flex=True)
        Heading(sub, "Config Options:")
        parts = []
        for cat_name, cat_info in CONFIG_CATEGORIES.items():
            vals = form.pipeline_read(cat_info["pipeline_key"]) or []
            if vals:
                parts.append(f"{cat_name}: {', '.join(sorted(vals))}")
        config_text = "\n".join(parts) if parts else "\nClick here to explore\ntiered tooltips\ntry hovering optimizer for 5 seconds\n1st small popup\nthen big pop up\nthe 'Pin' button"
        if parts:
            Body(sub, config_text, name="lbl_config")
        else:
            Title(sub, config_text, name="lbl_config",glow=True)

        sub.on_click_me(self.swap_pane(2, lambda p: self.pane_config_detail(p, "Optimizer")))

    # ══════════════════════════════════════════════════════════════
    # PANE: Gladiator picker
    # ══════════════════════════════════════════════════════════════

    def pane_gladiator_picker(self, parent) -> None:
        """Full pane — multi-select gladiator list."""
        header = Row(parent, justify_spread=True)
        Title(header, "Gladiators", glow=True)
        Body(header, "Count: 0", name="lbl_gladiator_count")
        SelectionList(parent,
            pipeline_key  = "GladiatorList",
            data          = GLADIATORS,
            width_flex    = True,
            height_flex   = True,
            tooltip_class = TooltipGladiator,
            on_change     = lambda selected: self.update_gladiator_summary(selected),  # TODO: NIP — SelectionList callback
        )

    def update_gladiator_summary(self, selected) -> None:
        """Sync gladiator label and count after selection change."""
        form = self.form
        lbl  = form.widgets.get("lbl_gladiators")
        if lbl:
            lbl.set_text("\n".join(sorted(selected)) if selected else "(none selected)")
        lbl = form.widgets.get("lbl_gladiator_count")
        if lbl:
            lbl.set_text(f"Count: {len(selected)}")
        self.calc_total_runs()

    # ══════════════════════════════════════════════════════════════
    # PANE: Arena picker
    # ══════════════════════════════════════════════════════════════

    def pane_arena_picker(self, parent) -> None:
        """Full pane — multi-select arena list with filter."""
        header = Row(parent, justify_spread=True)
        Title(header, "Arenas", glow=True)
        Body(header, "Count: 0", name="lbl_arena_count")
        TextBox(parent,
            placeholder = "Filter list...",
            on_change   = lambda text: sel.set_filter(text),  # TODO: NIP — TextBox callback
        )
        sel = SelectionList(parent,
            pipeline_key  = "ArenaList",
            data          = ARENAS,
            width_flex    = True,
            height_flex   = True,
            tooltip_class = TooltipArena,
            on_change     = lambda selected: self.on_arena_changed(selected),  # TODO: NIP — SelectionList callback
        )

    def on_arena_changed(self, selected) -> None:
        """Sync arena label and count after selection change."""
        form = self.form
        lbl  = form.widgets.get("lbl_arena")
        if lbl:
            lbl.set_text("\n".join(sorted(selected)) if selected else "(none selected)")
        lbl = form.widgets.get("lbl_arena_count")
        if lbl:
            lbl.set_text(f"Count: {len(selected)}")
        self.calc_total_runs()

    # ══════════════════════════════════════════════════════════════
    # PANE: RNG / Seed picker
    # ══════════════════════════════════════════════════════════════

    def pane_rng_picker(self, parent) -> None:
        """Full pane — random + manual seed configuration."""
        Title(parent, "Seed List", glow=True)
        self.rng_info(parent)
        self.rng_data(parent)
        self.rng_foot(parent)

    def rng_info(self, parent) -> None:
        """Explain why seeds matter."""
        sub = CardCol(parent)
        Heading(sub, "Why Seeds Matter:")
        Body(sub, "Every Gladiator/Arena combo runs the\nEXACT same seed list.")
        Body(sub, "Same seeds = same results. Every time.")
        Body(sub, "This is what makes results repeatable\nand comparisons meaningful.")

    def rng_data(self, parent) -> None:
        """Random count + manual seed entry fields."""
        form = self.form
        row  = Row(parent, width_flex=True)

        sub = CardCol(row, width_flex=2)
        Heading(sub, "Random Seeds:")
        TextBox(sub,
            placeholder   = "Count...",
            initial_value = str(form.pipeline_read("SeedCountRandom") or 0),
            name          = "txt_seed_count",
            on_submit     = lambda val: self.on_seed_count_changed(val),  # TODO: NIP — TextBox callback
        )

        sub         = CardCol(row, width_flex=3)
        row_manual  = Row(sub)
        Heading(row_manual, "Manual Seeds:")
        Spacer(row_manual)
        btn_paste = Button(row_manual, "Paste", color_bg=Style.COLOR_TAB_BG)
        btn_paste.on_click_me(self.on_paste_seeds)
        btn_clear = Button(row_manual, "Clear", color_bg=Style.COLOR_PAL_RED_DARK)
        btn_clear.on_click_me(self.clear_manual_seeds)
        TextBox(sub,
            placeholder = "Enter seed(s)...",
            name        = "txt_manual_seed",
            on_submit   = lambda val: self.on_manual_seed_added(val),  # TODO: NIP — TextBox callback
        )

    def rng_foot(self, parent) -> None:
        """Display current manual seed list."""
        sub   = CardCol(parent)
        Heading(sub, "Manual Seeds:")
        seeds     = self.form.pipeline_read("SeedListManual") or []
        seed_text = ", ".join(str(s) for s in seeds) if seeds else "(no manual seeds)"
        Body(sub, seed_text, name="lbl_manual_seeds")

    def on_seed_count_changed(self, val: str) -> None:
        """Handle random seed count submission."""
        try:
            count = max(0, int(val))
            self.form.pipeline_set("SeedCountRandom", count)
            self.update_rng_summary()
            self.calc_total_runs()
        except ValueError:
            pass

    def on_manual_seed_added(self, val: str) -> None:
        """Parse and append manual seeds from text input."""
        new_seeds = parse_int_list(val)
        if not new_seeds:
            return
        seeds = self.form.pipeline_read("SeedListManual") or []
        for s in new_seeds:
            if s not in seeds:
                seeds.append(s)
        self.form.pipeline_set("SeedListManual", seeds)
        self.update_manual_seed_label()
        self.update_rng_summary()
        self.calc_total_runs()

    def clear_manual_seeds(self) -> None:
        """Clear all manual seeds."""
        self.form.pipeline_set("SeedListManual", [])
        self.update_manual_seed_label()
        self.update_rng_summary()
        self.calc_total_runs()

    def on_paste_seeds(self) -> None:
        """Paste seeds from clipboard."""
        import pygame
        try:
            raw = pygame.scrap.get(pygame.SCRAP_TEXT)
            if not raw:
                return
            text = raw.decode("utf-8", errors="ignore").rstrip("\x00")
        except Exception:
            return
        self.on_manual_seed_added(text)

    def update_manual_seed_label(self) -> None:
        """Refresh the manual seeds display label."""
        lbl = self.form.widgets.get("lbl_manual_seeds")
        if not lbl:
            return
        seeds = self.form.pipeline_read("SeedListManual") or []
        lbl.set_text(", ".join(str(s) for s in seeds) if seeds else "(no manual seeds)")

    def update_rng_summary(self) -> None:
        """Refresh the RNG summary label on the settings pane."""
        lbl = self.form.widgets.get("lbl_rng")
        if not lbl:
            return
        random_count = self.form.pipeline_read("SeedCountRandom") or 0
        manual_count = len(self.form.pipeline_read("SeedListManual") or [])
        total        = random_count + manual_count
        lbl.set_text(f"{total} seeds ({random_count} random + {manual_count} manual)")

    # ══════════════════════════════════════════════════════════════
    # PANE: Config detail (optimizer, activation, loss, etc.)
    # ══════════════════════════════════════════════════════════════

    # Armory.py method: pane_config_detail  Update: named widgets, zero-arg callback
    def pane_config_detail(self, parent, category_name: str = "Optimizer") -> None:
        """Full pane — category selector + item multi-select."""
        Title(parent, "Config Options", glow=True)
        row = Row(parent, width_flex=True, height_flex=True)
        print(f"pane_config_detail GLADIATORS id: {id(GLADIATORS)}, count: {len(GLADIATORS)}")
        cat_dict = {name: {} for name in CONFIG_CATEGORIES}
        SelectionList(row,
                      name="sel_config_categories",
                      text="Setting:",
                      data=cat_dict,
                      single_select=True,
                      height_flex=True,
                      on_change=lambda selected: self.on_config_cat_changed(),  # TODO: NIP — SelectionList callback
                      )
        self.preselect_category(category_name)

        col_right = CardCol(row, width_flex=True, height_flex=True)
        cat = CONFIG_CATEGORIES[category_name]
        print(f"DETAIL: {category_name} has {len(cat['data'])} items")
        SelectionList(col_right,
                      name="sel_config_items",
                      pipeline_key=cat["pipeline_key"],
                      data=cat["data"],
                      width_flex=True,
                      height_flex=True,
                      tooltip_class=TooltipGladiator,
                      on_change=lambda selected: self.update_config_summary(),  # TODO: NIP — SelectionList callback
                      )


    # Armory.py method: on_config_cat_changed  Update: zero-arg, reads from widgets
    def on_config_cat_changed(self) -> None:
        """Switch config detail pane to newly selected category."""

        sel = self.form.widgets.get("sel_config_categories")
        print(f"In config cat changed - sel {sel}")
        selected = sel.get_selected() if sel else []
        print(f"In config cat changed - sel {selected}")
        if selected:
            self.form.set_pane(2, lambda p, c=selected[0]: self.pane_config_detail(p, c))

    # Armory.py method: preselect_category  Update: reads from widgets instead of param
    def preselect_category(self, category_name: str) -> None:
        """Pre-highlight the active category in the category list."""
        sel = self.form.widgets.get("sel_config_categories")
        if not sel:
            return
        for item in sel.items:
            if item.text == category_name:
                item.is_selected = True
                item.apply_selection_visual()

    def update_config_summary(self) -> None:
        """Refresh the config summary label on the settings pane."""
        lbl = self.form.widgets.get("lbl_config")
        if not lbl:
            return
        parts = []
        for cat_name, cat_info in CONFIG_CATEGORIES.items():
            vals = self.form.pipeline_read(cat_info["pipeline_key"]) or []
            if vals:
                parts.append(f"{cat_name}: {', '.join(sorted(vals))}")
        lbl.set_text("\n".join(parts) if parts else "(none configured)")
        self.calc_total_runs()

    # ══════════════════════════════════════════════════════════════
    # PANE: Hyperparams picker
    # ══════════════════════════════════════════════════════════════

    def pane_hyperparams_picker(self, parent) -> None:
        """Full pane — edit hyperparams + list-type hyperparams."""
        Title(parent, "Hyperparams", glow=True)
        card = CardCol(parent)

        for name, meta in HYPERPARAMS.items():
            row = Row(card)
            Body(row, name)
            Spacer(row)
            TextBox(row,
                placeholder   = str(meta["default"]),
                initial_value = str(self.form.pipeline_read(f"HP_{name}") or meta["default"]),
                pipeline_key  = f"HP_{name}",
                on_submit     = lambda val, n=name: self.update_hyperparam_summary(),  # TODO: NIP — TextBox callback
            )

        for name, meta in HYPERPARAMS_LIST.items():
            self.build_list_hyperparam(parent, name, meta)

    def build_list_hyperparam(self, parent, name: str, meta: dict) -> None:
        """Build a single list-type hyperparam section (e.g. Batch Size, Neuron Layers)."""
        Spacer(parent)
        sub        = CardCol(parent)
        header_row = Row(sub, justify_spread=True)
        Heading(header_row, f"{name}:")
        Spacer(header_row)

        btn_paste = Button(header_row, "Paste", color_bg=Style.COLOR_TAB_BG)
        btn_paste.on_click_me(lambda: self.on_hplist_paste(name, meta))  # TODO: NIP — needs args

        btn_clear = Button(header_row, "Clear", color_bg=Style.COLOR_PAL_RED_DARK)
        btn_clear.on_click_me(lambda: self.on_hplist_clear(name, meta))  # TODO: NIP — needs args

        txt_name = f"txt_hplist_{name.replace(' ', '_')}"
        lbl_name = f"lbl_hplist_{name.replace(' ', '_')}"

        TextBox(sub,
            placeholder = f"Add {name}...",
            name        = txt_name,
            on_submit   = lambda val, n=name, m=meta: self.on_hplist_add(n, m, val),  # TODO: NIP — TextBox callback
        )

        if meta.get("hint"):
            Body(sub, meta["hint"])

        current = self.form.pipeline_read(meta["pipeline_key"]) or []
        Body(sub, self.format_hplist(current, meta["parse"]), name=lbl_name)

    def on_hplist_add(self, name: str, meta: dict, val: str) -> None:
        """Parse and append a list-hyperparam entry."""
        parsed = self.parse_hplist_entry(val, meta["parse"])
        if parsed is None:
            return
        current = self.form.pipeline_read(meta["pipeline_key"]) or []
        if parsed not in current:
            current.append(parsed)
        self.form.pipeline_set(meta["pipeline_key"], current)
        self.refresh_hplist_label(name, meta)
        self.update_hyperparam_summary()
        self.calc_total_runs()

    def on_hplist_paste(self, name: str, meta: dict) -> None:
        """Paste a list-hyperparam entry from clipboard."""
        import pygame
        try:
            raw = pygame.scrap.get(pygame.SCRAP_TEXT)
            if not raw:
                return
            text = raw.decode("utf-8", errors="ignore").rstrip("\x00")
        except Exception:
            return
        self.on_hplist_add(name, meta, text)

    def on_hplist_clear(self, name: str, meta: dict) -> None:
        """Clear all entries for a list-type hyperparam."""
        self.form.pipeline_set(meta["pipeline_key"], [])
        self.refresh_hplist_label(name, meta)
        self.update_hyperparam_summary()
        self.calc_total_runs()

    def refresh_hplist_label(self, name: str, meta: dict) -> None:
        """Refresh display label for a list-type hyperparam."""
        lbl_name = f"lbl_hplist_{name.replace(' ', '_')}"
        lbl      = self.form.widgets.get(lbl_name)
        if not lbl:
            return
        current = self.form.pipeline_read(meta["pipeline_key"]) or []
        lbl.set_text(self.format_hplist(current, meta["parse"]))

    def update_hyperparam_summary(self) -> None:
        """Refresh the hyperparams summary label on the settings pane."""
        lbl = self.form.widgets.get("lbl_hyperparams")
        if not lbl:
            return
        parts = [f"{name}: {self.form.pipeline_read(f'HP_{name}') or meta['default']}"
                 for name, meta in HYPERPARAMS.items()]
        for name, meta in HYPERPARAMS_LIST.items():
            current = self.form.pipeline_read(meta["pipeline_key"]) or []
            if current:
                parts.append(f"{name}: {self.format_hplist(current, meta['parse'])}")
        lbl.set_text("\n".join(parts))

    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

    def swap_pane(self, index: int, builder) -> callable:
        """Return a zero-arg callable that swaps a pane. For use with on_click_me."""
        def do_swap():
            self.form.set_pane(index, builder)
        return do_swap

    @staticmethod
    def parse_hplist_entry(val: str, parse_type: str):
        """Parse a raw string into a typed hyperparam value."""
        try:
            if parse_type == "int":
                return int(val.strip())
            if parse_type == "layers":
                return [int(x) for x in val.strip().split(",") if x.strip()]
        except (ValueError, AttributeError):
            return None
        return None

    @staticmethod
    def format_hplist(items: list, parse_type: str) -> str:
        """Format a list-hyperparam for display."""
        if not items:
            return "(none)"
        if parse_type == "int":
            return ", ".join(str(x) for x in items)
        if parse_type == "layers":
            return ", ".join("-".join(str(n) for n in layer) for layer in items)
        return str(items)

    # ══════════════════════════════════════════════════════════════
    # CALCULATIONS — called from other tabs too
    # ══════════════════════════════════════════════════════════════

    def calc_total_runs(self) -> int:
        """Compute total run count and update launch button."""
        form       = self.form
        gladiators = len(form.pipeline_read("GladiatorList")  or [])
        arenas     = len(form.pipeline_read("ArenaList")      or [])
        seeds      = ((form.pipeline_read("SeedCountRandom")  or 0)
                      + len(form.pipeline_read("SeedListManual") or []))
        total      = max(1, gladiators) * max(1, arenas) * max(1, seeds)

        for cat_name, cat_info in CONFIG_CATEGORIES.items():
            count = len(form.pipeline_read(cat_info["pipeline_key"]) or [])
            if count > 1:
                total *= count

        for name, meta in HYPERPARAMS_LIST.items():
            count = len(form.pipeline_read(meta["pipeline_key"]) or [])
            if count > 1:
                total *= count

        btn = form.widgets["btnLaunch"]
        if btn:
            btn.set_text(f"   Launch   \n({total} runs)")
        return total

    # ══════════════════════════════════════════════════════════════
    # DATA LOADING — called from FormNeuroForge
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def load_legos(db_path) -> None:
        """Load gladiator/arena/config legos from project database."""
        import sqlite3
        print("in Armory load legos")
        print(f"LOAD LEGO GLADIATORS id: {id(GLADIATORS)}, count: {len(GLADIATORS)}")
        for d in DIMENSION_MAP.values():
            d.clear()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT name, dimensions, desc, when_to_use, best_for, code FROM lego"
        ).fetchall()
        conn.close()
        print(f"LOAD LEGOS: {len(rows)} rows from {db_path}")
        for row in rows:
            entry = {
                "desc":       EZ_Pane.format_tooltip_desc(row),
                "short_desc": (row["desc"] or "").strip(),
                "code":       (row["code"] or "").strip(),
            }
            for dim in row["dimensions"].split(","):
                dim    = dim.strip()
                target = DIMENSION_MAP.get(dim)
                if target is not None:
                    target[row["name"]] = entry

    @staticmethod
    def format_tooltip_desc(row) -> str:
        """Build multi-section tooltip text from a lego row."""
        parts = []
        if (row["desc"]        or "").strip():  parts.append(row["desc"].strip())
        if (row["when_to_use"] or "").strip():  parts.append(f"When To Use: {row['when_to_use'].strip()}")
        if (row["best_for"]    or "").strip():  parts.append(f"Best For: {row['best_for'].strip()}")
        return "\n\n".join(parts) if parts else "(no description)"