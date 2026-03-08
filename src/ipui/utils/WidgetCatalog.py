# WidgetCatalog.py  NEW: Runtime widget discovery and docstring parsing
import inspect
import pkgutil
import importlib


class WidgetCatalog:
    """Discovers all _BaseWidget subclasses at runtime and parses their structured docstrings.

    Usage:
        catalog = WidgetCatalog("ipui.widgets")
        entries = catalog.entries   # list of dicts
    """

    FIELDS = ( "desc", "when_to_use", "best_for", "example", "api")

    def __init__(self, package_name="ipui.widgets"):
        self.package_name = package_name
        self.entries      = []
        self.discover()

    # ══════════════════════════════════════════════════════════════
    # DISCOVERY
    # ══════════════════════════════════════════════════════════════

    def discover(self):
        """Import all widget modules, walk subclasses, build entries."""
        self.import_all_modules()
        from ipui.engine._BaseWidget import _BaseWidget
        classes = self.collect_subclasses(_BaseWidget)
        self.entries = [self.build_entry(cls) for cls in classes]
        self.entries.sort(key=lambda e: e["name"])

    def import_all_modules(self):
        """Force-import every module under the widgets package."""
        try:
            package = importlib.import_module(self.package_name)
        except ModuleNotFoundError:
            return
        for importer, mod_name, is_pkg in pkgutil.walk_packages(
            package.__path__, prefix=package.__name__ + "."
        ):
            try:
                importlib.import_module(mod_name)
            except Exception:
                pass

    def collect_subclasses(self, base):
        """Recursively gather all concrete subclasses of base."""
        result = []
        for cls in base.__subclasses__():
            result.append(cls)
            result.extend(self.collect_subclasses(cls))
        return result

    # ══════════════════════════════════════════════════════════════
    # ENTRY BUILDING
    # ══════════════════════════════════════════════════════════════

    def build_entry(self, cls):
        """Build a catalog entry dict from a widget class."""
        parsed = self.parse_docstring(cls)
        source = self.safe_source(cls)
        lines  = source.count("\n") + 1 if source else 0
        return {
            #"name":       parsed.get("name", cls.__name__),
            "name":        cls.__name__,
            "class":       cls,
            "file":        self.safe_file(cls),
            "lines":       lines,
            "desc":        parsed.get("desc", ""),
            "when_to_use": parsed.get("when_to_use", ""),
            "best_for":    parsed.get("best_for", ""),
            "example":     parsed.get("example", ""),
            "api":         parsed.get("api", ""),
            "source":      source,
        }

    # ══════════════════════════════════════════════════════════════
    # DOCSTRING PARSING
    # ══════════════════════════════════════════════════════════════

    @classmethod
    def parse_docstring(cls, widget_class):
        """Extract structured fields from a class docstring.

        Expects format:
            name:        Button
            desc:        One click. Beveled like forged steel.
            when_to_use: Any action the user can trigger.
        """
        doc = inspect.getdoc(widget_class)
        if not doc:
            return {}
        result = {}
        for line in doc.split("\n"):
            line = line.strip()
            if not line:
                continue
            for field in cls.FIELDS:
                prefix = field + ":"
                if line.lower().startswith(prefix):
                    value = line[len(prefix):].strip()
                    result[field] = value
                    break
        return result

    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def safe_source(cls):
        """Get source code, return empty string on failure."""
        try:
            return inspect.getsource(cls)
        except (OSError, TypeError):
            return ""

    @staticmethod
    def safe_file(cls):
        """Get source filename, return empty string on failure."""
        try:
            path = inspect.getfile(cls)
            return path.split("/")[-1].split("\\")[-1]
        except (OSError, TypeError):
            return ""

    # ══════════════════════════════════════════════════════════════
    # CONVENIENCE
    # ══════════════════════════════════════════════════════════════

    def as_grid_data(self):
        """Return data formatted for DataGrid.set_data (list of dicts)."""
        return [
            {
                "Widget":      e["name"],
                #"Lines":       e["lines"],
                #"File":        e["file"],
                "Description": e["desc"],
            }
            for e in self.entries
        ]

    def entry_for(self, widget_name):
        """Look up a single entry by widget name."""
        for e in self.entries:
            if e["name"] == widget_name:
                return e
        return None