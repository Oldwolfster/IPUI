# Todo.py  Update: two-pane todo app for Showcase
from pathlib import Path
from ipui import *


class TodoApp(_BaseTab):
    DATA_FILE = Path.home() / "ipui_todo.txt"

    def ip_setup(self, ip):
        self.tasks     = self.load_tasks()
        self.task_list = None

    # ══════════════════════════════════════════════════════════════
    # PANE BUILDERS
    # ══════════════════════════════════════════════════════════════

    def input(self, parent):
        Title(parent, "Add Task")
        self.txt_task = TextBox(parent, placeholder="What needs doing?",
                                on_submit=self.add_task, flex_width=1)
        Row(parent)
        Button(parent, "Add",              color_bg=Style.COLOR_BUTTON_CTA,
               on_click=self.add_task)
        Button(parent, "Clear Completed",  color_bg=Style.COLOR_BUTTON_WARNING,
               on_click=self.clear_completed)
        Button(parent, "Reload From Disk", on_click=self.reload_from_disk)
        self.lbl_stats = Body(parent, "")
        self.update_stats()

    def task_list_pane(self, parent):
        self.task_list = CardCol(parent, scroll_v=True, flex_height=1)
        self.render_task_list()

    # ══════════════════════════════════════════════════════════════
    # RENDERING
    # ══════════════════════════════════════════════════════════════

    def render_task_list(self):
        if not self.task_list:    return
        self.task_list.clear_children()
        Title(self.task_list, "Tasks")
        if not self.tasks:
            Body(self.task_list, "No tasks yet. Add one on the left.")
        else:
            for i, task in enumerate(self.tasks):
                self.render_task_row(i, task)
        self.update_stats()

    def render_task_row(self, index, task):
        row    = CardRow(self.task_list, flex_width=1)
        prefix = "✓" if task["done"] else "•"
        Body(row, f"{prefix} {task['text']}", flex_width=1)
        Detail(row, "Done" if task["done"] else "Todo")
        Button(row, "Toggle", on_click=lambda i=index: self.toggle_task(i))
        Button(row, "Delete", on_click=lambda i=index: self.delete_task(i))

    def update_stats(self):
        if not hasattr(self, 'lbl_stats'):    return
        total     = len(self.tasks)
        done      = sum(1 for t in self.tasks if t["done"])
        remaining = total - done
        self.lbl_stats.set_text(f"Total: {total}   Done: {done}   Remaining: {remaining}")

    # ══════════════════════════════════════════════════════════════
    # ACTIONS
    # ══════════════════════════════════════════════════════════════

    def add_task(self):
        text = self.txt_task.text.strip()
        if not text:
            self.show_modal("Please type a task first.")
            return
        self.tasks.append({"text": text, "done": False})
        self.save_tasks()
        self.txt_task.set_text("")
        self.render_task_list()

    def toggle_task(self, index):
        self.tasks[index]["done"] = not self.tasks[index]["done"]
        self.save_tasks()
        self.render_task_list()

    def delete_task(self, index):
        deleted = self.tasks.pop(index)
        self.save_tasks()
        self.render_task_list()
        self.show_modal(f"Deleted: {deleted['text']}")

    def clear_completed(self):
        before  = len(self.tasks)
        self.tasks = [t for t in self.tasks if not t["done"]]
        removed = before - len(self.tasks)
        self.save_tasks()
        self.render_task_list()
        if removed == 0:    self.show_modal("No completed tasks to clear.")
        else:               self.show_modal(f"Removed {removed} completed task(s).")

    def reload_from_disk(self):
        self.tasks = self.load_tasks()
        self.render_task_list()
        self.show_modal("Reloaded tasks from disk.")

    # ══════════════════════════════════════════════════════════════
    # PERSISTENCE
    # ══════════════════════════════════════════════════════════════

    def load_tasks(self):
        if not self.DATA_FILE.exists():
            return []
        tasks = []
        for line in self.DATA_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:                continue
            done = line.startswith("[x]")
            text = line[3:].strip() if line[:3].lower() in {"[ ]", "[x]"} else line
            if text:
                tasks.append({"text": text, "done": done})
        return tasks

    def save_tasks(self):
        lines = []
        for task in self.tasks:
            marker = "[x]" if task["done"] else "[ ]"
            lines.append(f"{marker} {task['text']}")
        self.DATA_FILE.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")