# SelectionList.py (complete file)
from ipui.engine._BaseWidget import _BaseWidget
from ipui.widgets.Row import CardCol
from ipui.widgets.SelectableListItem import SelectableListItem


class SelectionList(_BaseWidget):
    """
    desc:        Scrollable multi-select list with pipeline sync and tooltip support.
    when_to_use: Picking one or many items from a known set.
    best_for:    Gladiator lists, arena lists, config categories, anything dict-shaped.
    example:     SelectionList(parent, data=items, pipeline_key="picks", on_change=handler)
    api:         get_selected(), get_selected_data(), set_filter(text), sync_from_pipeline()
    """

    def build(self):
        self.my_name    = f"SelectionList: {self.text}"
        self.items_data = self.data or {}

        if self.scrollable:
            raise ValueError(
                "SelectionList handles scrolling internally. "
                "TO FIX: Remove scrollable=True from the SelectionList constructor."
            )

        self.list_card = CardCol(self, height_flex=True, scrollable=True)
        self.items     = []

        for name, item_data in self.items_data.items():
            item          = SelectableListItem(self.list_card, text=name, data=item_data)
            item.on_click = lambda i=item: self.on_item_clicked(i)
            if self.tooltip_class:
                item.tool_tip_huge = self.tooltip_class(name, item_data)
            self.items.append(item)

        if self.pipeline_key and self.form:
            self.sync_from_pipeline()

    @property
    def selected_count(self):
        return len(self.get_selected())

    def set_filter(self, text):
        text = (text or "").lower()
        for item in self.items:
            item.visible = text in item.text.lower()
        self.list_card.scroll_offset = 0

    def on_item_clicked(self, clicked_item=None):
        if self.single_select and clicked_item:
            self.deselect_others(clicked_item)
        if self.pipeline_key:   self.form.pipeline_set(self.pipeline_key, self.get_selected())
        if self.on_change:      self.on_change(self.get_selected())

    def deselect_others(self, keep):
        for item in self.items:
            if item is not keep and item.is_selected:
                item.is_selected = False
                item.apply_selection_visual()

    def get_selected(self):
        return [item.text for item in self.items if item.is_selected]

    def get_selected_data(self):
        return {item.text: item.data for item in self.items if item.is_selected}

    def sync_from_pipeline(self):
        selected = self.form.pipeline_read(self.pipeline_key)
        if selected is None:
            return
        selected_set = set(selected)
        if selected_set == set(self.get_selected()):
            return
        for item in self.items:
            item.is_selected = (item.text in selected_set)
            item.apply_selection_visual()
        if self.on_change:
            self.on_change(self.get_selected())