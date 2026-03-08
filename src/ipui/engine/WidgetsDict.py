from ipui.utils.EZ import EZ


class WidgetsDict(dict):
    def __getitem__(self, key):
        if key not in self:
            raise RuntimeError(f"Control '{key}' not found. Registered: {list(self.keys())}")
            EZ.err(
                f"Pipeline key assigned to Control that is not found: '{key}'"
                f"Registered names: {list(self.keys())}\n\n"
                f""
                f"# =========================\n"
                f"# TWO WAYS TO FIX\n"
                f"# 1) If this is a Debugger pane: register the derive on the Debugger form's pipeline,\n"
                f"#    not the debug target's pipeline.\n"
                f"# 2) If this is normal app UI: add name='{key}' to the widget you want updated so it\n"
                f"#    is registered in form.widgets.\n"
                f"# =========================\n",
                RuntimeError
            )

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
            f"# TWO EASY WAYS TO FIX\n"
            f"# 1) Name a widget '{key}'.  \n\tIt will be synchronized with that pipeline field.\n"
            f"# 2) REMOVE: Stop setting pipeline key: **{key}**\n"
            f"# =========================\n",
            RuntimeError
        )
