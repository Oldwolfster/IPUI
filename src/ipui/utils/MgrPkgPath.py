# MgrAssets.py  NEW: Single source of truth for resolving package-relative file paths
# Replaces three different ad-hoc patterns scattered across IconCache, MgrFont, MarkdownTOC.

from pathlib import Path
import ipui


class MgrPkgPath:
    """
    desc:        Resolves any path relative to the installed ipui package root.
    when_to_use: Anywhere you need to load a bundled asset (icon, font, db, doc, etc).
    best_for:    Wheel-safe path resolution. CWD-independent. One line, no dirname math.
    example:     path = MgrAssets.path("assets/sample_db/Showdown.db")
    api:         path(rel), exists(rel), root()
    """

    @classmethod
    def root(cls):
        return Path(ipui.__file__).parent

    @classmethod
    def path(cls, rel):
        """Returns Path object — for path math (joining, parent, exists)."""
        return cls.root() / rel

    @classmethod
    def as_str(cls, rel):
        """Returns str — for libraries that explicitly need a string path.
            named as_str to avoid shadowing the builtin in side the class.
        """
        return str(cls.path(rel))

    @classmethod
    def exists(cls, rel):
        return cls.path(rel).exists()