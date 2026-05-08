# MiniBoard.py

from ipui import *
from pathlib import Path
import json


class MiniBoard(_BaseTab):

    def ip_setup_early(self, ip):
        self.storage_folder = Path.home() / "IPUI" / "MiniBoard"
        self.storage_file   = self.storage_folder / "cards.json"

        self.cards = self.load_cards()
        self.form.pipeline_set("new_card_text", "")

    def load_cards(self):
        default_cards = {
            "todo" : ["Write README", "Fix weird button bug"],
            "doing": ["Build MiniBoard", "Test API"],
            "done" : ["Install IPUI"],
        }

        if not self.storage_file.exists():
            return default_cards

        try:
            with open(self.storage_file, "r", encoding="utf-8") as private_file:
                data = json.load(private_file)

            return {
                "todo" : list(data.get("todo",  [])),
                "doing": list(data.get("doing", [])),
                "done" : list(data.get("done",  [])),
            }

        except Exception:
            return default_cards

    def save_cards(self):
        self.storage_folder.mkdir(parents=True, exist_ok=True)

        with open(self.storage_file, "w", encoding="utf-8") as private_file:
            json.dump(self.cards, private_file, indent=4)

    def todo(self, parent):
        Title(parent, f"To Do ({len(self.cards['todo'])})")

        row = Row(parent)
        TextBox(row, placeholder="New card", pipeline_key="new_card_text", width_flex=1)
        Button(row, "Add", on_click=self.add_card)

        self.build_card_list(parent, "todo")

    def doing(self, parent):
        Title(parent, f"Doing ({len(self.cards['doing'])})")
        self.build_card_list(parent, "doing")

    def done(self, parent):
        Title(parent, f"Done ({len(self.cards['done'])})")
        self.build_card_list(parent, "done")
        Button(parent, "Clear Done", on_click=self.clear_done)

    def build_card_list(self, parent, column):
        list_box = CardCol(parent, height_flex=1, scroll_v=True)

        for text in self.cards[column]:
            card = Card(list_box)
            row  = Row(card)

            if column != "todo":
                Button(row, "<", on_click=lambda text=text, column=column: self.move_left(text, column))

            Body(row, text, width_flex=1)

            if column != "done":
                Button(row, ">", on_click=lambda text=text, column=column: self.move_right(text, column))

    def add_card(self):
        text = self.form.pipeline_read("new_card_text").strip()

        if not text:
            return

        self.cards["todo"].append(text)
        self.form.pipeline_set("new_card_text", "")
        self.save_and_refresh()

    def move_left(self, text, column):
        if column == "doing":
            self.move_card(text, "doing", "todo")
        elif column == "done":
            self.move_card(text, "done", "doing")

    def move_right(self, text, column):
        if column == "todo":
            self.move_card(text, "todo", "doing")
        elif column == "doing":
            self.move_card(text, "doing", "done")

    def move_card(self, text, source, target):
        if text not in self.cards[source]:
            return

        self.cards[source].remove(text)
        self.cards[target].append(text)
        self.save_and_refresh()

    def clear_done(self):
        self.cards["done"].clear()
        self.save_and_refresh()

    def save_and_refresh(self):
        self.save_cards()
        self.refresh_all_panes()

    def refresh_all_panes(self):
        self.form.refresh_pane(0)
        self.form.refresh_pane(1)
        self.form.refresh_pane(2)