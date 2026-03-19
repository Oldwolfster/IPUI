# paneHome.py  NEW FILE  (replaces frmHome.py)



from forms.NeuroForge.custom_widgets.ProjectManager import ProjectManager
from ipui import *

class EZ_Pane(_basePane):

    def welcome(self, parent):
        card = CardCol(parent, width_flex=True, height_flex=True)
        Title(card, "Welcome to IPUI", glow=True)
        sub = CardCol(card)
        Heading(sub, "Easy to get right:", glow=True)
        Heading(sub, "Hard to get wrong:", glow=True)
        Body(sub, "Select a project or create a new one.")
        Spacer(card)
        sub = CardCol(card)
        Heading(sub, "Our Goal:", glow=True)
        Body(sub, "Build neural networks without writing a line of code—\nbut with more power, control, and visibility")
        Spacer(card)
        sub = CardCol(card)
        Heading(sub, "NeuroForge Sacred Laws:", glow=True)
        self.sacred_law(sub, "100% Auditable!",       "ABSOLUTELY EVERYTHING")
        self.sacred_law(sub, "200% Deterministic!",    "ABSOLUTELY EVERYTHING")
        self.sacred_law(sub, "User Responsible for",   "ABSOLUTELY NOTHING", True)
        self.sacred_law(sub, "But able to override",   "ABSOLUTELY EVERYTHING")

    def sacred_law(self, parent, label, value, glow=False):
        row = Row(parent)
        Body(row, label)
        Body(row, value, glow=glow, text_align="r")

    def metaphor(self, parent):
        card = CardCol(parent, width_flex=True, height_flex=True)
        Title(card, "Our Metaphor", glow=True)

        sub = CardCol(card)
        Heading(sub, "Arena:")
        Body(sub, "The training data.")
        Body(sub, "Identical for all gladiators.")

        sub = CardCol(card)
        Heading(sub, "Gladiator:")
        Body(sub, "A specific 'Model Config'")
        Body(sub, "Identical Gladiators tests determinism")
        Body(sub, "Any change is isolated.  Perfect A/B test")

    def select_project(self, parent):
        projects = ProjectManager.list_projects()
        if not projects:
            self.name_project(parent)
            return

        header = Row(parent, justify_spread=True)
        Title(header, "Select Project", glow=True)
        btn = Button(header, "+New", color_bg=Style.COLOR_PAL_GREEN_SECOND)
        btn.on_click = lambda: self.form.set_pane(1, self.name_project)

        scroller = CardCol(parent, height_flex=True, scrollable=True)
        for project_info in projects:
            item = ProjectListItem(scroller, data=project_info)
            item.on_click = lambda p=project_info: self.do_select_project(p.path)

    def name_project(self, parent):
        has_projects = len(ProjectManager.list_projects()) > 0

        header = Row(parent, justify_spread=True)
        Title(header, "Name New Project", glow=True)
        if has_projects:
            btn = Button(header, "Back")
            btn.on_click = lambda: self.form.set_pane(1, self.select_project)
        Spacer(header)
        btn = Button(header, "+Add", color_bg=Style.COLOR_PAL_GREEN_SECOND)
        btn.on_click = lambda: self.form.widgets["txt_project_name"].submit()

        TextBox(parent,
                placeholder="Enter project name...",
                initial_value=self.default_project_name(),
                name="txt_project_name",
                on_submit=lambda name: self.create_project(name),
                )

        Spacer(parent)
        sub = CardCol(parent)
        Heading(sub, "Any Name Works!")
        Body(sub, "A few fun examples...")
        Body(sub, "Optimizer Shootout on XOR")
        Body(sub, "Find Best Initializer for Any Activation")
        Body(sub, "Compare Batch Size Impact on Optimization")

    def create_project(self, name):
        clean_name = ProjectManager.sanitize_filename(name)
        self.form.show_modal(f"Creating Project: {clean_name}",
                             lambda: ProjectManager.create_project(name),
                             min_seconds=1.69)
        path = ProjectManager.PROJECTS_FOLDER / f"{clean_name}.nf"
        self.do_select_project(path)


    def default_project_name(self):
        from datetime import datetime
        if ProjectManager.list_projects():
            return "NeuroForgeProject_" + datetime.now().strftime("%Y_%m_%d_%H_%M")
        return "get_the_lay_of_the_land"


    def do_select_project(self, path):
        def do_load():
            ProjectManager.set_active_project(path)
            self.form.active_project = ProjectManager.get_project_info(path)

        self.form.show_modal("Loading Project...", 0.1, do_load)
        btn = self.form.widgets["btnLaunch"]
        if btn:
            btn.set_enabled()
        self.form.calc_total_runs()
        self.form.switch_tab("Workbench")

        def create_project(self, name):
            clean_name = ProjectManager.sanitize_filename(name)
            self.form.show_modal(f"Creating Project: {clean_name}",
                            lambda: ProjectManager.create_project(name),
                            min_seconds=1.0)
            path = ProjectManager.PROJECTS_FOLDER / f"{clean_name}.nf"
            self.do_select_project(path)