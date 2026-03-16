from ipui.engine._BaseHugeTooltip import _BaseHugeTooltip


class TooltipArena(_BaseHugeTooltip):

    def __init__(self, arena_name, arena_data):
        super().__init__()
        self.arena_name = arena_name
        self.arena_data = arena_data

    def header_text(self):
        return self.arena_name

    def content_to_display(self):
        desc = self.arena_data.get("desc") or "(no description)"
        code = self.arena_data.get("code") or "(no code)"
        all_lines = desc.split("\n") + [""] + code.split("\n")
        return [all_lines]