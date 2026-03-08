import pygame
import time
from ipui.engine._BaseWidget import _BaseWidget
from ipui.Style import Style


class ProjectListItem(_BaseWidget):
    """
    desc:        Custom widget Project card showing name, path, date, and run count. Clickable.
    when_to_use: Listing saved projects for selection.
    best_for:    The Home tab project browser.
    example:     item = ProjectListItem(parent, data=project_info)
    api:         (display only — click via on_click)
    """
    def build(self):
        self.project_info   = self.data
        self.my_name        = f"ProjectListItem: {self.project_info.name}"
        self.font           = self.font or Style.FONT_BODY
        self.font_detail    = Style.FONT_DETAIL
        self.color_bg       = Style.COLOR_CARD_BG
        self.color_txt      = Style.COLOR_TEXT
        name_surf           = self.font.render(self.project_info.name, True, self.color_txt)
        detail_surf         = self.font_detail.render(self.build_detail_string(), True, Style.COLOR_TEXT_MUTED)
        self.my_surface     = self.composite(name_surf, detail_surf)

    def composite(self, name_surf, detail_surf):
        w    = max(name_surf.get_width(), detail_surf.get_width())
        h    = name_surf.get_height() + detail_surf.get_height() + 4
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.blit(name_surf,   (0, 0))
        surf.blit(detail_surf, (0, name_surf.get_height() + 4))
        return surf

    def build_detail_stringOrig(self):
        p   = self.project_info
        pct = self.completion_percent()
        if   pct is not None:   runs = f"{p.run_count}/{p.expected_runs} ({pct}%)"
        elif p.run_count > 0:   runs = f"{p.run_count} runs"
        else:                   runs = "empty"
        batches = f"{p.batch_count} bat" if p.batch_count else "no batches"
        when    = self.format_time_ago(p.mtime)
        return f"{runs} | {batches} | {when}"

    def build_detail_string(self):
        import os
        size = os.path.getsize(self.project_info.path)
        kb = size / 1024
        when = self.format_time_ago(self.project_info.mtime)
        return f"{kb:.1f} KB | {when}"


    def completion_percent(self):
        if self.project_info.expected_runs == 0:
            return None
        return int(self.project_info.run_count / self.project_info.expected_runs * 100)

    def format_time_ago(self, mtime):
        delta = time.time() - mtime
        if   delta < 60:        return "just now"
        elif delta < 3600:      return f"{int(delta / 60)}m ago"
        elif delta < 86400:     return f"{int(delta / 3600)}h ago"
        elif delta < 172800:    return "yesterday"
        elif delta < 2592000:   return f"{int(delta / 86400)}d ago"
        else:                   return time.strftime("%b %d", time.localtime(mtime))