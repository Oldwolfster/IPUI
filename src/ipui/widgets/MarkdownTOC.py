    # MarkdownTOC.py  NEW: Table of contents widget for markdown files
import re
import ipui
from pathlib import Path
from ipui.engine._BaseWidget import _BaseWidget
from ipui.widgets.SelectionList import SelectionList
from ipui.widgets.Label import Title
from ipui.utils.general_text import strip_emojis, strip_for_md_toc

class MarkdownTOC(_BaseWidget):
    """
    desc:        Scans a markdown file, extracts TOC entries, renders as single-select list.
    when_to_use: Navigation sidebar for markdown documentation.
    best_for:    Reference tabs, help screens, documentation browsers.
    example:     MarkdownTOC(parent, data="docs/README.md", on_change=handler)
    api:         get_toc(), get_selected()
    """


    def build(self):
        self.toc_titles = []
        self.slug_map   = {}
        lines           = self.read_file()
        entries         = self.extract_toc(lines)

        for title, slug in entries:
            self.toc_titles.append(title)
            self.slug_map[title] = slug

        Title(self, "Table of Contents")
        items = {title: {} for title in self.toc_titles}
        self.sel = SelectionList(self,
            data          = items,
            single_select = True,
            flex_height   = 1,
            on_change     = self.handle_item_changed,
        )
        self.preselect()

    def handle_item_changed(self, selected):
        if self.on_change and selected:
            title = selected[0]
            slug  = self.slug_map.get(title, title)
            self.on_change(slug)

    def preselect(self):
        if not self.initial_value:    return
        for item in self.sel.items:
            if item.text == self.initial_value:
                item.is_selected = True
                item.apply_selection_visual()
                return

    def read_file(self):
        package_root = Path(ipui.__file__).parent
        resolved     = package_root / self.data
        try:
            with open(resolved, 'r', encoding='utf-8') as f:
                return f.read().splitlines()
        except FileNotFoundError:
            return []

    def extract_toc(self, lines):
        explicit     = self.extract_explicit_toc(lines)
        all_headings = self.extract_from_headings(lines)
        if not explicit:
            return all_headings
        explicit_titles = {slug: title for title, slug in explicit}
        result = [("Preamble", "preamble")]
        for title, slug in all_headings:
            display = explicit_titles.get(slug, title)
            result.append((display, slug))
        return result


    def extract_explicit_toc(self, lines):
        in_toc  = False
        entries = [("Preamble", "preamble")]
        for line in lines:
            if line.strip().lower().startswith("## table of contents"):
                in_toc = True
                continue
            if in_toc:
                if line.startswith("## ") or line.startswith("# "):       # REFERENCE
                    break
                if line.startswith("- ["):                                 # REPLACE  (was line.strip().startswith)
                    start = line.index("[") + 1
                    end   = line.index("]")
                    title = line[start:end]
                    slug  = self.extract_slug(line)
                    entries.append((title, slug))
        return entries

    def extract_slug(self, line):
        start = line.index("(#") + 2
        end   = line.index(")", start)
        return line[start:end].strip('-').lower()

    def extract_from_headings(self, lines):
        entries = []
        for line in lines:
            if line.startswith("## "):
                title = strip_for_md_toc(line[3:])
                slug  = self.heading_to_slug(line[3:].strip())
                if title:
                    entries.append((title, slug))
        return entries

    def heading_to_slug(self, heading):
        cleaned = strip_for_md_toc(heading).lower()
        slug    = cleaned.replace(' ', '-')
        slug    = re.sub(r'[^a-z0-9\-]', '', slug)
        return slug


    def get_toc(self):
        return list(self.toc_titles)

    def get_selected(self):
        return self.sel.get_selected()

    def on_item_changed(self, selected):
        if self.on_change and selected:
            self.on_change(selected[0])

    def select_slug(self, slug):
        """Select the TOC entry whose slug matches; fires on_change so Body re-renders."""
        title = self.title_for_slug(slug)
        if not title:
            return False
        for item in self.sel.items:
            item.is_selected = (item.text == title)
            item.apply_selection_visual()
        if self.on_change:
            self.on_change(slug)
        return True

    def title_for_slug(self, slug):
        """Reverse-lookup: slug → title. Returns None if not in this TOC."""
        for title, mapped_slug in self.slug_map.items():
            if mapped_slug == slug:
                return title
        return None