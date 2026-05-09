# Image.py  NEW: Display an image from a file path (user or framework-bundled)
from ipui.engine._BaseWidget import _BaseWidget
from ipui.utils.EZ import EZ
from pathlib import Path
import pygame


class Image(_BaseWidget):
    """
    desc:        Displays an image from a file path.
    when_to_use: Photos, logos, diagrams, any visual asset.
    best_for:    Embedding images in cards, panes, or any container.
    example:     Image(parent, "photos/cat.png")
    api:         (display only — no custom methods)
    """
    def build(self):
        path              = self.resolve_path(self.text)
        self.surface_raw  = pygame.image.load(str(path)).convert_alpha()
        self.surface_zoom = None
        self.encroach_x   = True
        self.encroach_y   = True
        self.pad=-10
        self.my_surface   = self.surface_raw
        self.zoom         = 1.0
        self.private_cached_size = None

    def draw(self, surface):
        if self.rect and self.surface_zoom is None:
            self.scale_to_fit()
        super().draw(surface)

    def scale_to_fit(self):
        inner_w = self.rect.width  - self.frame_x
        inner_h = self.rect.height - self.frame_y
        if inner_w <= 0 or inner_h <= 0: return
        raw_w, raw_h = self.surface_raw.get_size()
        scale   = min(inner_w / raw_w, inner_h / raw_h) * self.zoom
        new_w   = max(1, int(raw_w * scale))
        new_h   = max(1, int(raw_h * scale))
        self.surface_zoom        = pygame.transform.smoothscale(self.surface_raw, (new_w, new_h))
        self.my_surface          = self.surface_zoom
        self.private_cached_size = (new_w, new_h)

    def resolve_path(self, text):
        direct = Path(text)
        if direct.exists():
            return direct
        from ipui.utils.MgrPkgPath import MgrPkgPath
        pkg = MgrPkgPath.path(text)
        if pkg.exists():
            return pkg
        EZ.err(
            f"Image file not found: '{text}'\n"
            f"Looked in:\n"
            f"  1) {direct.resolve()}\n"
            f"  2) {pkg}\n"
            f"Provide a valid relative, absolute, or package-relative path.\n"
            f'Example: Image(parent, "photos/cat.png")',
            origin="Image(", exc_type=FileNotFoundError
        )