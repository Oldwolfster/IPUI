# ipui/engine/MgrColor.py
from ipui.Style import Style


class MgrColor:
    """
    Color manager - handles hover color computation and caching.
    Provides three algorithms for testing, uses HSL-based by default.
    """

    hover_cache = {}

    @classmethod
    def init(cls):
        """Compute and store all derived colors on Style."""

        Style.COLOR_BUTTON_HOVER = cls.compute_hover(Style.COLOR_BUTTON_BG)
        Style.COLOR_TAB_BG_HOVER = cls.compute_hover(Style.COLOR_TAB_BG)

    @classmethod
    def compute_hover(cls, base_rgb):
        """
        Compute hover color with caching.
        Uses HSL algorithm by default (best visual results).
        """
        if base_rgb in cls.hover_cache:
            return cls.hover_cache[base_rgb]

        result = cls.compute_hover_hsl(base_rgb)
        cls.hover_cache[base_rgb] = result
        return result

    # ============================================================
    # Algorithm 1: Luminance-based with adaptive delta
    # ============================================================
    @classmethod
    def compute_hover_luminance(cls, base_rgb, strength=0.15):
        """
        Brighten dark colors, darken light colors.
        Uses luminance calculation with adaptive strength.
        """
        r, g, b = base_rgb
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        direction = 1 if lum < 128 else -1
        delta = direction * strength * (1 - abs(lum / 255 - 0.5) * 2)

        factor = 1 + delta
        return (
            int(min(255, max(0, r * factor))),
            int(min(255, max(0, g * factor))),
            int(min(255, max(0, b * factor)))
        )

    # ============================================================
    # Algorithm 2: HSL boost away from extremes
    # ============================================================
    @classmethod
    def compute_hover_hsl_simple(cls, base_rgb):
        """
        Adjust lightness in HSL space.
        Boosts light colors up, dark colors down.
        """
        h, s, l = cls.rgb_to_hsl(base_rgb)
        l = min(0.95, max(0.05, l + 0.12 if l < 0.5 else l - 0.12))
        return cls.hsl_to_rgb(h, s, l)

    # ============================================================
    # Algorithm 3: HSL with luminance-based direction (DEFAULT)
    # ============================================================
    @classmethod
    def compute_hover_hsl(cls, base_rgb):
        """
        Best results: uses luminance to determine direction,
        then adjusts lightness in HSL space for smooth color shifts.
        """
        r, g, b = base_rgb
        lum = 0.299 * r + 0.587 * g + 0.114 * b

        direction = 1 if lum < 128 else -1
        delta = 0.12 * direction

        h, s, l = cls.rgb_to_hsl(base_rgb)
        l = min(0.95, max(0.05, l + delta))
        return cls.hsl_to_rgb(h, s, l)

    # ============================================================
    # Color Space Conversion
    # ============================================================

    @classmethod
    def rgb_to_hsl(cls, rgb):
        """Convert RGB (0-255) to HSL (h: 0-360, s: 0-1, l: 0-1)"""
        r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2.0

        if max_c == min_c:
            h = s = 0.0
        else:
            d = max_c - min_c
            s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)

            if max_c == r:
                h = (g - b) / d + (6.0 if g < b else 0.0)
            elif max_c == g:
                h = (b - r) / d + 2.0
            else:
                h = (r - g) / d + 4.0
            h /= 6.0

        return h * 360, s, l

    @classmethod
    def hsl_to_rgb(cls, h, s, l):
        """Convert HSL (h: 0-360, s: 0-1, l: 0-1) to RGB (0-255)"""
        h = h / 360.0

        def hue_to_rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1 / 6: return p + (q - p) * 6 * t
            if t < 1 / 2: return q
            if t < 2 / 3: return p + (q - p) * (2 / 3 - t) * 6
            return p

        if s == 0:
            r = g = b = l
        else:
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1 / 3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1 / 3)

        return (int(r * 255), int(g * 255), int(b * 255))

    @classmethod
    def clear_cache(cls):
        """Clear hover color cache (useful for testing different algorithms)"""
        cls.hover_cache.clear()

    @classmethod
    def compute_darken(cls, base_rgb, amount=0.12):
        """Darken a color by reducing lightness."""
        h, s, l = cls.rgb_to_hsl(base_rgb)
        l = max(0.05, l - amount)
        return cls.hsl_to_rgb(h, s, l)

    @classmethod
    def compute_disabled(cls, base_rgb):
        """Disabled = original × 0.5 + 30 gray bias. Muted but recognizable."""
        key = ("disabled", base_rgb)

        if key in cls.hover_cache:
            return cls.hover_cache[key]
        r, g, b = base_rgb
        result = (
            int(min(255, max(0, r * 0.5 + 30))),
            int(min(255, max(0, g * 0.5 + 30))),
            int(min(255, max(0, b * 0.5 + 30))),
        )
        cls.hover_cache[key] = result
        return result


    @staticmethod
    def apply_bevel(widget, flavor="raised"):
        if flavor == "sunken":
            widget.border_top       = Style.COLOR_BEVEL_SUNKEN_DK
            widget.border_left = Style.COLOR_BEVEL_SUNKEN_DK
            widget.border_bottom = Style.COLOR_BEVEL_SUNKEN_LT
            widget.border_right = Style.COLOR_BEVEL_SUNKEN_LT
        elif flavor == "hot":
            widget.border_top = Style.COLOR_BEVEL_HOT_LT
            widget.border_left = Style.COLOR_BEVEL_HOT_LT
            widget.border_bottom = Style.COLOR_BEVEL_HOT_DK
            widget.border_right = Style.COLOR_BEVEL_HOT_DK
        else:  # Default "raised"
            widget.border_top = Style.COLOR_BEVEL_RAISED_LT
            widget.border_left = Style.COLOR_BEVEL_RAISED_LT
            widget.border_bottom = Style.COLOR_BEVEL_RAISED_DK
            widget.border_right = Style.COLOR_BEVEL_RAISED_DK

    @classmethod
    def compute_bevel(cls, base_rgb, flavor="raised"):
        """Compute bevel colors relative to widget's own background."""
        if flavor == "sunken":
            return cls.compute_darken(base_rgb, 0.15), cls.compute_darken(base_rgb, 0.15), \
                cls.compute_hover(base_rgb), cls.compute_hover(base_rgb)
        else:  # raised
            return cls.compute_hover(base_rgb), cls.compute_hover(base_rgb), \
                cls.compute_darken(base_rgb, 0.20), cls.compute_darken(base_rgb, 0.20)