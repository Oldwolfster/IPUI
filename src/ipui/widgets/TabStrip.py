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
        self.flex_width  = 1
        self.flex_height = 1
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

    def find_tab_file(self, tab_name):
        form_dir  = Path(inspect.getfile(self.form.__class__)).parent
        tab_lower = tab_name.replace(" ", "").replace("_", "").lower()
        found     = [f for f in form_dir.rglob("*.py")
                     if f.stem.replace("_", "").replace(" ", "").lower() == tab_lower]
        if len(found) > 1:
            EZ.err(
                f"Multiple files match tab '{tab_name}': {[f.name for f in found]}\n"
                f"Each tab must resolve to exactly one file.\n"
                f"Remove or rename the duplicate.",
                locate=tab_name
            )
        return found[0] if found else None

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
        self.tab_row   = CardRow(outer, flex_width=1,pad=2)

    def build_content_area(self):
        self.content = Row(self, flex_width=1, flex_height=1)
        self.panes   = []
        self.rebuild_tab_buttons()

    def rebuild_tab_buttons(self):
        self.tab_row.children.clear()
        for tab_name in self.data:
            btn          = Button(self.tab_row, tab_name, color_bg=Style.COLOR_TAB_BG, flex_width=1,border_radius=0)
            btn.on_click = lambda name=tab_name: self.switch_tab(name)


    def prepare(self, name):
        """Resolve, cache, and initialize a tab's _BaseTab on demand."""
        if name not in self.tab_cache:  self.resolve_tab(name)
        return self.tab_cache[name]


    def err_tab_one_pager(self, name, method_name):
        """tab_early_load needs a tab file — gentle nudge to migrate from the one-pager smoke-test shape."""
        file_name = name.replace(' ', '')
        EZ.err(
            f"To use tab_early_load, create a tab file for '{name}'.\n"
            f"\n"
            f"  1) Create {file_name}.py in your form's directory:\n"
            f"\n"
            f"        from ipui import *\n"
            f"\n"
            f"        class {file_name}(_BaseTab):\n"
            f"            def {method_name}(self, parent):\n"
            f"                # paste the body of your form's {method_name}() here\n"
            f"                ...\n"
            f"\n"
            f"  2) Remove the {method_name}() method from your form.\n"
            f"\n"
            f"  3) tab_early_load = ['{name}'] now works as expected.\n"
            f"\n"
            f"TIP: Or just remove '{name}' from tab_early_load — early load is\n"
            f"TIP: an optimization, not a requirement. The one-pager keeps working."
        )
    def err_tab_not_in_layout(self, name):
        """tab_early_load names a tab that isn't in TAB_LAYOUT."""
        EZ.err(
            f"tab_early_load contains '{name}', but TAB_LAYOUT has no '{name}' tab.\n"
            f"\n"
            f"ROOT CAUSE: Every name in tab_early_load must match a key in TAB_LAYOUT.\n"
            f"            Looks like a typo or a leftover entry.\n"
            f"\n"
            f"You wrote:     tab_early_load = [..., '{name}', ...]\n"
            f"Did you mean:  one of these — {list(self.tab_layout.keys())}\n"
            f"\n"
            f"Fixes:\n"
            f"  1) Remove '{name}' from tab_early_load.\n"
            f"  2) Add '{name}' as a key in TAB_LAYOUT."
        )



    def err_tab_unresolvable(self, name, first_builder):
        """tab_early_load names a tab whose builder lives nowhere — not on the form, not in a file."""
        method_name = first_builder.replace(" ", "_") if isinstance(first_builder, str) else "<builder>"
        form_dir = Path(inspect.getfile(self.form.__class__)).parent
        expected = form_dir / (name.replace(" ", "") + ".py")
        EZ.err(
            f"tab_early_load contains '{name}', but it can't be found.\n"
            f"\n"
            f"ROOT CAUSE: Early-loaded tabs need either:\n"
            f"            (a) a method on the form that builds the pane(s), OR\n"
            f"            (b) an external {name.replace(' ', '')}.py file with a _BaseTab subclass.\n"
            f"\n"
            f"The '{name}' tab's first pane is built by '{method_name}'. IPUI checked\n"
            f"the form (no method named '{method_name}') and the form's directory\n"
            f"(no file at {expected}) — neither exists.\n"
            f"\n"
            f"Fixes:\n"
            f"  1) Remove '{name}' from tab_early_load.\n"
            f"\n"
            f"  2) Add a tab builder method to the form. Example:\n"
            f"        def {method_name}(self, parent):\n"
            f"            # build the '{name}' tab here\n"
            f"\n"
            f"  3) Create {name.replace(' ', '')}.py with a _BaseTab subclass."
        )
    # ============================================================
    # Switching tabs
    # ============================================================
    def switch_tab(self, name):
        if not self.allow_switch(name):     return
        if name != self.active_tab:
            self.cache_active_tab()
        self.active_tab = name
        self.update_button_visuals()
        self.resolve_tab(name)  # 1. instantiate tab class (cheap, no widgets)
        self.set_ip_context(name) # last addition 5/4
        self.fire_ip_setup_early(name)  # 2. user pre-widget state on self
        self.build_tabs_widget_tree(name)  # 3. run pane builders, widgets register
        self.fire_ip_setup(name)  # 4. user post-widget state, BINDINGS-safe
        self.fire_ip_activated(name)  # 5. user activation hook

    def allow_switch(self, name):
        if not self.on_change:              return True
        return self.on_change(name, self.active_tab) is not False


    def fire_ip_setup_early(self, name):
        tab = self.tab_cache.get(name)
        if tab is None: return
        if getattr(tab, 'private_setup_early_done', False): return
        tab.private_setup_early_done = True
        if hasattr(tab, 'ip_setup_early'):
            tab.ip_setup_early(tab.ip)

    def build_tabs_widget_tree(self, name):
        if name in self.content_cache:
            self.restore_cached_tab(name)
            return
        entries = self.tab_layout[name]
        if self.needs_missing_page(name, entries):
            entries = self.missing_tab_entries(name)
        self.rebuild_tab_areas(entries)
        self.run_pane_builders(name, entries)

    def fire_ip_setup(self, name):
        """Update: defensive getattr for form-as-tab Quick Start pattern"""
        tab = self.tab_cache.get(name)
        if tab and not getattr(tab, 'private_setup_done', False):
            tab.private_setup_done = True
            tab.ip_setup(tab.ip)

    def fire_ip_activated(self, name):
        """Update: only fires ip_activated — context now set in set_ip_context"""
        tab = self.tab_cache.get(name)
        if tab is None: return
        from ipui.engine.IPUI import IPUI
        tab.ip_activated(IPUI.ip)


    def set_ip_context(self, name):
        """populate ip with tab context BEFORE ip_setup or ip_activated fires"""
        tab = self.tab_cache.get(name)
        if tab is None: return
        from ipui.engine.IPUI import IPUI
        ip = IPUI.ip
        ip.set_tab_context(tab, name, True, self.content)

    def cache_active_tab(self):
        if self.active_tab is None:    return
        self.content_cache[self.active_tab] = (
            list(self.content.children),
            list(self.panes),
        )
        self.content.children.clear()

    def restore_cached_tab(self, name):
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
                #Col(self.content, flex_width=weight, flex_height=1)
                current_area = None
                pane = Pane(self.content, flex_width=weight, flex_height=1)
                pane.color_bg  = None
                pane.border_top = None
                self.panes[i]  = pane
            else:
                if current_area is None:  current_area = TabArea(self.content, flex_width=0, flex_height=1)
                current_area.flex_width += weight
                pane = Pane(current_area.inner, flex_width=weight, flex_height=1)
                self.panes[i] = pane

    def run_pane_builders(self, name, pane_list):
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
        return [("__missing__.pitch", 1.5), ("__missing__.choices",1)]

    def ensure_pane_count(self, needed):
        while len(self.panes) < needed:
            pane = CardCol(self.content, flex_width=1, flex_height=1)
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
        #print(f"RESOLVE_TAB: cache check '{tab_name}', in cache = {tab_name in self.tab_cache}")
        if tab_name in self.tab_cache:
            return self.tab_cache[tab_name]

        form_file  = Path(inspect.getfile(self.form.__class__)).parent
        tab_lower  = tab_name.replace(" ", "").replace("_", "").lower()
        #20260505 found = [f for f in form_file.rglob("*.py")
        #20260505         if f.stem.replace("_", "").replace(" ", "").lower() == tab_lower]
        found = [f for f in form_file.rglob("*.py")  # NEW
                 if not self.is_in_excluded_dir(f, form_file)  # NEW
                 and f.stem.replace("_", "").replace(" ", "").lower() == tab_lower]  # NEW

        if len(found) == 0:
            return None
            #raise ImportError(f"No file '{tab_name}.py' found under {form_file}")
        if len(found) > 1:
            raise ImportError(f"Multiple '{tab_name}.py' found: {[str(f) for f in found]}")

        tab_class = self.load_tab_class(found[0], tab_name)
        instance   = tab_class(self.form)
        self.tab_cache[tab_name] = instance
        return instance


    def is_in_excluded_dir(self, path, form_dir):                                       # NEW
        """A user's project shouldn't find files inside installed packages, but        # NEW
        framework-internal forms searching their own directory tree are fine."""       # NEW
        form_in_site_packages = "site-packages" in form_dir.parts                       # NEW
        path_in_site_packages = "site-packages" in path.parts                           # NEW
        return path_in_site_packages and not form_in_site_packages

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
                self.run_pane_builders(tab_name, entries)
            else:
                pane                        = self.panes[index]
                if pane is None: return
                pane.flex_width = weight
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
