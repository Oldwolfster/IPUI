from ipui import *

class SmokeTest(_BaseForm):
    TAB_LAYOUT = {
        "Hello World"   :["welcome"],       # ← This one works immediately
                                            #   due to the welcome method below
        "Widgets"       :["demo","demo2"],  # ← Will trigger template picker
        "Bouncing Ball" :["arena", None]    # ← Will trigger template picker
    }

    def welcome(self, parent):              # ← matches "welcome" in TAB_LAYOUT
        Banner  (parent, "IPUI"              , text_align=CENTER, glow=True)
        Body    (parent, "Easy to get right!", text_align=CENTER)
        Heading (parent, "Hard to get wrong.", text_align=CENTER)
        Title   (parent, "Because we've all spent 3 hours debugging a button", text_align=CENTER, glow=True)
        Button  (parent, "Click Me :)"       , on_click=lambda: self.form.show_modal("Hello"))
        #Button(parent, "Click Me :)", on_click=lambda: print("Hello"), border=5)

if __name__ == "__main__": show(SmokeTest)