# MarkdownBody.py  Update: silent-strip comments/images, inline marker stripping, blockquotes-as-Card, dead code removed
import re
import ipui
from pathlib import Path

from ipui import Style, Plate, Button, CENTER, Row, Image, Icon, CardRow
from ipui.engine._BaseWidget import _BaseWidget
from ipui.widgets.Card    import Card
from ipui.widgets.CodeBox import CodeBox
from ipui.widgets.Spacer  import Spacer
from ipui.widgets.Label import Title, Heading, Body, Banner
from ipui.utils.general_text import strip_emojis, strip_for_md_toc
import re


# Pre-compile once at module load — render_lines is called per file render.
RX_HTML_COMMENT  = re.compile(r'<!--.*?-->')
RX_IMAGE_LINE    = re.compile(r'^\s*!\[[^\]]*\]\([^)]*\)\s*$')
RX_BOLD          = re.compile(r'\*\*([^*]+)\*\*')
RX_ITALIC        = re.compile(r'(?<!\*)\*([^*]+)\*(?!\*)')
RX_INLINE_CODE   = re.compile(r'`([^`]+)`')
RX_LINK_LINE     = re.compile(r'^\s*-?\s*\[([^\]]+)\]\(#([^)]+)\)\s*$')
RX_BADGE_URL     = re.compile(r'shields\.io/badge/([^)]+)')

class MarkdownBody(_BaseWidget):
    """
    desc:        Renders one section of a .md file using native IPUI widgets.
    when_to_use: Display a specific documentation section inside your app.
    best_for:    Reference detail panes, help content, paired with MarkdownTOC.
    example:     MarkdownBody(parent, data="docs/README.md", text="quick-start")
    api:         (read-only)
    """

    def build(self):
        if not self.data:
            Body(self, "No markdown file specified.")
            return
        self.gap = Style.TOKEN_GAP * 2
        lines   = self.read_file()
        self.text = self.text or "preamble" #hhmm
        section = self.find_section(lines, self.text or "")
        self.render_nav_header()
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

    # ══════════════════════════════════════════════════════════════
    # SECTION FINDING — only h2 (## ) headings are addressable
    # ══════════════════════════════════════════════════════════════

    def find_section(self, lines, slug):

        if preamble := self.find_preamble(slug, lines): return preamble
        found  = False
        result = []
        for line in lines:
            if line.startswith("## "):
                if found:
                    break
                if self.heading_to_slug(line[3:].strip()) == slug:
                    found = True
                continue
            if found:
                result.append(line)
        if not result:
            return [f"Section '{slug}' not found."]
        return result

    def find_preamble(self, slug, lines):
        if slug != "preamble":
            return None
        result = []
        started = False
        for line in lines:
            if line.startswith("# ") and not started:
                started = True
                continue
            if started and line.startswith("## "):
                break
            if started:
                result.append(line)
        return result or ["No preamble content found."]



    def heading_to_slug(self, heading):
        cleaned = strip_for_md_toc(heading).lower()
        slug    = cleaned.replace(' ', '-')
        slug    = re.sub(r'[^a-z0-9\-]', '', slug)
        return slug

    # ══════════════════════════════════════════════════════════════
    # RENDERING — top-down dispatch, one method per concern
    # ══════════════════════════════════════════════════════════════

    def render_nav_header(self):
        toc = self.find_toc()
        if not toc:
            return
        titles = toc.get_toc()
        slugs = [toc.slug_map[t] for t in titles]
        idx = slugs.index(self.text) if self.text in slugs else -1
        has_prev = idx > 0
        has_next = 0 <= idx < len(slugs) - 1
        row = Row(self, justify_spread=True)
        bt  = Button(row,
               enabled=has_prev,
               on_click=(lambda: self.goto(slugs[idx - 1])) if has_prev else None)
        Icon(bt,"Left")
        title = titles[idx] if idx >= 0 else self.text or ""
        Banner(row, title, flex_width=1, text_align=CENTER, glow=True)
        bt  = Button(row,
               enabled=has_next,
               on_click=(lambda: self.goto(slugs[idx + 1])) if has_next else None)
        Icon(bt, "Right")

    def render_lines(self, lines):
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("```"):
                i = self.render_code_block(lines, i)
            elif line.lstrip().startswith(">"):
                i = self.render_blockquote(lines, i)
            elif self.is_skippable(line):
                pass
            elif self.is_badge_line(line):                          # NEW
                i = self.render_badges(lines, i)

            elif RX_IMAGE_LINE.match(line):
                self.render_image(line)
            elif RX_LINK_LINE.match(line):
                self.render_link_line(line)

            elif line.startswith("### "):
                Heading(self, self.clean_inline(line[4:]))
            elif line.startswith("# "):
                Title(self, self.clean_inline(line[2:]), glow=True)
            elif line.startswith("- ") or line.startswith("* "):
                Body(self, f"  {self.clean_inline(line[2:])}")
            elif line.strip() == "---":
                Spacer(self)
            elif line.strip() == "":
                Spacer(self)
            else:
                Body(self, self.clean_inline(line))
            i += 1

    def render_link_line(self, line):
        """Whole-line markdown link → CTA Button that calls goto(slug)."""
        m = RX_LINK_LINE.match(line)
        text = self.clean_inline(m.group(1))
        slug = m.group(2).lower()

        Button(self, f"    {text}     ", color_bg=Style.COLOR_BUTTON_CTA,
               on_click=lambda s=slug: self.goto(s))

    def is_skippable(self, line):
        """HTML comments are silently dropped."""
        stripped = line.strip()
        if not stripped:                       return False
        if stripped.startswith("<!--"):        return True
        return False

    def is_badge_line(self, line):
        return RX_IMAGE_LINE.match(line) and "shields.io/badge" in line

    def clean_inline(self, text):
        """Strip emojis, HTML comments, and inline markdown markers; keep the words."""
        text = strip_emojis(text)
        text = RX_HTML_COMMENT.sub('', text)
        text = RX_BOLD       .sub(r'\1', text)
        text = RX_INLINE_CODE.sub(r'\1', text)
        text = RX_ITALIC     .sub(r'\1', text)
        return text

    def render_blockquote(self, lines, start):
        """Accumulate consecutive `> ` lines into a single Card."""
        card = Plate(self, color_bg=Style_quote_bg())
        card.gap = Style.TOKEN_GAP * 2
        i    = start
        while i < len(lines) and lines[i].lstrip().startswith(">"):
            quoted = lines[i].lstrip()[1:].lstrip()      # strip leading '>' + one optional space
            if quoted == "":
                Spacer(card)
            else:
                Body(card, self.clean_inline(quoted))
            i += 1
        return i - 1   # outer loop will += 1


    def render_image(self, line):
        match = re.search(r'!\[[^\]]*\]\(([^)]+)\)', line)
        if not match:
            return
        raw_path = match.group(1)
        resolved = self.resolve_image_path(raw_path)
        Image(Card(self,pad=1), resolved)
        #Image(self, resolved)

    def render_code_block(self, lines, start):
        code = []
        i    = start + 1
        while i < len(lines) and not lines[i].startswith("```"):
            code.append(lines[i])
            i += 1
        card = Card(self, pad=0)
        cb= CodeBox(card, data="\n".join(code) + "\n")   # trailing newline so CodeBox doesn't think it's a path
        #cb.parent.gap = Style.TOKEN_GAP * 2
        return i



    def resolve_image_path(self, raw_path):
        from ipui.utils.MgrPkgPath import MgrPkgPath
        from pathlib import Path
        if "raw.githubusercontent.com" in raw_path:
            for marker in ("src/ipui/", "main/"):
                if marker in raw_path:
                    raw_path = raw_path.split(marker, 1)[1]
                    break
        md_dir = MgrPkgPath.path(self.data).parent
        relative = md_dir / raw_path
        if relative.exists():
            return str(relative)
        pkg = MgrPkgPath.path(raw_path)
        if pkg.exists():
            return str(pkg)
        return raw_path



    def find_toc(self):
        """Locate a MarkdownTOC sibling-or-anywhere in this form.
        Returns the TOC instance, or None if zero or ambiguous (multiple TOCs)."""
        from ipui.widgets.MarkdownTOC import MarkdownTOC
        if not self.form:
            return None
        tocs = [w for w in self.form.widget_registry.values()
                if isinstance(w, MarkdownTOC)]
        if len(tocs) == 1:
            return tocs[0]
        return None

    def goto(self, slug):
        """Navigate to a section by slug. Updates TOC selection if a TOC is in the form."""
        toc = self.find_toc()
        if toc:
            toc.select_slug(slug)        # fires on_change → owner pane → body re-renders
            return
        self.text = slug                  # no TOC: just rebuild ourselves
        self.clear_children()
        self.build()








