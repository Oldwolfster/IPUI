from ipui import *
from ipui import _basePane


class FixScroll(_basePane):

    @staticmethod
    def pane1(parent):
        scroller= Card(parent, scrollable=True)
        Banner(parent,"Fix when scroll needs to go on parent\nThe quick brown fox jumped over the lazy good for nothign dog\nThe quick brown fox jumped over the lazy good for nothign dog\nThe quick brown fox jumped over the lazy good for nothign dog",glow=True, scrollable=True)
        Banner(scroller,"Fix when scroll needs to go on parent\nThe quick brown fox jumped over the lazy good for nothign dog\nThe quick brown fox jumped over the lazy good for nothign dog\nThe quick brown fox jumped over the lazy good for nothign dog",glow=True,scrollable=True)
        #Banner(scroller,"Fix when scroll needs to go on parent\nThe quick brown fox jumped over the lazy good for nothign dog\nThe quick brown fox jumped over the lazy good for nothign dog\nThe quick brown fox jumped over the lazy good for nothign dog", glow=True, scrollable=True, height_flex=False)
        card = CardCol(parent, name="test1_scroll", scrollable=True, height_flex=1)
        for i in range(1, 3):
            Body(card, f"Scrollable label number {i} - testing scroll behavior2", name=f"lbl1_{i}")

    @staticmethod
    def pane2(parent):
        pass
        #card = CardCol(parent, name="test2_no_scroll",scrollable=True, height_flex=1)
        #for i in range(1, 125):
        #    Body(card, f"Non-scrollable label number {i} - should clip", name=f"lbl2_{i}")

    @staticmethod
    def pane3(parent):
        Title(parent, "ScrollMachine Test")
        big_text = "\n".join(f"Line {i} - The quick brown fox" for i in range(1, 50))
        TextArea(parent, scrollable=True, height_flex=1, initial_value=big_text)