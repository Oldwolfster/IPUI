from pathlib import Path
from ipui import *


class TodoApp(_BaseForm):
    DATA_FILE = Path.home() / "ipui_todo.txt"

    def build(self):
        self.tasks = self.load_tasks()

        Banner(self, "IPUI Todo", glow=True, text_align=CENTER)
        Detail(self, f"Saving to: {self.DATA_FILE}", text_align=CENTER)

        main_row = Row(self, flex_width=1, flex_height=1)

        left = CardCol(main_row, flex_width=2, flex_height=1)
        right = CardCol(main_row, flex_width=3, flex_height=1, scroll_v=True)
        self.task_list = right

        Title(left, "Add Task")
        self.txt_task = TextBox(
            left,
            placeholder="What needs doing?",
            on_submit=self.add_task,
            flex_width=1,
        )

        Row(left)
        Button(
            left,
            "Add",
            color_bg=Style.COLOR_BUTTON_CTA,
            on_click=self.add_task,
        )
        Button(
            left,
            "Clear Completed",
            color_bg=Style.COLOR_BUTTON_WARNING,
            on_click=self.clear_completed,
        )
        Button(
            left,
            "Reload From Disk",
            on_click=self.reload_from_disk,
        )

        self.lbl_stats = Body(left, "", name="lbl_stats")
        self.render_task_list()

    def load_tasks(self):
        if not self.DATA_FILE.exists():
            return []

        tasks = []
        for raw_line in self.DATA_FILE.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue

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

    def add_task(self):
        text = self.read_task_text()
        if not text:
            self.show_modal("Please type a task first.")
            return

        self.tasks.append({"text": text, "done": False})
        self.save_tasks()
        self.clear_task_entry()
        self.render_task_list()

    def clear_completed(self):
        before = len(self.tasks)
        self.tasks = [task for task in self.tasks if not task["done"]]
        removed = before - len(self.tasks)
        self.save_tasks()
        self.render_task_list()

        if removed == 0:
            self.show_modal("No completed tasks to clear.")
        else:
            self.show_modal(f"Removed {removed} completed task(s).")

    def reload_from_disk(self):
        self.tasks = self.load_tasks()
        self.render_task_list()
        self.show_modal("Reloaded tasks from disk.")

    def render_task_list(self):
        self.task_list.clear_children()
        Title(self.task_list, "Tasks")

        if not self.tasks:
            Body(self.task_list, "No tasks yet. Add one on the left.")
        else:
            for index, task in enumerate(self.tasks):
                row = CardRow(self.task_list, flex_width=1)
                status = "Done" if task["done"] else "Todo"
                prefix = "✓" if task["done"] else "•"
                Body(row, f"{prefix} {task['text']}", flex_width=1)
                Detail(row, status)
                Button(row, "Toggle", on_click=lambda i=index: self.toggle_task(i))
                Button(row, "Delete", on_click=lambda i=index: self.delete_task(i))

        total = len(self.tasks)
        done = sum(1 for task in self.tasks if task["done"])
        remaining = total - done
        self.lbl_stats.set_text(f"Total: {total}   Done: {done}   Remaining: {remaining}")

    def toggle_task(self, index):
        self.tasks[index]["done"] = not self.tasks[index]["done"]
        self.save_tasks()
        self.render_task_list()

    def delete_task(self, index):
        deleted = self.tasks.pop(index)
        self.save_tasks()
        self.render_task_list()
        self.show_modal(f"Deleted: {deleted['text']}")

    def read_task_text(self):
        for attribute_name in ("text", "value"):
            if hasattr(self.txt_task, attribute_name):
                value = getattr(self.txt_task, attribute_name)
                if isinstance(value, str):
                    return value.strip()
        return ""

    def clear_task_entry(self):
        if hasattr(self.txt_task, "set_text"):
            self.txt_task.set_text("")
            return
        if hasattr(self.txt_task, "text"):
            self.txt_task.text = ""


if __name__ == "__main__":
    show(TodoApp)
