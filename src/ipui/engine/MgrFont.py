# ipui/engine/MgrFont.py

import pygame
import os

from ipui.Style import Style


class MgrFont:
    """
    Font manager - handles font loading with cascading fallbacks.
    Strategy: Bundled TTF → System fonts → Pygame default
    """

    # Font paths (relative to project root)
    #FONT_DIR = "src/assets/fonts"
    FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
    FONT_REGULAR = "Roboto-Regular.ttf"
    FONT_BOLD = "Roboto-Bold.ttf"
    FONT_LIGHT = "Roboto-Light.ttf"

    # System font fallbacks (covers Windows/Mac/Linux)
    SYSTEM_FONTS_REGULAR = [
        'Roboto', 'Arial', 'Helvetica', 'DejaVu Sans', 'Segoe UI',
        'Liberation Sans', 'Noto Sans', 'Ubuntu', 'Cantarell', 'Verdana'
    ]
    SYSTEM_FONTS_BOLD = [
        'Roboto Bold', 'Arial Bold', 'Helvetica Bold', 'DejaVu Sans Bold',
        'Segoe UI Bold', 'Liberation Sans Bold', 'Noto Sans Bold',
        'Ubuntu Bold', 'Cantarell Bold', 'Verdana Bold'
    ]
    SYSTEM_FONTS_LIGHT = [
        'Roboto Light', 'Helvetica Light', 'Segoe UI Light',
        'Noto Sans Light', 'Ubuntu Light', 'Arial'
    ]
    SYSTEM_FONTS_MONO = [
        'Consolas', 'Courier New', 'DejaVu Sans Mono',
        'Liberation Mono', 'Noto Sans Mono', 'Ubuntu Mono',
        'Menlo', 'Monaco', 'monospace'
    ]
    mono_font_source = None
    # Cached fonts
    regular_font_source = None
    bold_font_source = None
    light_font_source = None
    font_cache = {}


    @classmethod
    def init(cls):
        """Initialize fonts from Style proportions using physical screen height."""

        physical_h = pygame.display.Info().current_h

        cls.regular_font_source = cls.load_font_source(cls.FONT_REGULAR, cls.SYSTEM_FONTS_REGULAR, "Regular")
        cls.bold_font_source = cls.load_font_source(cls.FONT_BOLD, cls.SYSTEM_FONTS_BOLD, "Bold")
        cls.light_font_source = cls.load_font_source(cls.FONT_LIGHT, cls.SYSTEM_FONTS_LIGHT, "Light")
        cls.mono_font_source = cls.load_font_source("", cls.SYSTEM_FONTS_MONO, "Mono")

        scale = Style.font_scale

        Style.FONT_BANNER = cls.get_font_for_height(physical_h * scale * Style.FONT_RATIO_BANNER, 'bold')
        Style.FONT_HEADING = cls.get_font_for_height(physical_h * scale * Style.FONT_RATIO_HEADING, 'bold')
        Style.FONT_TITLE = cls.get_font_for_height(physical_h * scale * Style.FONT_RATIO_TITLE, 'bold')
        Style.FONT_BODY = cls.get_font_for_height(physical_h * scale * Style.FONT_RATIO_BODY, 'regular')
        Style.FONT_DETAIL = cls.get_font_for_height(physical_h * scale * Style.FONT_RATIO_DETAIL, 'regular')
        Style.FONT_MONO = cls.get_font_for_height(physical_h * scale * Style.FONT_RATIO_MONO, 'mono')

    @classmethod
    def load_font_source(cls, ttf_filename, system_font_names, weight_name):
        """
        Try to load font source in order: bundled TTF → system font → None (pygame default).
        Returns: font source (filepath, font name, or None)
        """
        # Try bundled TTF
        ttf_path = os.path.join(cls.FONT_DIR, ttf_filename)
        if ttf_filename and os.path.exists(ttf_path): 
            print(f"✓ Loaded {weight_name} font: {ttf_path}")
            return ttf_path
        else: print ("Font folder not found")

        # Try system fonts
        for font_name in system_font_names:
            if pygame.font.match_font(font_name):
                print(f"✓ Using system font for {weight_name}: {font_name}")
                return font_name

        # Fallback to pygame default
        print(f"⚠ {weight_name} font not found - using pygame default (limited unicode)")
        return None

    @classmethod
    def get_font_for_height(cls, target_height, weight='regular'):
        """
        Get font that matches target height.
        Uses binary search for efficiency.
        """
        # Select font source based on weight
        if weight == 'bold':
            source = cls.bold_font_source
        elif weight == 'light':
            source = cls.light_font_source
        elif weight == 'mono':  # NEW
            source = cls.mono_font_source  # NEW
        else:
            source = cls.regular_font_source

        # Check cache
        cache_key = (source, int(target_height), weight)
        if cache_key in cls.font_cache:
            return cls.font_cache[cache_key]

        # Binary search for optimal size
        min_size, max_size = 8, 200
        best_font = None

        while min_size <= max_size:
            mid = (min_size + max_size) // 2
            font = cls.create_font(source, mid)

            if font.get_height() >= target_height:
                best_font = font
                max_size = mid - 1
            else:
                min_size = mid + 1

        # Fallback if binary search fails
        if best_font is None:
            best_font = cls.create_font(source, 48)

        cls.font_cache[cache_key] = best_font
        return best_font

    @classmethod
    def create_font(cls, source, size):
        """Create pygame font from source (filepath, font name, or None)."""
        if source is None:
            # Pygame default
            return pygame.font.Font(None, size)
        elif os.path.exists(source):
            # TTF file
            return pygame.font.Font(source, size)
        else:
            # System font name
            font_path = pygame.font.match_font(source)
            if font_path:
                return pygame.font.Font(font_path, size)
            else:
                # Fallback to default if system font disappeared
                return pygame.font.Font(None, size)