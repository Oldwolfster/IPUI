# MarkdownView.py  NEW: Markdown file viewer widget
import ipui
from ipui.engine._BaseWidget import _BaseWidget
from ipui.Style import Style
from ipui.widgets.CodeBox import CodeBox
from ipui.widgets.Spacer import Spacer
from ipui.widgets.Label import Title, Heading, Body


class MarkdownView(_BaseWidget):
    """
    desc:        Renders a .md file using native IPUI widgets.
    when_to_use: Display README or documentation inside your app.
    best_for:    Reference tabs, help screens, about pages.
    example:     MarkdownView(parent, data="README.md")
    api:         (read-only)
    """

    def build(self):
        if not self.data:
            Body(self, "No markdown file specified.")
            return
        lines = self.read_file()
        self.parse(lines)

    def read_file(self):
        import os
        from pathlib import Path

        cwd          = Path(os.getcwd())
        requested    = Path(self.data)
        package_root = Path(ipui.__file__).parent
        resolved     = package_root / self.data


        print(f"[MarkdownView] CWD:       {cwd}")
        print(f"[MarkdownView] Requested: {requested}")
        print(f"[MarkdownView] Resolved:  {resolved}")
        print(f"[MarkdownView] Exists:    {resolved.exists()}")

        try:
            with open(self.data, 'r', encoding='utf-8') as f: #resolved
                return f.read().splitlines()
        except FileNotFoundError as e:
            Body(self, f"Markdown file not found: {resolved}")
            Body(self, f"CWD was: {cwd}")
            return []

    def parse(self, lines):
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("```"):
                i = self.parse_code_block(lines, i)
            elif line.startswith("### "):
                Heading(self, line[4:])
            elif line.startswith("## "):
                Heading(self, line[3:], glow=True)
            elif line.startswith("# "):
                Title(self, line[2:], glow=True)
            elif line.startswith("- ") or line.startswith("* "):
                Body(self, f"  {line}")
            elif line.strip() == "":
                Spacer(self)
            else:
                Body(self, line)
            i += 1

    def parse_code_block(self, lines, start):
        code = []
        i = start + 1
        while i < len(lines) and not lines[i].startswith("```"):
            code.append(lines[i])
            i += 1
        CodeBox(self, data="\n".join(code))
        return i