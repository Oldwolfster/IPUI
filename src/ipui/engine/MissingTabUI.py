# MissingTabUI.py  NEW: Badass missing-tab wizard
from pathlib import Path

from ipui.engine._BasePane import _basePane
from ipui.widgets.Row import CardCol, CardRow
from ipui.widgets.Label import Title, Body, Detail, Banner
from ipui.widgets.Button import Button
from ipui.widgets.Spacer import Spacer
from ipui.Style import Style


class MissingTabUI(_basePane):

    def pitch(self, parent):
        card = parent
        tab_name = self.form.pipeline_read("missing_tab_name") or "???"
        file_name = f"{tab_name}.py"

        Banner(card, "Whoa there, Pilgrim!", glow=True)
        Spacer(card, height_flex=2)
        Title(card, f"The '{tab_name}' tab needs a home.",name="title_home")
        Title(card, f"AKA No {file_name} file found",name="title_aka")
        Spacer(card, height_flex=1)
        Title(card, "We can fix that faster than you")
        Title(card, "can say 'backpropagation'.")
        Spacer(card, height_flex=2)
        #wefix = Card(card)
        Banner(card, "Pick a template\nWe'll forge it for you.", glow=True)

        Spacer(card, height_flex=1)
        Body(card, self.form.pipeline_read("missing_tab_path"), name="body_full_path_to_file")
        Spacer(card, height_flex=1)

    def choices(self, parent):
        card = parent
        Title(card, "Choose Your Weapon", glow=True)
        Spacer(card, height_flex=1)

        self.make_option(card,
            "Bare Bones",
            "Skeleton only. Stubs, no fluff",
            "For speed demons",
            Style.COLOR_PAL_GREEN_DARK,
            lambda: self.generate_file("bare"))


        Spacer(card, height_flex=1)

        self.make_option(card,
            "Starter Kit",
            "Stubs + basics (Cards, Titles, Body)",
            "Instant screen life",
            Style.COLOR_PAL_GREEN_SECOND,
            lambda: self.generate_file("StarterKit"))

        Spacer(card, height_flex=1)

        self.make_option(card,
            "Full Showcase",
            "Every widget in action",
            "Steal code like a PRO",
            Style.COLOR_PAL_BLUE_MUTED,
            lambda: self.generate_file("showcase"))

        Spacer(card, height_flex=2)

        self.make_option(card,
            "Nah, I Got This",
            "Close this and create the file yourself.",
            "We believe in you. Really we do... honest.",
            Style.COLOR_PAL_RED_DARK,
            self.dismiss)

    def make_option(self, parent, label, desc, snark, color, action=None):
        row = CardRow(parent, width_flex=True)
        btn = Button(row, label, color_bg=color)
        if action:  # NEW
            btn.on_click = action  # NEW
        col = CardCol(row, width_flex=True, border=0)
        col.color_bg = None
        Body(col, desc)
        Detail(col, snark)

    def dismiss(self):
        tab_name = self.form.pipeline_read("missing_tab_name")
        self.form.tab_strip.pane_cache.pop("__missing__", None)
        self.form.tab_strip.switch_tab(next(iter(self.form.tab_strip.data)))

    def generate_file(self, level):
        file_path = self.form.pipeline_read("missing_tab_path")
        if level == "bare":
            Path(file_path).write_text(self.generate_bare())
        else:
            here = Path(__file__).parent
            template = here / "templates" / f"Template{level.title()}.py"
            self.generate_from_template(template)
        self.form.tab_strip.pane_cache.pop("__missing__", None)
        self.form.tab_strip.pane_cache.pop(self.form.pipeline_read("missing_tab_name"), None)
        self.form.tab_strip.switch_tab(self.form.pipeline_read("missing_tab_name"))

    def read_template(self, level):
        here = Path(__file__).parent
        names = {
            "bare": None,
            "starter": "TemplateStarterKit.py",
            "showcase": "TemplateShowcase.py",
        }
        if level == "bare":
            return self.generate_bare()
        return (here / names[level]).read_text()


    def generate_bare(self):
        methods = self.form.pipeline_read("missing_tab_methods")
        tab_name = self.form.pipeline_read("missing_tab_name")
        lines = [
            "from ipui import *\n\n\n",
            f"class {tab_name}(_basePane):\n",
        ]
        for m in methods:
            lines.append(f"\n    def {m}(self, parent):\n")
            lines.append(f"        Body(parent, \"Filename: {tab_name}.py\")\n")
            lines.append(f"        Body(parent, \"Method: {m}\")\n")
            lines.append(f"        Body(parent, \"Add content here!\")\n")
        return "".join(lines)
    def swap_methods(self, template, methods):
        result = template
        for i, method_name in enumerate(methods):
            placeholder = f"method_{i + 1}_IPUI_TAB_BUILDER"
            result = result.replace(placeholder, method_name)
        remaining = self.find_remaining_placeholders(result)
        #result = self.remove_unused_methods(result, remaining)
        return result

    def find_remaining_placeholders(self, text):
        import re
        return re.findall(r'method_\d+_IPUI_TAB_BUILDER', text)

    def fix_class_name(self, text, tab_name):
        return text.replace("class TemplateStarterKit", f"class {tab_name}")


    def generate_from_template(self, template_path):
        methods = self.form.pipeline_read("missing_tab_methods")
        tab_name = self.form.pipeline_read("missing_tab_name")
        file_path = self.form.pipeline_read("missing_tab_path")
        swaps = {
            "TemplateStarterKit": tab_name,
            "method_1_IPUI_TAB_BUILDER": methods[0] if len(methods) > 0 else None,
            "method_2_IPUI_TAB_BUILDER": methods[1] if len(methods) > 1 else None,
            "method_3_IPUI_TAB_BUILDER": methods[2] if len(methods) > 2 else None,
        }
        lines = Path(template_path).read_text(encoding="utf-8").splitlines(keepends=True)
        print(f"TEMPLATE: {template_path}")        # NEW
        print(f"SWAPS: {swaps}")                   # NEW
        print(f"FIRST LINE: {lines[0]!r}")
        print(f"WRITING TO: {file_path}")          # NEW

        out = []
        for line in lines:
            for old, new in swaps.items():
                if old in line and new is not None:
                    line = line.replace(old, new)
            out.append(line)
        Path(file_path).write_text("".join(out), encoding="utf-8")