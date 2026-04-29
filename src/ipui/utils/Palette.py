# Palette.py  NEW:  Raw RGB color definitions - framework internals only

class Palette:
    """
    Raw RGB tuples — the paint tubes.
    App code should never reference these directly.
    Use Style roles instead.
    """

    # Grays (dark to light)
    GRAY_990                = (5, 5, 8)
    GRAY_975                = (10, 10, 15)
    GRAY_950                = (15, 15, 18)
    GRAY_900                = (25, 25, 30)
    GRAY_850                = (35, 35, 40)
    GRAY_800                = (45, 45, 52)
    GRAY_700                = (60, 60, 70)
    GRAY_600                = (80, 80, 90)
    GRAY_500                = (100, 100, 110)
    GRAY_400                = (130, 130, 140)
    GRAY_300                = (160, 160, 170)
    GRAY_200                = (200, 200, 205)
    GRAY_100                = (230, 230, 235)
    WHITE                   = (255, 255, 255)
    BLACK                   = (  0,   0,   0)

    # Orange — Brand / Focus / Selection ("glow of the forge")
    ORANGE_DEEP             = (180,  90,  20)
    ORANGE_FORGE            = (230, 140,  30)
    ORANGE_BRIGHT           = (255, 180,  60)
    ORANGE_MOLTEN           = (255,  50,   0)
    ORANGE_GLOW             = (255, 150,  50)

    # Green — Action
    GREEN_DARK              = (45, 120, 45)

    # Red — Danger / Error
    RED_DARK                = (140, 40, 40)
    RED_PRIMARY             = (200, 60, 60)

    # Blue — Info
    BLUE_MUTED              = (70, 90, 130)