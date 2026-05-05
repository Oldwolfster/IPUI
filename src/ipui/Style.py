# Style.py  Update:  Semantic roles only, imports from Palette
from ipui.utils.Palette import Palette


class Style:
    """
    Semantic roles, tokens, and font data.
    App code references these — never raw Palette values.
    """
    # ============================================================
    # ROLES — Semantic meaning (what app code uses)
    # ============================================================

    # Background & Surface
    COLOR_BACKGROUND         = Palette.GRAY_900
    COLOR_MODAL_BG           = Palette.GRAY_850
    COLOR_PANEL_BG           = Palette.GRAY_800
    COLOR_CARD_BG            = Palette.GRAY_850

    # Text
    COLOR_TEXT                = Palette.GRAY_200
    COLOR_TEXT_SECONDARY      = Palette.GRAY_300
    COLOR_TEXT_MUTED          = Palette.GRAY_400
    COLOR_TEXT_ACCENT         = Palette.ORANGE_FORGE
    COLOR_TEXT_GLOW           = Palette.ORANGE_GLOW

    # Borders
    COLOR_BORDER              = Palette.GRAY_500
    COLOR_BORDER_SUBTLE       = Palette.GRAY_700
    COLOR_CARD_BORDER         = Palette.GRAY_500

    # Buttons
    COLOR_BUTTON_BG           = Palette.GRAY_700
    COLOR_BUTTON_CTA          = Palette.GREEN_DARK
    COLOR_BUTTON_DANGER       = Palette.RED_DARK
    COLOR_BUTTON_SECONDARY    = Palette.BLUE_MUTED
    COLOR_BUTTON_ACCENT       = Palette.ORANGE_BRIGHT
    COLOR_BUTTON_WARNING      = Palette.ORANGE_FORGE

    # Tabs
    COLOR_TAB_BG              = Palette.GRAY_800
    COLOR_TAB_BG_HOVER        = None                    # Computed on init
    COLOR_TAB_BG_ACTIVE       = Palette.GRAY_700
    COLOR_TAB_TEXT            = Palette.GRAY_300
    COLOR_TAB_TEXT_ACTIVE     = Palette.WHITE
    COLOR_TAB_INDICATOR       = Palette.ORANGE_FORGE
    COLOR_TAB_ROW_CURRENT     = Palette.GRAY_800
    COLOR_TAB_STATUS_ERROR    = Palette.ORANGE_DEEP
    COLOR_TAB_STATUS_LINKED   = Palette.BLUE_MUTED

    # Hotkey rendering (Label glow)
    COLOR_HOTKEY              = Palette.ORANGE_BRIGHT
    COLOR_HOTKEY_GLOW         = Palette.ORANGE_DEEP

    # Molten (GlowingLabel)
    COLOR_MOLTEN              = Palette.ORANGE_MOLTEN
    COLOR_MOLTEN_GLOW         = Palette.ORANGE_GLOW

    # Code
    COLOR_CODE_BG             = Palette.GRAY_950

    # Bevel (3D effect)
    COLOR_BEVEL_LIGHT         = Palette.GRAY_600
    COLOR_BEVEL_DARK          = Palette.GRAY_950

    # Bevel Sets
    COLOR_BEVEL_RAISED_LT     = Palette.GRAY_600
    COLOR_BEVEL_RAISED_DK     = Palette.BLACK
    COLOR_BEVEL_SUNKEN_LT     = Palette.GRAY_700
    COLOR_BEVEL_SUNKEN_DK     = Palette.GRAY_975
    COLOR_BEVEL_HOT_LT        = Palette.ORANGE_BRIGHT
    COLOR_BEVEL_HOT_DK        = Palette.ORANGE_DEEP

    # Refined Bevel Roles
    COLOR_BEVEL_RAISED_LIGHT  = Palette.GRAY_600
    COLOR_BEVEL_RAISED_DARK   = Palette.GRAY_990
    COLOR_BEVEL_SUNKEN_INNER  = Palette.GRAY_975
    COLOR_BEVEL_SUNKEN_OUTER  = Palette.GRAY_700
    COLOR_BEVEL_HOT_LIGHT     = Palette.ORANGE_FORGE
    COLOR_BEVEL_HOT_DARK      = Palette.ORANGE_DEEP

    # ============================================================
    # TOKENS — Spacing (multiplier-based)
    # ============================================================
    TOKEN_MULTIPLIER          = 2
    TOKEN_PAD                 = TOKEN_MULTIPLIER * 8
    TOKEN_PAD_TIGHT           = TOKEN_MULTIPLIER * 1
    TOKEN_GAP                 = TOKEN_MULTIPLIER * 3
    TOKEN_GAP_TIGHT           = TOKEN_MULTIPLIER * 2
    TOKEN_BORDER              = TOKEN_MULTIPLIER * 1
    TOKEN_SCROLLBAR           = 12
    TOKEN_CORNER_RADIUS       = 4

    # User preference (0.0 to 1.0, future slider target)
    FONT_SCALE                = .369
    # Font proportions (relative to screen height)
    FONT_RATIO_BANNER         = .1969
    FONT_RATIO_TITLE          = .0889
    FONT_RATIO_HEADING        = .0696
    FONT_RATIO_BODY           = .0636
    FONT_RATIO_DETAIL         = .0590
    FONT_RATIO_MONO           = .0396



    # Initialized by MgrFont
    FONT_BANNER               = None
    FONT_TITLE                = None
    FONT_HEADING              = None
    FONT_BODY                 = None
    FONT_DETAIL               = None
    FONT_MONO                 = None
    FONT_MONO_BODY            = None