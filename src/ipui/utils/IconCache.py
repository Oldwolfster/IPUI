import os
import pygame


class IconCache:
    icons    = {}
    icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")

    @classmethod
    def get(cls, name, size):
        key = (name, size)
        if key not in cls.icons:
            path = os.path.join(cls.icon_dir, f"{name}.png")
            surf = pygame.image.load(path).convert_alpha()
            cls.icons[key] = pygame.transform.smoothscale(surf, (size, size))
        return cls.icons[key]