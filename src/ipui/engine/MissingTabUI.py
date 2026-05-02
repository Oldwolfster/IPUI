# MissingTabUI.py  NEW: Badass missing-tab wizard
from pathlib import Path

from ipui import CENTER, Heading, Card, Plate
from ipui.engine._BaseTab import _BaseTab
from ipui.widgets.Row import CardCol, CardRow, Row
from ipui.widgets.Label import Title, Body, Detail, Banner
from ipui.widgets.Button import Button
from ipui.widgets.Spacer import Spacer
from ipui.Style import Style


class MissingTabUI(_BaseTab):

    def pitch(self, parent):

        tab_name = self.form.pipeline_read("missing_tab_name") or "???"
        Spacer(parent, height_flex=1)
        row=Row(parent)
        Spacer(row,width_flex=1)
        card = Card(row,pad=20,width_flex=3)
        Spacer(card)
        c = Plate(card, pad=20,hug_parent=True)
        Banner(c, "Houston,", glow=True,text_align=CENTER,hug_parent=True)
        Title (c, "we've found a ghost in the machine.",glow=True,text_align=CENTER)
        Title(c, " ")
        Spacer(card)
        msg= Plate(c,pad=20)
        Heading(msg,f"The {tab_name} tab is listed in TAB_LAYOUT,",text_align=CENTER,hug_parent=True)
        Heading(msg, f"but IPUI couldn\'t find a matching file for it.", text_align=CENTER)

        Spacer(c, height_flex=1)
        #c = Plate(card, pad=20)
        Title(c, " ")
        Title(c, "Pick a template", text_align=CENTER, hug_parent=True)
        Title(c, "We'll forge it for you.", glow=True,text_align=CENTER)
        Body(c, f'Tab name: "{tab_name}"', text_align=CENTER)
        Spacer(row,width_flex=1)
        Spacer(card, height_flex=1)
        Spacer(parent, height_flex=1)


    def choices(self, parent):
        card = parent
        Title(card,"")
        Title(card, "Choose Your Weapon", glow=True,text_align=CENTER)
        Spacer(card, height_flex=1)

        self.make_option(card,
            "Bare\nBones",
            "Skeleton only. Stubs, no fluff",
            "For speed demons",
            Style.COLOR_BUTTON_SECONDARY,
            lambda: self.generate_file("bare"))


        Spacer(card, height_flex=1)

        self.make_option(card,
            "Starter\nKit",
            "Stubs + basics (Cards, Titles, Body)",
            "Instant screen life",
            Style.COLOR_BUTTON_SECONDARY,
            lambda: self.generate_file("StarterKit"))

        Spacer(card, height_flex=1)

        self.make_option(card,
            "Full\nShowcase",
            "Every widget in action",
            "Steal code like a PRO",
            Style.COLOR_BUTTON_CTA,
            lambda: self.generate_file("showcase"))

        Spacer(card, height_flex=1)

        self.make_option(card,
            "Nah,\nI Got This",
            "Close this and create the file yourself.",
            "We believe in you. Really we do... honest.",
            Style.COLOR_BUTTON_DANGER,
            self.dismiss)

        Spacer(card, height_flex=1)

    def make_option(self, parent, label, desc, snark, color, action=None):
        row = CardRow(parent, width_flex=1)
        btn = Button(row, label, color_bg=color,pad=10,border=3,width_flex=3)
        if action:  # NEW
            btn.on_click = action  # NEW
        col = CardCol(row, width_flex=8, border=0)
        col.color_bg = None
        Body(col, desc)
        Detail(col, snark)

    def dismiss(self):
        tab_name = self.form.pipeline_read("missing_tab_name")
        self.form.tab_strip.tab_cache.pop("__missing__", None)       # REPLACE pane_cache
        self.form.tab_strip.content_cache.pop(tab_name, None)        # NEW
        self.form.tab_strip.switch_tab(next(iter(self.form.tab_strip.data)))

    def generate_file(self, level):
        file_path = self.form.pipeline_read("missing_tab_path")
        tab_name  = self.form.pipeline_read("missing_tab_name")      # NEW - grab once
        if level == "bare":
            Path(file_path).write_text(self.generate_bare())
        else:
            here = Path(__file__).parent
            template = here / "templates" / f"Template{level}.py"
            print(f"template={template}")
            self.generate_from_template(template)


        self.form.tab_strip.tab_cache.pop("__missing__", None)
        self.form.tab_strip.tab_cache.pop(tab_name, None)
        self.form.tab_strip.content_cache.pop(tab_name, None)
        #print(f"HOT SWAP: tab_cache keys = {list(self.form.tab_strip.tab_cache.keys())}")  # NEW
        #print(f"HOT SWAP: content_cache keys = {list(self.form.tab_strip.content_cache.keys())}")  # NEW
        self.form.tab_strip.switch_tab(tab_name)


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
        file_name = tab_name.replace(" ", "") + ".py"
        lines = [
            "from ipui import *\n\n\n",
            f"class {tab_name.replace(' ', '')}(_BaseTab):\n",
        ]
        for m in methods:
            if m is None: continue
            lines.append(f"\n    def {m}(self, parent):\n")
            lines.append(f"        Body(parent, \"Filename: {file_name}\")\n")
            lines.append(f"        Body(parent, \"Method: {m}\")\n")
            lines.append(f"        Body(parent, \"Add content here!\")\n")
        return "".join(lines)

    def swap_methods(self, template, methods):
        result = template
        for i, method_name in enumerate(methods):
            placeholder = f"method_{i + 1}GameLoop_TAB_BUILDER"
            result = result.replace(placeholder, method_name)
        remaining = self.find_remaining_placeholders(result)
        #result = self.remove_unused_methods(result, remaining)
        return result

    def find_remaining_placeholders(self, text):
        import re
        return re.findall(r'method_\d+GameLoop_TAB_BUILDER', text)

    def fix_class_name(self, text, tab_name):
        return text.replace("class TemplateStarterKit", f"class {tab_name}")


    def generate_from_template(self, template_path):
        methods = self.form.pipeline_read("missing_tab_methods")
        tab_name = self.form.pipeline_read("missing_tab_name")
        file_path = self.form.pipeline_read("missing_tab_path")
        swaps = {
            "TemplateStarterKit": tab_name.replace(" ", ""),
            "method_1_IPUI_TAB_BUILDER": methods[0] if len(methods) > 0 else None,
            "method_2_IPUI_TAB_BUILDER": methods[1] if len(methods) > 1 else None,
            "method_3_IPUI_TAB_BUILDER": methods[2] if len(methods) > 2 else None,
        }
        lines = Path(template_path).read_text(encoding="utf-8").splitlines(keepends=True)
        #print(f"TEMPLATE: {template_path}")        # NEW
        #print(f"SWAPS: {swaps}")                   # NEW
        #print(f"FIRST LINE: {lines[0]!r}")
        #print(f"WRITING TO: {file_path}")          # NEW
        # We should decompose this section out to a discrete method
        out = []
        for line in lines:
            for old, new in swaps.items():
                if old in line and new is not None:
                    line = line.replace(old, new)
            out.append(line)
        Path(file_path).write_text("".join(out), encoding="utf-8")

        self.append_extra_stubs(file_path, methods, 3)


    def append_extra_stubs(self, file_path, methods, covered):
        extras = methods[covered:]
        if not extras:
            return
        lines = []
        for m in extras:
            lines.append(f"\n    def {m}(self, parent):")
            lines.append(f"        Body(parent, 'Method: {m}')")
            lines.append(f"        Body(parent, 'Add content here!')")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(lines) + "\n")