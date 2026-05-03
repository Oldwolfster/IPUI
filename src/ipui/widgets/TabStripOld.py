from ipui.widgets.Row import Col
from ipui.widgets.Spacer import Spacer
import importlib.util
import inspect
from pathlib import Path
from ipui.widgets.Row import Row
from ipui.Style import Style
from ipui.engine.MgrColor import MgrColor
from ipui.engine._BaseTab import _BaseTab
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
    desc:        String-based tab manager. Auto-discovers _BaseTab files, lazy-loads on first visit, caches everything.
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
        self.pad=0
        self.border=-2
        self.tab_cache  = {}
        self.content_cache = {}
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
        self.tab_row   = CardRow(outer, width_flex=1,pad=2)

    def build_content_area(self):
        self.content = Row(self, width_flex=1, height_flex=1)
        self.panes   = []
        self.rebuild_tab_buttons()

    def rebuild_tab_buttons(self):
        self.tab_row.children.clear()
        for tab_name in self.data:
            btn          = Button(self.tab_row, tab_name, color_bg=Style.COLOR_TAB_BG, width_flex=1,border_radius=0)
            btn.on_click = lambda name=tab_name: self.switch_tab(name)


    def prepare(self, name):
        """Resolve, cache, and initialize a tab's _BaseTab on demand."""
        if name not in self.tab_cache:  self.resolve_tab(name)
        return self.tab_cache[name]

    # ============================================================
    # Switching tabs
    # ============================================================

    def switch_tab(self, name):
        print(f"SWITCH_TAB called: {name}")
        if not self.allow_switch(name):     return
        if name != self.active_tab:
            self.cache_active_content()
        self.active_tab = name
        self.update_button_visuals()
        self.ensure_content(name)
        self.notify_activated(name)

    def allow_switch(self, name):
        if not self.on_change:              return True
        return self.on_change(name, self.active_tab) is not False

    def ensure_setup(self, name):
        tab = self.tab_cache.get(name)
        if tab and not tab.private_setup_done:
            tab.private_setup_done = True
            tab.ip_setup(tab.ip)


    def notify_activated(self, name):
        tab = self.tab_cache.get(name)
        if tab:
            from ipui.engine.IPUI import IPUI
            ip = IPUI.ip
            ip.set_tab_context(tab, name, True, self.content)
            tab.ip_activated(ip)

    def ensure_content(self, name):
        if name in self.content_cache:
            self.restore_cached_content(name)
            return
        entries = self.tab_layout[name]
        if self.needs_missing_page(name, entries):
            entries = self.missing_tab_entries(name)
        self.rebuild_tab_areas(entries)
        self.ensure_setup(name)
        self.fill_panes(name, entries)

    def cache_active_content(self):
        if self.active_tab is None:    return
        self.content_cache[self.active_tab] = (
            list(self.content.children),
            list(self.panes),
        )
        self.content.children.clear()

    def restore_cached_content(self, name):
        children, panes = self.content_cache[name]
        self.content.children.clear()
        self.content.children.extend(children)
        self.panes = panes

    def needs_missing_page(self, name, entries):
        if self.form_has_builders(entries):     return False
        if self.resolve_tab(name) is not None: return False
        return any(
            isinstance(b, str) and "." not in b
            for b, w in entries if b is not None
        )

    def form_has_builders(self, entries):
        for entry in entries:    # entries are 2-tuples initially but set_pane() grows them to 4-tuples with (builder, weight, args, kwargs)
            builder = entry[0]
            if builder is None:
                continue
            if isinstance(builder, str) and "." not in builder:
                method_name = builder.replace(" ", "_")
                if not hasattr(self.form, method_name):
                    return False
        return True

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
                pane = Pane(self.content, width_flex=weight, height_flex=1)
                pane.color_bg  = None
                pane.border_top = None
                self.panes[i]  = pane
            else:
                if current_area is None:  current_area = TabArea(self.content, width_flex=0, height_flex=1)
                current_area.width_flex += weight
                pane = Pane(current_area.inner, width_flex=weight, height_flex=1)
                self.panes[i] = pane

    def fill_panes(self, name, pane_list):
        for i, entry in enumerate(pane_list):
            builder = entry[0]
            args    = entry[2] if len(entry) > 2 else ()
            kwargs  = entry[3] if len(entry) > 3 else {}
            if builder is not None:
                self.invoke_builder(name, builder, self.panes[i], *args, **kwargs)

    def missing_tab_entries(self, tab_name):
        from ipui.engine.MissingTabUI import MissingTabUI
        self.form.pipeline_set("missing_tab_name", tab_name)
        methods = [e[0] if isinstance(e, tuple) else e for e in self.tab_layout[tab_name]]
        self.form.pipeline_set("missing_tab_methods", methods)
        form_dir = Path(inspect.getfile(self.form.__class__)).parent  # NEW
        self.form.pipeline_set("missing_tab_path", str(form_dir / (tab_name.replace(" ", "") + ".py")))
        self.tab_cache["__missing__"] = MissingTabUI(self.form)
        return [("__missing__.pitch", 2), ("__missing__.choices",1)]

    def ensure_pane_count(self, needed):
        while len(self.panes) < needed:
            pane = CardCol(self.content, width_flex=1, height_flex=1)
            self.panes.append(pane)

    def invoke_builder(self,   tab_name, builder, pane, *args, **kwargs):
        """clean dispatch checklist"""
        if self.inv_delegate  (tab_name, builder, pane, *args, **kwargs): return
        if self.inv_cross_tab (tab_name, builder, pane, *args, **kwargs): return
        if self.inv_pane      (tab_name, builder, pane, *args, **kwargs): return
        self.houston          (tab_name, builder)

    def inv_delegate(self, tab_name, builder, pane, *args, **kwargs):
        """invoke a callable (lambda or function)"""
        if not callable(builder):    return False
        builder(pane, *args, **kwargs)
        return True

    def inv_cross_tab(self, tab_name, builder, pane, *args, **kwargs):
        """invoke a dotted cross-tab pane reference"""
        if not isinstance(builder, str):    return False
        if "." not in builder:              return False
        source_tab, method_name = builder.split(".", 1)
        instance = self.prepare(source_tab)
        self.validate_and_call(instance, method_name, tab_name, pane, *args, **kwargs)
        return True

    def inv_pane(self, tab_name, builder, pane, *args, **kwargs):
        """invoke a pane builder from form or tab file"""
        if not isinstance(builder, str):    return False
        instance, method_name = self.resolve_builder(tab_name, builder)
        self.validate_and_call(instance, method_name, tab_name, pane, *args, **kwargs)
        return True

    def houston(self, tab_name, builder):
        """nothing matched — bad builder type"""
        EZ.err(f"Tab '{tab_name}': expected string or callable, got {type(builder).__name__}")

    def resolve_builder(self, tab_name, builder):
        """find instance and method name for a string builder"""
        if "." in builder:
            source_tab, method_name = builder.split(".", 1)
            return self.prepare(source_tab), method_name
        instance = self.resolve_tab_or_form(tab_name, builder)
        method_name = builder.replace(" ", "_")
        if instance and not hasattr(instance, method_name):
            method_name = builder.replace(" ", "")
        return instance, method_name

    def validate_and_call(self, instance, method_name, tab_name, pane, *args, **kwargs):
        """check method exists and is callable, then invoke"""
        if not hasattr(instance, method_name):
            self.err_method_not_found(instance, method_name, tab_name)
        method = getattr(instance, method_name)
        if not callable(method):
            EZ.err(
                f"'{method_name}' on {type(instance).__name__} is a {type(method).__name__}, not a method.\n"
                f"TAB_LAYOUT pane name '{method_name}' collides with an attribute.\n"
                f"FIX: Rename the pane method or the attribute.")
        method(pane, *args, **kwargs)

    def err_method_not_found(self, instance, method_name, tab_name):
        """friendly error for missing pane builder"""
        import inspect
        mod = inspect.getmodule(instance.__class__)
        file_path = getattr(mod, '__file__', None) or getattr(instance.__class__, '__module__', 'unknown file')
        full_path = f'File "{Path(inspect.getfile(self.form.__class__)).parent / (tab_name + ".py")}", line 1'
        EZ.err(f"Method '{method_name}' not found in '{file_path}.py'. "
               f"Add def {method_name}(self, parent): to that file.", origin=full_path)

    def resolve_tab_or_form(self, tab_name, builder):
        method_name = builder.replace(" ", "_")
        if hasattr(self.form, method_name):
            self.tab_cache[tab_name] = self.form  # to support the 'one pager' version.
            return self.form
        return self.resolve_tab(tab_name)

    # ============================================================
    # Lazy discovery of tabs/panes
    # ============================================================
    def resolve_tab(self, tab_name):
        """Find, import, and cache a _BaseTab instance for this tab."""
        print(f"RESOLVE_TAB: cache check '{tab_name}', in cache = {tab_name in self.tab_cache}")
        if tab_name in self.tab_cache:
            return self.tab_cache[tab_name]

        form_file  = Path(inspect.getfile(self.form.__class__)).parent
        tab_lower  = tab_name.replace(" ", "").lower()
        found = [f for f in form_file.rglob("*.py")
                 if f.stem.replace("_", "").replace(" ", "").lower() == tab_lower]
        print(f"RESOLVE_TAB: looking for '{tab_lower}', found = {found}")  # NEW

        if len(found) == 0:
            return None
            #raise ImportError(f"No file '{tab_name}.py' found under {form_file}")
        if len(found) > 1:
            raise ImportError(f"Multiple '{tab_name}.py' found: {[str(f) for f in found]}")

        tab_class = self.load_tab_class(found[0], tab_name)
        instance   = tab_class(self.form)
        self.tab_cache[tab_name] = instance
        return instance

    def load_tab_class(self, file_path, tab_name):
        """Import a file and find the _BaseTab subclass inside."""
        spec   = importlib.util.spec_from_file_location(tab_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for attr_name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, _BaseTab) and obj is not _BaseTab:
                return obj

        raise ImportError(f"No _BaseTab subclass found in {file_path}")

    # ============================================================
    # Mutation and visibility
    # ============================================================
    def get_tab(self, name):
        """Return the cached _BaseTab instance for a tab, or None."""
        return self.tab_cache.get(name)

    def hide_tab(self, name):
        for btn in self.tab_row.children:
            if btn.text == name:  btn.visible = False

    def show_tab(self, name):
        for btn in self.tab_row.children:
            if btn.text == name:  btn.visible = True

    def set_pane(self, index, builder, *args, tab_name=None, weight=None, **kwargs):
        tab_name                            = tab_name or self.active_tab
        needs_rebuild                       = index >= len(self.tab_layout[tab_name])
        self.grow_tab_layout(index, tab_name)
        entry                               = self.tab_layout[tab_name][index]
        weight                              = weight if weight is not None else entry[1]
        self.tab_layout[tab_name][index]    = (builder, weight, args, kwargs)
        if tab_name == self.active_tab:
            if needs_rebuild:
                entries                      = self.tab_layout[tab_name]
                self.rebuild_tab_areas(entries)
                self.fill_panes(tab_name, entries)
            else:
                pane                        = self.panes[index]
                if pane is None: return
                pane.children.clear()
                self.invoke_builder         ( tab_name, builder, pane, *args, **kwargs)
            # Removed 4/22 self.form.layout_engine.RunLayout()

    def grow_tab_layout(self, index, tab_name):
        entries = self.tab_layout[tab_name]
        while len(entries) <= index:
            entries.append((None, 1))

    def refresh_pane(self, index, tab_name=None):
        tab_name = tab_name or self.active_tab
        entry = self.tab_layout[tab_name][index]
        builder = entry[0] if isinstance(entry, tuple) else entry
        self.set_pane(index, builder, tab_name=tab_name)

    # ============================================================
    # Property
    # ============================================================
    @property
    def active_tab(self):
        return self._active_tab

    @active_tab.setter
    def active_tab(self, value):
        self._active_tab = value
