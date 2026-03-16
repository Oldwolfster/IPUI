# Pipeline.py  NEW: Reactive data store with derives

from ipui.utils.EZ import EZ


class Pipeline:

    def __init__(self, widgets, widget_registry):
        self.widgets = widgets                  #only named widgets
        self.widget_registry = widget_registry  #all widgets with wid
        self.data     = {}
        self.derives  = {}
        self.debug    = False

    def set(self, key, value):
        self.data[key] = value
        if self.debug:
            print(f"[pipeline] '{key}' set to '{value}'")
        self.fire_derives(key)
        self.notify_source(key)

    def notify_sourceOld(self, key):
        for widget in self.widgets.values():
            if getattr(widget, 'pipeline_key', None) == key:
                if hasattr(widget, 'sync_from_pipeline'):
                    widget.sync_from_pipeline()


    def notify_source(self, key):
        for widget in self.widget_registry.values():        # REPLACE (was: self.widgets.values())
            if getattr(widget, 'pipeline_key', None) == key:
                if hasattr(widget, 'sync_from_pipeline'):
                    widget.sync_from_pipeline()

    def read(self, key):
        return self.data.get(key)

    def register_derive(self, control_name, property, compute, triggers):
        self.derives[control_name] = {
            "property": property,
            "compute":  compute,
            "triggers":     triggers,
        }

    def fire_derives(self, changed_key):
        for control_name, entry in self.derives.items():
            if changed_key not in entry["triggers"]:
                continue
            args   = [self.data.get(k, "") for k in entry["triggers"]]
            result = entry["compute"](*args)
            self.apply(control_name, entry["property"], result)
            if self.debug:
                print(
                    f"[pipeline]   → {entry['compute'].__name__}"
                    f"({', '.join(repr(a) for a in args)}) → {repr(result)}"
                    f" → {control_name}.{entry['property']}"
                )

    def apply(self, control_name, property, value):
        control = self.widgets.get(control_name)
        if control is None:
            return
        if   property == "text":    control.set_text(str(value))
        elif property == "enabled":
            if value:               control.set_enabled()
            else:                   control.set_disabled()
        elif property == "visible": control.visible = bool(value)

