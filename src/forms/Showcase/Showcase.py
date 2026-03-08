from ipui import *
from ipui.widgets.CodeBox import CodeBox
from ipui.widgets.Label import Detail


class Showcase(_basePane):
    """
    A 'Signature' Tab designed by Gemini to sell the IPUI Aesthetic.
    """

    # ⛓️ THE REACTIVE BRAIN
    # This DAG ensures that as you type your name, the banner
    # and the 'Join' button update in perfect sync.
    DECLARATION_UPDATES = {
        "hero_banner": {
            "property": "text",
            "compute": "compute_welcome",
            "triggers": ["user_name"],
        },
        "btn_join": {
            "property": "enabled",
            "compute": "is_valid_name",
            "triggers": ["user_name"],
        }
    }

    def the_pitch(self, parent):
        """The 'Marketing' side: Show off typography and glow."""
        card = CardCol(parent, height_flex=True)

        Banner(card, "IPUI: The Forge", glow=True, name="hero_banner")

        Title(card, "Built for Developers, Designed for Humans.")

        Body(card,
             "Most Pygame UIs feel like 1995. IPUI feels like the future. "
             "Every widget you see here is layout-aware, DPI-scaled, "
             "and render-optimized using Dirty-Flag logic.")

        Spacer(card)

        # Showing off the mono font and automatic source introspection
        Heading(card, "Self-Documenting Code:")
        CodeBox(card, data=__file__, start="# ⛓️ THE REACTIVE", end="}")
        Spacer(card)

    def pipeline_live(self, parent):
        """The 'Functional' side: Show off the Reactive Pipeline."""
        card = CardCol(parent, height_flex=True)

        Title(card, "Live Pipeline Demo", glow=True)

        Heading(card, "1. Enter your Pilot Name:")
        TextBox(card,
                placeholder="Type something...",
                pipeline_key="user_name",
                width_flex=True)

        Spacer(card, height_flex=1)

        # This button is controlled by the is_valid_name compute method
        Button(card, "Initialize System",
               name="btn_join",
               color_bg=Style.COLOR_PAL_GREEN_DARK)

        Detail(card, "The button above stays disabled until you provide a name.")
        Spacer(card, height_flex=1)
    # --- Compute Methods for the DAG ---

    def compute_welcome(self, name):
        if name:
            return f"Welcome, {name}"
        return "IPUI: The Forge"

    def is_valid_name(self, name):
        # Logic: Name must be at least 3 chars to enable the button
        return len(name.strip()) >= 3