class Style:
    """
    Pure style data - palette, roles, and tokens.
    No logic - delegates to MgrFont and MgrColor.
    """

    # ============================================================
    # SCREEN
    # ============================================================
    SCREEN_WIDTH            = 1900
    SCREEN_HEIGHT           = 900

    # ============================================================
    # PALETTE - Raw RGB tuples (the paint tubes)
    # ============================================================

    # Grays (dark to light)
    COLOR_PAL_GRAY_950      = (15, 15, 18)      # Near black
    COLOR_PAL_GRAY_900      = (25, 25, 30)      # Darkest background
    COLOR_PAL_GRAY_850      = (35, 35, 40)      # Panel background
    COLOR_PAL_GRAY_800      = (45, 45, 52)      # Elevated surface
    COLOR_PAL_GRAY_700      = (60, 60, 70)      # Inactive elements
    COLOR_PAL_GRAY_600      = (80, 80, 90)      # Hover states
    COLOR_PAL_GRAY_500      = (100, 100, 110)   # Borders
    COLOR_PAL_GRAY_400      = (130, 130, 140)   # Muted text
    COLOR_PAL_GRAY_300      = (160, 160, 170)   # Secondary text
    COLOR_PAL_GRAY_200      = (200, 200, 205)   # Primary text
    COLOR_PAL_GRAY_100      = (230, 230, 235)   # Bright text
    COLOR_PAL_WHITE         = (255, 255, 255)   # Pure white
    COLOR_PAL_BLACK         = (  0,   0,   0)   # Pure Black

    # Orange - Brand/Focus/Selection ("glow of the forge")
    COLOR_PAL_ORANGE_DEEP   = (180,  90,  20)     # Dark accent
    COLOR_PAL_ORANGE_FORGE  = (230, 140,  30)    # Primary brand orange
    COLOR_PAL_ORANGE_BRIGHT = (255, 180,  60)    # Highlighted/glow
    COLOR_PAL_ORANGE_MOLTEN = (255,  50,   0)      # Red-orange for text
    COLOR_PAL_ORANGE_GLOW   = (255, 150,  50)    # Glow effect

    # Green - Primary Actions
    COLOR_PAL_GREEN_DARK    = (45, 120, 45)     # Button background
    COLOR_PAL_GREEN_SECOND  = (45, 140, 90)
    #COLOR_PAL_GREEN_ACTION  = (60, 160, 60)     # Primary action
    #COLOR_PAL_GREEN_HOVER   = (80, 190, 80)     # Hover state
    #COLOR_PAL_GREEN_BORDER  = (100, 200, 100)   # Button border

    COLOR_PAL_GREEN_DARK_DISABLED = (330, 50, 30)
    COLOR_PAL_GREEN_SECOND_DISABLED = (30, 55, 45)

    # (55, 75, 65) — OVERRIDE DISABLED GREEN



    # Red - Danger/Error (future use)
    COLOR_PAL_RED_DARK      = (140, 40, 40)
    COLOR_PAL_RED_PRIMARY   = (200, 60, 60)

    # Blue - Info only (demoted, not primary UI)
    COLOR_PAL_BLUE_MUTED = (70, 90, 130)

    # ============================================================
    # ROLES - Semantic meaning (what app code uses)
    # ============================================================

    # Background & Surface
    COLOR_BACKGROUND        = COLOR_PAL_GRAY_900
    COLOR_MODAL_BG          = COLOR_PAL_GRAY_850
    COLOR_PANEL_BG          = COLOR_PAL_GRAY_800
    COLOR_CARD_BG           = COLOR_PAL_GRAY_850

    # Text
    COLOR_TEXT              = COLOR_PAL_GRAY_200
    COLOR_TEXT_SECONDARY    = COLOR_PAL_GRAY_300
    COLOR_TEXT_MUTED        = COLOR_PAL_GRAY_400
    COLOR_TEXT_ACCENT       = COLOR_PAL_ORANGE_FORGE
    COLOR_TEXT_GLOW         = COLOR_PAL_ORANGE_GLOW

    # In your Button drawing logic
    #if self.is_enabled and self.color_bg == Style.COLOR_PAL_GREEN_ACTION:
    #    text_color = (10, 30, 10)  # Deep forest "almost black"
    #else:
    #    text_color = self.color_txt

    # Borders
    COLOR_BORDER            = COLOR_PAL_GRAY_500
    COLOR_BORDER_SUBTLE     = COLOR_PAL_GRAY_700
    COLOR_CARD_BORDER       = COLOR_PAL_GRAY_500

    # Buttons
    COLOR_BUTTON_BG         = COLOR_PAL_GRAY_700
    #COLOR_BUTTON_HOVER      = None  # Computed on init

    # Tabs
    COLOR_TAB_BG            = COLOR_PAL_GRAY_800
    COLOR_TAB_BG_HOVER      = None  # Computed on init
    COLOR_TAB_BG_ACTIVE     = COLOR_PAL_GRAY_700
    COLOR_TAB_TEXT          = COLOR_PAL_GRAY_300
    COLOR_TAB_TEXT_ACTIVE   = COLOR_PAL_WHITE
    COLOR_TAB_INDICATOR     = COLOR_PAL_ORANGE_FORGE

    # Special (for GlowingLabel)
    COLOR_MOLTEN            = COLOR_PAL_ORANGE_MOLTEN
    COLOR_MOLTEN_GLOW       = COLOR_PAL_ORANGE_GLOW

    # Bevel (3D effect)
    COLOR_BEVEL_LIGHT       = COLOR_PAL_GRAY_600
    COLOR_BEVEL_DARK        = COLOR_PAL_GRAY_950

    # ============================================================
    # REFINED BEVEL ROLES (The "Forge" Metals)
    # ============================================================

    # 1. RAISED (For Buttons, Tabs, and the 'Launch' button)
    # Makes things pop UP toward the user
    COLOR_BEVEL_RAISED_LIGHT = (80, 80, 90)  # Gray 600
    COLOR_BEVEL_RAISED_DARK = (5, 5, 8)  # Almost Pure Black (Hidden Shadow)

    # 2. SUNKEN (For Project Lists, Text Inputs, and Containers)
    # Makes things look etched INTO the metal floor
    COLOR_BEVEL_SUNKEN_INNER = (10, 10, 15)  # Dark shadow inside the top rim
    COLOR_BEVEL_SUNKEN_OUTER = (60, 60, 70)  # Light hitting the bottom 'lip'

    # 3. MOLTEN (For Selected/Active items)
    # The "Heat" effect
    COLOR_BEVEL_HOT_LIGHT = (230, 140, 30)  # Primary Orange
    COLOR_BEVEL_HOT_DARK = (180, 90, 20)  # Deep Orange shadow

    # ============================================================
    # BEVEL SETS (Physicality)
    # ============================================================

    # RAISED: For things that stick UP (Tabs, Buttons)
    # Light is on Top/Left
    COLOR_BEVEL_RAISED_LT = COLOR_PAL_GRAY_600  # (80, 80, 90)
    COLOR_BEVEL_RAISED_DK = (0, 0, 0)  # Pure Black shadow

    # SUNKEN: For things that are recessed (Project List, Inputs)
    # Shadow is on Top/Left, Light hits the Bottom/Right 'lip'
    COLOR_BEVEL_SUNKEN_LT = COLOR_PAL_GRAY_700  # (60, 60, 70)
    COLOR_BEVEL_SUNKEN_DK = (10, 10, 15)  # Darker than BG

    # HOT: For active/selected state (The "Glow" of the Forge)
    COLOR_BEVEL_HOT_LT = COLOR_PAL_ORANGE_BRIGHT  # (255, 180, 60)
    COLOR_BEVEL_HOT_DK = COLOR_PAL_ORANGE_DEEP  # (180, 90, 20)


    # ============================================================
    # TOKENS - Spacing (multiplier-based)
    # ============================================================
    TOKEN_MULTIPLIER        = 2
    TOKEN_PAD               = TOKEN_MULTIPLIER * 2  # space between a widget's edge and its content (inside the border)
    TOKEN_PAD_TIGHT         = TOKEN_MULTIPLIER * 1  # space between a widget's edge and its content (inside the border)
    TOKEN_GAP               = TOKEN_MULTIPLIER * 3  # space between sibling children (between widgets)
    TOKEN_GAP_TIGHT         = TOKEN_MULTIPLIER * 2  # space between sibling children (between widgets)
    TOKEN_BORDER            = TOKEN_MULTIPLIER * 1  # 2
    TOKEN_SCROLLBAR         = 20
    TOKEN_CORNER_RADIUS     = 4


    # Font proportions (artist data - relative to screen height)
    FONT_RATIO_BANNER       = .1969
    FONT_RATIO_TITLE        = .0889
    FONT_RATIO_HEADING       = .0696
    FONT_RATIO_BODY         = .0636
    FONT_RATIO_DETAIL       = .0590
    FONT_RATIO_MONO         = .0396

    # User preference (0.0 to 1.0, future slider target)
    font_scale              = .369

    # Initialized by MgrFont
    FONT_BANNER             = None
    FONT_TITLE              = None
    FONT_HEADING            = None
    FONT_BODY               = None
    FONT_DETAIL             = None