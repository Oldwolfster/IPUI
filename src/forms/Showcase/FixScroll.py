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
        card = CardCol(parent, name="test2_no_scroll",scrollable=True, height_flex=1)
        for i in range(1, 125):
            Body(card, f"Non-scrollable label number {i} - should clip", name=f"lbl2_{i}")