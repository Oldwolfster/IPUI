# Logger.py (complete file)
import sys
import inspect
from datetime import datetime


class Log:
    def __init__(self, message, category="General", severity="Medium", source=""):
        self.message   = message
        self.category  = category
        self.severity  = severity
        self.source    = source
        self.timestamp = datetime.now()

    @property
    def time_str(self):
        return self.timestamp.strftime("%H:%M:%S")

    @property
    def date_str(self):
        return self.timestamp.strftime("%Y-%m-%d")

    def matches(self, keyword="", category="", severities=None):
        if keyword and keyword.lower() not in self.message.lower():
            return False
        if category and category.lower() not in self.category.lower():
            return False
        if severities and self.severity not in severities:
            return False
        return True

    def display_text(self):
        return f"{self.time_str}  [{self.severity[0]}]  [{self.category}]  {self.message}"


class Logger:
    instance        = None
    SEVERITIES      = ["Low", "Medium", "High", "Error"]
    MAX_ENTRIES     = 5000

    def __init__(self):
        Logger.instance       = self
        self.original_stdout  = sys.stdout
        self.entries          = []
        self.ui_callback      = None
        # INTERCEPT PRINT STATEMETNS.stdout            = self

    # ---- Public API ----

    @staticmethod
    def log(message, category="General", severity="Medium"):
        inst = Logger.instance
        if inst is None:
            return
        source = Logger.caller_module()
        entry  = Log(message, category, severity, source)
        inst.entries.append(entry)
        if len(inst.entries) > inst.MAX_ENTRIES:    # Add below this line
            inst.entries = inst.entries[-inst.MAX_ENTRIES:]
        inst.original_stdout.write(entry.display_text() + "\n")
        inst.notify_ui()

    @staticmethod
    def log_subprocess(line, run_id="Unknown"):
        Logger.log(line, category=f"Run-{run_id}", severity="Low")

    # ---- stdout intercept ----

    def write(self, text):
        if not text.strip():
            return
        source = Logger.caller_module()
        entry  = Log(text.rstrip(), category="Print", severity="Low", source=source)
        self.entries.append(entry)
        self.original_stdout.write(entry.display_text() + "\n")
        self.notify_ui()

    def flush(self):
        self.original_stdout.flush()

    # ---- Helpers ----

    @staticmethod
    def caller_module():
        for frame in inspect.stack()[2:]:
            module = frame.filename.split("/")[-1].split("\\")[-1].replace(".py", "")
            if module != "Logger":
                return module
        return "Unknown"

    def notify_ui(self):
        if self.ui_callback:
            self.ui_callback()

    def filtered(self, keyword="", category="", severities=None):
        return [e for e in self.entries if e.matches(keyword, category, severities)]