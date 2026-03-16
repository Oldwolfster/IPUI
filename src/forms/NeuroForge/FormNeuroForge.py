from ipui import IPUI
from ipui.Style import Style
from ipui.docs.ProjectManager import ProjectManager
from forms.NeuroForge.SubProcesses import SubProcesses
from ipui.engine.Log import Logger
from ipui.engine._BaseForm import _BaseForm
from ipui.widgets.Button import Button
from ipui.widgets.Row import Row
from ipui.widgets.Label import Banner


class FormNeuroForge(_BaseForm):

    TAB_LAYOUT = {
        #TAB NAME       PANEL 1                     , PANEL X (as many as you want)     , [Panel Flex, 2](to change size)
        "Home"      : ["welcome"                    , "select_project"                  , "metaphor"],
        "Ludus"     : ["batches"                    , "batch_runs"                     , "best_runs"],
        "Armory"    : ["match_hints"                , "match_settings"                  , None],
        "Forge"     : ["info"                       , "workbench"                       , "preview"],
        "Colosseum" : ["status"                     , "runs"                            , "analysis"],
        "Pro"       : ["Armory.match_settings"      , "Forge.workbench"                 , "Forge.preview"],
        "Export"    : ["build"],
        "Log"       : ["log"],
    }
    tab_early_load  = ["Log"]
    tab_on_change   = "guard_tab_switch"

    def build(self):
        self.active_project = None
        self.initialize_defaults()
        self.build_header_row()

    def build_footer(self):
        self.autoload_last_project()

    def initialize_defaults(self):
        self.pipeline_set("GladiatorList",    ["AutoForge"])
        self.pipeline_set("ArenaList",        ["XOR"])
        self.pipeline_set("SeedCountRandom",  2)
        self.pipeline_set("SeedListManual",   [980963])
        self.pipeline_set("OptimizerManual",  [])
        self.pipeline_set("HP_Epochs to Run",      50)
        self.pipeline_set("HP_Training Set Size",   40)
        self.pipeline_set("HP_Learning Rate",        0)

    def autoload_last_project(self):
        Logger().log("autoloading last project")
        projects = ProjectManager.list_projects()
        if projects:
            path = projects[0].path
            ProjectManager.set_active_project(path)
            self.active_project = ProjectManager.get_project_info(path)
            self.widgets["btnLaunch"].set_enabled()
            self.switch_tab("Forge")


    def guard_tab_switch(self, name, current):
        if name != "Home" and self.active_project is None:
            self.show_modal("Please select or create a project first", lambda: None, min_seconds=.15)
            return False

    def build_header_row(self):
        header       = Row(self, justify_spread=True)
        btn          = Button(header, "Back to\nShowcase",   color_bg=Style.COLOR_TAB_BG,width_flex=1)
        btn.on_click = lambda: IPUI.back()
        Banner(header, "NeuroForge", text_align='c', glow=True,width_flex=12)
        btn          = Button(header, "Launch", color_bg=Style.COLOR_PAL_GREEN_DARK,  name="btnLaunch",width_flex=1)
        btn.set_disabled("Select Project To Enable")
        btn.on_click = lambda: self.launch_colosseum()

    def launch_colosseum(self):
        self.widgets["btnLaunch"].text = ("Launch")
        self.widgets["btnLaunch"].set_disabled("Running...")
        self.show_modal("Preparing the Arena...", self.launch_training, min_seconds=0.5)

    def launch_training(self):
        guid = SubProcesses.write_launch_config(self)
        Logger.log(f"Config written: {guid[:8]}...")
        batch_id = SubProcesses.launch_prepare_batch(self)
        if batch_id is None:            return
        self.active_batch_id = batch_id
        colosseum = self.prepare("Colosseum")
        colosseum.clear_temp_folder()
        self.TAB_LAYOUT["Colosseum"] = ["status", "runs", "analysis"]
        self.switch_tab("Colosseum")
        self.show_tab("Colosseum")
        Logger.log(f"Colosseum opened! Batch {batch_id}")
        SubProcesses.launch_shards(self, batch_id)

    def update(self):
        if not hasattr(self, 'active_batch_id'):    return
        self.poll_counter = getattr(self, 'poll_counter', 0) + 1

        if self.poll_counter % 30 == 0:
            Logger.log(f"Poll #{self.poll_counter}")  # Add above poll_shards call
            self.get_tab("Colosseum").poll_shards()

    def calc_total_runs(self):
        """Compute total run count and update launch button."""
        gladiators = len(self.pipeline_read("GladiatorList")  or [])
        arenas     = len(self.pipeline_read("ArenaList")      or [])
        seeds      = ((self.pipeline_read("SeedCountRandom")  or 0)
                      + len(self.pipeline_read("SeedListManual") or []))
        total      = max(1, gladiators) * max(1, arenas) * max(1, seeds)

        CONFIG_KEYS = [
            "OptimizerList",       "HiddenActivationList",
            "OutputActivationList","LossFunctionList",
            "InitializerList",     "InputScalerList",
            "TargetScalerList",
        ]
        for key in CONFIG_KEYS:
            count = len(self.pipeline_read(key) or [])
            if count > 1:                total *= count

        HPLIST_KEYS = ["BatchSizeList", "NeuronLayersList"]
        for key in HPLIST_KEYS:
            count = len(self.pipeline_read(key) or [])
            if count > 1:                total *= count

        btn = self.widgets.get("btnLaunch")
        if btn:
            btn.set_text(f"   Launch   \n({total} runs)")