from ipui import *


class Kanban(_BaseTab):

    def todo(self, parent):
        Spacer(parent)
        row=Row(parent)
        Spacer(row)
        outer=Plate(row,pad_x=-10)

        inner=Plate(outer)
        Body(inner,"Test pad")
        Spacer(row)
        Spacer(parent)

    def doing(self, parent):
        Body(parent, "Filename: Kanban.py")
        Body(parent, "Method: doing")
        Body(parent, "Add content here!")

    def done(self, parent):
        Body(parent, "Filename: Kanban.py")
        Body(parent, "Method: done")
        Body(parent, "Add content here!")
