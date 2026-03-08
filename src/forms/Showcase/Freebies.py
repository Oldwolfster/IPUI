# Freebies.py  NEW: Showcase what _BaseForm gives you for free

from ipui import *
from ipui.widgets.CodeBox import CodeBox


class EZ_Pane(_basePane):

    DECLARATION_UPDATES= {
        "lbl_pipeline_echo" : {"property": "text", "compute":  "compute_echo"       ,"triggers": ["demo_key"],},
        "lbl_keystrokes"    : {"property": "text", "compute":  "compute_keystrokes" ,"triggers": ["demo_key"],},
    }



    # ══════════════════════════════════════════════════════════════
    # PANE 2 — Live Pipeline Demo
    # ══════════════════════════════════════════════════════════════

    def pipeline_demo(self, parent):
        Title(parent, "Pipeline — Live", glow=True)

        card = Card(parent)
        Heading(card, "Type below. Watch the magic.", glow=True)
        Body(card, "The TextBox writes to the pipeline.")
        Body(card, "The labels below are derives.")
        Body(card, "You wrote zero update code.")

        Spacer(parent)
        card = CardCol(parent, width_flex=True)
        TextBox(card,
            placeholder  = "Type anything...",
            pipeline_key = "demo_key",
            width_flex   = False)

        Spacer(parent)
        card = Card(parent)
        Heading(card, "Echo (derive → text):", glow=True)
        Body(card, "Waiting for input...",
            name       = "lbl_pipeline_echo",
            text_align = 'l')

        Spacer(parent)
        card = Card(parent)
        Heading(card, "Keystroke Count (derive → text):", glow=True)
        Body(card, "0 keystrokes",
            name       = "lbl_keystrokes",
            text_align = 'l')

        Spacer(parent)
        card = Card(parent)
        Heading(card, "How it works:", glow=True)
        Body(card, "TextBox has pipeline_key='demo_key'")
        Body(card, "Each keystroke → pipeline_set('demo_key', text)")
        Body(card, "Pipeline checks all derives for 'demo_key'")
        Body(card, "Matching derives fire their compute function")
        Body(card, "Result is applied to the named widget")
        Spacer(parent, height_flex=1)


    # ══════════════════════════════════════════════════════════════
    # PANE 1 — The Pitch
    # ══════════════════════════════════════════════════════════════

    def the_pitch(self, parent):
        Spacer(parent, height_flex=1)
        Banner(parent, "Wait... this is FREE?", glow=True)
        Spacer(parent, height_flex=1)

        card = Card(parent)
        Title(card, "Every Form comes loaded.", glow=True)
        Title(card, "With Extras to make your life easy.", glow=True)
        Spacer(parent, height_flex=1)

        card = Card(parent)
        Heading(card, "Reactive Pipeline", glow=True)
        Body(card, "Set a value. Everything downstream updates.")
        Body(card, "Zero wiring. Zero callbacks. Just declare.")

        Spacer(parent, height_flex=1)
        card = Card(parent)
        Heading(card, "Widgets Registry", glow=True)
        Body(card, "Name a widget. Access it from anywhere.")
        Body(card, "No self.btn_save_ref_copy_backup_final.")

        Spacer(parent, height_flex=1)
        card = Card(parent)
        Heading(card, "Professional grade debug tools.", glow=False)
        Body(card, "Designed to help you solve problems.")
        Spacer(card)
        Body(card, "Press F12 Now!  Take a look.", glow=True)

        Spacer(parent, height_flex=2)
        Body(parent, "Try the demos next door  →", text_align='r')
        Spacer(parent, height_flex=1)

    # ══════════════════════════════════════════════════════════════
    # PANE 3 — Source behind the demo
    # ══════════════════════════════════════════════════════════════

    def widgets_demo(self, parent):
        Title(parent, "Source Behind the Demo", glow=True)

        card = Card(parent)
        Heading(card, "The code that powers the live textbox.", glow=True)
        Body(card, "The TextBox writes to the pipeline.")
        Body(card, "The derive labels update automatically.")
        Body(card, "Read the source. Watch it happen live.")

        #Spacer(parent)
        card = Card(parent, scrollable=True, height_flex=1)
        CodeBox(card,
            data  = __file__,
            start = "DECLARATION_UPDATES= {",
            end   = "# ══════════════════════════════════════════════════════════════\n    # PANE 3")

    # ══════════════════════════════════════════════════════════════
    # DERIVE COMPUTES
    # ══════════════════════════════════════════════════════════════

    def compute_echo(self, demo_key):
        if not demo_key:
            return "Waiting for input..."
        return f"Pipeline says: '{demo_key}'"

    def compute_keystrokes(self, demo_key):
        count = len(demo_key) if demo_key else 0
        if count == 0:
            return "0 keystrokes"
        return f"{count} keystroke{'s' if count != 1 else ''} and counting..."