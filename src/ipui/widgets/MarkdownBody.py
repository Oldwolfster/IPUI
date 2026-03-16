# MarkdownBody.py  NEW: Renders a single section from a markdown file
import re
import ipui
from pathlib import Path
from ipui.engine._BaseWidget import _BaseWidget
from ipui.widgets.CodeBox import CodeBox
from ipui.widgets.Spacer import Spacer
from ipui.widgets.Label import Title, Heading, Body
from ipui.utils.general_text import strip_emojis, strip_for_md_toc



class MarkdownBody(_BaseWidget):
    """
    desc:        Renders one section of a .md file using native IPUI widgets.
    when_to_use: Display a specific documentation section inside your app.
    best_for:    Reference detail panes, help content, paired with MarkdownTOC.
    example:     MarkdownBody(parent, data="docs/README.md", text="Quick Start")
    api:         (read-only)
    """

    def build(self):
        if not self.data:
            Body(self, "No markdown file specified.")
            return
        lines = self.read_file()
        section = self.find_section(lines, self.text or "")
        self.render_lines(section)

    def read_file(self):
        package_root = Path(ipui.__file__).parent
        resolved     = package_root / self.data
        try:
            with open(resolved, 'r', encoding='utf-8') as f:
                return f.read().splitlines()
        except FileNotFoundError:
            Body(self, f"Markdown file not found: {resolved}")
            return []

    def find_sectionDeleteMe(self, lines, title):
        clean_title = strip_for_md_toc(title)
        found       = False
        result      = []
        for line in lines:
            if line.startswith("## "):
                if found: break
                heading = strip_for_md_toc(line[3:])
                if heading == clean_title: found = True
                continue
            if found: result.append(line)
        if not result: return [f"Section '{title}' not found."]
        return result

    def find_section(self, lines, slug):
        found  = False
        result = []
        for line in lines:
            if line.startswith("## "):
                if found:
                    break
                heading_slug = self.heading_to_slug(line[3:].strip())
                if heading_slug == slug:
                    found = True
                continue
            if found:
                result.append(line)
        if not result:
            return [f"Section '{slug}' not found."]
        return result

    def heading_to_slug(self, heading):
        cleaned = strip_for_md_toc(heading).lower()
        slug    = cleaned.replace(' ', '-')
        slug    = re.sub(r'[^a-z0-9\-]', '', slug)
        return slug

    def render_lines(self, lines):
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("```"):
                i = self.render_code_block(lines, i)
            elif line.startswith("### "):
                Heading(self, strip_emojis(line[4:]))
            elif line.startswith("# "):
                Title(self, strip_emojis(line[2:]), glow=True)
            elif line.startswith("- ") or line.startswith("* "):
                Body(self, f"  {strip_emojis(line)}")
            elif line.strip() == "---":
                Spacer(self)
            elif line.strip() == "":
                Spacer(self)
            else:
                Body(self, strip_emojis(line))
            i += 1

    def render_code_block(self, lines, start):
        code = []
        i = start + 1
        while i < len(lines) and not lines[i].startswith("```"):
            code.append(lines[i])
            i += 1
        CodeBox(self, data="\n".join(code) + "\n") #the newline ensures code box doesn't treat it as a file.
        return i