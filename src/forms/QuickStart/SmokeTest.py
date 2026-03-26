### Step 1: 30-Second Smoke Test – See It Work Instantly

# Save as **SmokeTest.py**:


from ipui import *

class QuickTest(BaseForm):
    TAB_LAYOUT = {"Smoke Test": ["go"]}

class SmokeTest(_basePane):

    def go(self, parent):
        Banner(parent, "IPUI", glow=True, text_align=CENTER)
        Body (parent, "Easy to get right!", text_align=CENTER)
        Title  (parent, "Hard to get wrong.", text_align=CENTER, glow=True)
        Button(parent, "Click Me",
               color_bg=Style.COLOR_PAL_GREEN_DARK,
               on_click=lambda: self.form.show_modal("Hello World!"))

if __name__ == "__main__":
    show(QuickTest)