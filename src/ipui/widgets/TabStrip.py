# TabStrip.py  Update: lazy pane discovery from string-based data dict
from ipui.widgets.Row import Col
from ipui.widgets.Spacer import Spacer
import importlib.util
import inspect
from pathlib import Path
from ipui.widgets.Row import Row
from ipui.Style import Style
from ipui.engine.MgrColor import MgrColor
from ipui.engine._BasePane import _basePane
from ipui.engine._BaseWidget import _BaseWidget
from ipui.utils.EZ import EZ
from ipui.widgets.Button import Button
from ipui.widgets.Pane import Pane
from ipui.widgets.Row import CardCol, CardRow
from ipui.widgets.TabArea import TabArea
from ipui.widgets.Label import Title, Body
from ipui.widgets.Button import Button
from pathlib import Path
import inspect
from ipui.widgets.TabArea import TabArea


class TabStrip(_BaseWidget):
    """
    desc:        String-based tab manager. Auto-discovers _basePane files, lazy-loads on first visit, caches everything.
    when_to_use: Any multi-view interface. Define tabs as a dict, drop matching .py files, done.
    best_for:    The entire app navigation. One dict = single source of truth.
    example:     TabStrip(parent, data={"Home": ["welcome", "details"], "Log": ["log"]})
    api:         switch_tab(name), hide_tab(name), show_tab(name), set_pane(tab, idx, builder), get_tab(name), prepare(name)
    note:        When using _BaseForm with TAB_LAYOUT, all api methods are available directly on the form.
    """
    def build(self):
        self.width_flex  = 1
        self.height_flex = 1
        self.active_tab  = None
        self.pane_cache  = {}
        self.tab_layout  = {}
        self.clean_tab_layout_once()
        self.build_tab_buttons()
        for name in (self.early_load or []):  # Maybe below contenyt
            self.prepare(name)
        self.build_content_area()
        self.switch_tab(next(iter(self.tab_layout)))

    def clean_tab_layout_once(self):
        """do any cleaning needed for tab_layout - should end with each value is a list of tuple(s) aka [("pane",1)]"""
        self.clean_tab_layout_ensure_list()
        self.clean_tab_layout_add_default_flex()

    def clean_tab_layout_ensure_list(self):
        """Ensure every value in dict is a list. this gives flexibility that single pane - not in list wont cause an error"""
        for key, val in self.data.items():
            if not isinstance(val, list): self.data[key] = [val]

    def clean_tab_layout_add_default_flex(self):
        """Normalize mixed format: builder or (builder, weight) -> [(builder, weight)]"""
        for key, entries in self.data.items():
            one_tab = []
            for entry in entries:
                if isinstance(entry, tuple): one_tab.append(entry)
                else                       : one_tab.append((entry, 1))
            self.tab_layout[key] = one_tab

    # ============================================================
    # Build
    # ============================================================
    def build_tab_buttons(self):
        outer          = CardRow(self, pad=2)
        self.tab_row   = CardRow(outer, width_flex=True)

    def build_content_area(self):
        self.content = Row(self, width_flex=True, height_flex=True)
        self.panes   = []
        self.rebuild_tab_buttons()

    def rebuild_tab_buttons(self):
        self.tab_row.children.clear()
        for tab_name in self.data:
            btn          = Button(self.tab_row, tab_name, color_bg=Style.COLOR_TAB_BG, width_flex=True,border_radius=0)
            btn.on_click = lambda name=tab_name: self.switch_tab(name)


    def prepare(self, name):
        """Resolve, cache, and initialize a tab's _basePane on demand."""
        if name not in self.pane_cache:  self.resolve_pane(name)
        return self.pane_cache[name]

    # ============================================================
    # Switching
    # ============================================================

    def switch_tab(self, name):
        if self.on_change:
            if self.on_change(name, self.active_tab) is False:
                return
        self.active_tab = name
        self.update_button_visuals()
        entries = self.tab_layout[name]
        if self.needs_missing_page(name, entries):
            entries = self.missing_tab_entries(name)
        self.rebuild_tab_areas(entries)
        self.fill_panes(name, entries)

    def needs_missing_page(self, name, entries):
        if self.resolve_pane(name) is not None:
            return False
        return any(
            isinstance(b, str) and "." not in b
            for b, w in entries if b is not None
        )

    def update_button_visuals(self):
        for btn in self.tab_row.children:
            if btn.text == self.active_tab:
                MgrColor.apply_bevel(btn, "sunken")
                btn.show_glow = True
            else:
                MgrColor.apply_bevel(btn, "raised")
                btn.show_glow = False


    def rebuild_tab_areas(self, pane_list):

        self.content.children.clear()
        #pane_list        = self.tab_layout[name]
        self.panes       = [None] * len(pane_list)
        current_area     = None

        for i, entry in enumerate(pane_list):
            builder, weight = entry[0], entry[1]
            if builder is None:
                #Col(self.content, width_flex=weight, height_flex=True)
                current_area = None
                pane = Pane(self.content, width_flex=weight, height_flex=True)
                pane.color_bg  = None
                pane.border_top = None
                self.panes[i]  = pane
            else:
                if current_area is None:  current_area = TabArea(self.content, width_flex=0, height_flex=True)
                current_area.width_flex += weight
                pane = Pane(current_area.inner, width_flex=weight, height_flex=True)
                self.panes[i] = pane



    def fill_panes(self, name, pane_list):
        for i, entry in enumerate(pane_list):
            builder = entry[0]
            args    = entry[2] if len(entry) > 2 else ()
            kwargs  = entry[3] if len(entry) > 3 else {}
            if builder is not None:
                self.invoke_builder(name, builder, self.panes[i], *args, **kwargs)

    def rebuild_pane_content(self, name):
        entries = self.parse_builders(self.tab_layout.get(name, []))
        if self.resolve_pane(name) is None:
            needs_local = any(
                isinstance(e[0], str) and "." not in e[0]
                for e in entries if e[0] is not None
            )
            if needs_local:
                entries = self.parse_builders(self.missing_tab_entries(name))
                self.ensure_pane_count(len(entries))

        for i, pane in enumerate(self.panes):
            pane.children.clear()
            if i < len(entries):
                builder, weight  = entries[i]
                pane.visible     = True
                pane.width_flex  = weight
                if builder:
                    self.invoke_builder(name, builder, pane)
            else:
                pane.visible = False
        #self.form.pipeline.fire_all() #Initialize Reactive components

    def missing_tab_entries(self, tab_name):
        from ipui.engine.MissingTabUI import MissingTabUI
        self.form.pipeline_set("missing_tab_name", tab_name)
        methods = [e[0] if isinstance(e, tuple) else e for e in self.tab_layout[tab_name]]
        self.form.pipeline_set("missing_tab_methods", methods)
        form_dir = Path(inspect.getfile(self.form.__class__)).parent  # NEW
        self.form.pipeline_set("missing_tab_path", str(form_dir / (tab_name + ".py")))
        self.pane_cache["__missing__"] = MissingTabUI(self.form)
        return [("__missing__.pitch", 2), ("__missing__.choices",1)]

    def ensure_pane_count(self, needed):
        while len(self.panes) < needed:
            pane = CardCol(self.content, width_flex=True, height_flex=True)
            self.panes.append(pane)



    def invoke_builder(self, tab_name, builder, pane, *args, **kwargs):
        """Call a builder: resolves strings lazily, passes callables through."""
        if callable(builder):
            builder(pane, *args, **kwargs)
        elif isinstance(builder, str):
            if "." in builder:
                source_tab, method_name = builder.split(".", 1)
                instance = self.prepare(source_tab)
            else:
                instance = self.resolve_pane(tab_name)
                method_name = builder
            if instance is None:
                self.build_missing_pane(tab_name, pane)
            else:
                if not hasattr(instance, method_name):
                    import inspect
                    mod      = inspect.getmodule(instance.__class__)
                    file_path = getattr(mod, '__file__', None) or getattr(instance.__class__, '__module__', 'unknown file')
                    full_path =  f'File "{Path(inspect.getfile(self.form.__class__)).parent / (tab_name + ".py")}", line 1'
                    EZ.err(f"Method '{method_name}' not found in '{file_path}.py'. "
                           f"Add def {method_name}(self, parent): to that file.", origin=full_path)
                getattr(instance, method_name)(pane, *args, **kwargs)
        else:
            raise TypeError(f"Tab '{tab_name}': expected string or callable, got {type(builder)}")

    # ============================================================
    # Mutation and visibility
    # ============================================================
    def get_tab(self, name):
        """Return the cached _basePane instance for a tab, or None."""
        return self.pane_cache.get(name)

    def hide_tab(self, name):
        for btn in self.tab_row.children:
            if btn.text == name:  btn.visible = False

    def show_tab(self, name):
        for btn in self.tab_row.children:
            if btn.text == name:  btn.visible = True


    def set_pane(self, index, builder, *args, tab_name=None, **kwargs):
        tab_name                            = tab_name or self.active_tab
        entry                               = self.tab_layout[tab_name][index]
        weight                              = entry[1]
        self.tab_layout[tab_name][index]    = (builder, weight, args, kwargs)
        if tab_name == self.active_tab:
            pane                            = self.panes[index]
            if pane is None: return
            pane.children.clear()
            pane.children.clear()
            self.invoke_builder             ( tab_name, builder, pane, *args, **kwargs)


    def refresh_pane(self, index, tab_name=None):
        tab_name = tab_name or self.active_tab
        entry = self.tab_layout[tab_name][index]
        builder = entry[0] if isinstance(entry, tuple) else entry
        self.set_pane(index, builder, tab_name=tab_name)

    # ============================================================
    # Lazy discovery
    # ============================================================
    def resolve_pane(self, tab_name):
        """Find, import, and cache a Pane instance for this tab."""
        if tab_name in self.pane_cache:
            return self.pane_cache[tab_name]

        form_file  = Path(inspect.getfile(self.form.__class__)).parent
        #tab_lower  = tab_name.lower()
        #found      = [f for f in form_file.rglob("*.py") if f.stem.lower() == tab_lower]
        tab_lower  = tab_name.replace(" ", "").lower()
        found      = [f for f in form_file.rglob("*.py") if f.stem.replace("_", "").lower() == tab_lower]
        if len(found) == 0:
            return None
            #raise ImportError(f"No file '{tab_name}.py' found under {form_file}")
        if len(found) > 1:
            raise ImportError(f"Multiple '{tab_name}.py' found: {[str(f) for f in found]}")

        pane_class = self.load_pane_class(found[0], tab_name)
        instance   = pane_class(self.form)
        self.pane_cache[tab_name] = instance
        return instance

    def load_pane_class(self, file_path, tab_name):
        """Import a file and find the _basePane subclass inside."""
        spec   = importlib.util.spec_from_file_location(tab_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for attr_name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, _basePane) and obj is not _basePane:
                return obj

        raise ImportError(f"No _basePane subclass found in {file_path}")

    # ============================================================
    # Property
    # ============================================================
    @property
    def active_tab(self):
        return self._active_tab

    @active_tab.setter
    def active_tab(self, value):
        self._active_tab = value

    # ============================================================
    #
    # ============================================================
    def build_missing_pane(self, tab_name, pane):


        form_dir = Path(inspect.getfile(self.form.__class__)).parent
        file_path = form_dir / (tab_name + ".py")

        Title(pane, f"Tab '{tab_name}' needs a file")
        Body(pane,  f"Create:  {file_path}")
        Body(pane,  "Perhaps intentional for the moment.")
        btn = Button(pane, "Create Tab File", color_bg=Style.COLOR_PAL_GREEN_DARK)
        btn.on_click = lambda: self.create_pane_file(tab_name, file_path)

    def create_pane_file(self, tab_name, file_path):
        code = (
            f"from ipui.engine._basePane import _basePane\n"
            f"from ipui.widgets.Row import CardCol\n"
            f"from ipui.widgets.Text import Title, Heading\n\n\n"
            f"class {tab_name}(_basePane):\n\n"
            f"    def welcome(self, parent):\n"
            f"        card = CardCol(parent, width_flex=True, height_flex=True)\n"
            f"        Title(card, 'Welcome to IPUI', glow=True)\n"
            f"        sub = CardCol(card)\n"
            f"        Heading(sub, 'Easy to get right:', glow=True)\n"
            f"        Heading(sub, 'Hard to get wrong:', glow=True)\n"
        )
        file_path.write_text(code)
        self.switch_tab(self.active_tab)