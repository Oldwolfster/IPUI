from ipui.utils.EZ import EZ


class WidgetsDict(dict):
    def __getitem__(self, key):
        if key not in self:
            EZ.err(f"Control '{key}' not found. Registered: {list(self.keys())}")


        return super().__getitem__(key)



    def get(self, key, default=None):
        if key in self:
            return super().get(key, default)

        EZ.err(
            f"Pipeline key assigned to Control that is not found:\n"
            f"**{key}**\n"
            f"Registered names: {list(self.keys())}\n\n"
            f""
            f"# =========================\n"
            f"# THREE EASY WAYS TO FIX\n"
            f"# 1) In BINDINGS change {key} to one of the above registered names.'\n"
            f"# 2) Name a widget '{key}'.  \n\tIt will be synchronized with that pipeline field.\n"
            f"# 3) REMOVE: Remove: **{key}** from BINDINGS\n"
            f"# =========================\n",
            RuntimeError
        )
