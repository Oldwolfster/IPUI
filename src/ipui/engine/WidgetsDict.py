from ipui.utils.EZ import EZ

# Define a private constant that can't be confused with a real value
_MISSING = object()

class WidgetsDict(dict):
    def __getitem__(self, key):
        if key not in self:
            EZ.err(f"Control '{key}' not found. Registered: {list(self.keys())}")


        return super().__getitem__(key)



    def get(self, key, default=_MISSING):
        if key in self              : return super().get(key)   # We use super() to avoid recursion if self is a dict-like
        if default is not _MISSING  : return default            # If the user passed ANYTHING (even None), return it.

        EZ.err(
            f"Pipeline key assigned to Control that is not found:\n"
            f"**{key}**\n"
            f"Registered names: {list(self.keys())}\n\n"
            f""
            f"# =========================\n"
            f"# Four EASY WAYS TO FIX\n"
            f"# 1) In BINDINGS change {key} to one of the above registered names.'\n"
            f"# 2) Name a widget '{key}'.  It will be synchronized with that pipeline field.\n"
            f"# 3) REMOVE: Remove: **{key}** from BINDINGS\n"
            f"# NOTE: It is also possible that {key} is not created yet. (Timing issue)"
            f"# 4) Send a default value (None works) and test for it if it's legitimate that the control might not exist yet \n"
            f"# =========================\n",
            RuntimeError
        )
