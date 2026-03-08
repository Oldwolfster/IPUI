from ipui.engine._BaseHugeTooltip import _BaseHugeTooltip

class TooltipGladiator(_BaseHugeTooltip):

    def __init__(self, gladiator_name, gladiator_data):
        super().__init__()
        self.gladiator_name = gladiator_name
        self.gladiator_data = gladiator_data

    def header_text(self):
        return f"{self.gladiator_name}:"

    def content_to_display(self):
        desc = self.gladiator_data.get("desc") or "(no description)"
        code = self.gladiator_data.get("code") or "(no code)"
        all_lines = desc.split("\n") + [""] + code.split("\n")
        return [all_lines]