############## BADGES ###################
    def render_badges(self, lines, start):

        i   = start
        self.did_badge_card = False
        card=None
        while i < len(lines) and self.is_badge_line(lines[i]):
            if self.did_badge_card==False:
                self.did_badge_card=True
                Body(self, "")
                r2 = Row(self)
                pt= Plate(r2)
                Spacer(r2)
                row = Row(pt)
                card=CardRow(row ,gap=25)
                Spacer(row)
                Body(self, "")
            #self.render_one_badge(row, lines[i])
            self.render_one_badge(card, lines[i])
            i += 1
        return i - 1

    def render_one_badge(self, parent, line):
        m = RX_BADGE_URL.search(line)
        if not m:
            return
        parts = self.parse_badge_parts(m.group(1))
        if not parts:
            return
        label, value, color = parts

        row=Row(Plate(parent))
        Icon(row,"Shield",data=3) #Data scales the icon
        Button(row, f"{label} {value}", color_bg=self.badge_color(color))

    def parse_badge_parts(self, path):
        from urllib.parse import unquote
        path  = unquote(path)
        path  = path.replace("--", "\x00")
        parts = path.split("-")
        parts = [p.replace("\x00", "-") for p in parts]
        if len(parts) < 3:
            return None
        color = parts[-1]
        value = parts[-2]
        label = "-".join(parts[:-2])
        return label, value, color

    def badge_color(self, color):
        colors = {
            "blue":   (54, 114, 181),
            "orange": (222, 120, 30),
            "green":  (68, 153, 72),
            "red":    (200, 60, 60),
            "yellow": (200, 180, 40),
        }
        return colors.get(color, Style.COLOR_BUTTON_BG)



def Style_quote_bg():
    """Slightly different bg so blockquote card reads as 'quoted', not 'random card'."""
    from ipui.Style import Style
    return Style.COLOR_TAB_BG