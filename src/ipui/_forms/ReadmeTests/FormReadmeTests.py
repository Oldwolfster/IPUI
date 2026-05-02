# FormReadmeTests.py  New: exercises every README code example in one host form
# Drop this and its sibling files into forms/readme_tests/ and run.
# Every pane method is annotated with its README line range.
from ipui import *
import pygame


# ─────────────────────────────────────────────────────────────────────
# Custom widget for README L295-300 ("build() vs __init__")
# ─────────────────────────────────────────────────────────────────────
class MyWidget(_BaseWidget):                              # README L296
    def build(self):                                      # README L297
        self.font     = Style.FONT_BODY                   # README L298
        self.color_bg = Style.COLOR_CARD_BG               # README L299


# ─────────────────────────────────────────────────────────────────────
# ReadmeTests host form
# ─────────────────────────────────────────────────────────────────────
class ReadmeTests(_BaseForm):

    # ---------------- Class-attribute snippets wired live ----------------

    # README L1126-1131: PIPELINE_DEFAULTS
    PIPELINE_DEFAULTS = {
        "training_active": False,
        "epoch":            0,
        "config_valid":     True,
    }

    # README L928-931: tab_early_load — Pipeline tab pre-built at startup
    tab_early_load = ["Config"]

    # README L935-938: tab_hidden — Hidden tab is shown via a button on Tabs tab
    tab_hidden = ["Hidden"]

    # README L949: tab_on_change (permissive — logs to console, never vetoes)
    tab_on_change = "guard_tab_switch"

    # README L859-863, L898, L910: TAB_LAYOUT
    TAB_LAYOUT = {
        "QuickStart"    : ["quickstart"],
        "CoreConcepts"  : ["core_layout", "core_split"],
        "UpdateUI"      : ["reactive_demo", "imperative_demo", "hybrid_demo"],
        "IpPortal"      : ["ip_portal"],
        "StateMachine"  : ["state_machine"],
        "Lifecycle"     : ["lifecycle"],
        "WidgetCat"     : ["widget_catalog"],
        "Layout"        : ["layout_demo"],
        "Tabs"          : [("tabs_sidebar", 1), ("tabs_main", 3)],          # README L898
        "Pipeline"      : ["pipeline_demo"],
        "Imperative"    : ["imperative_full"],
        "Styling"       : ["styling_demo"],
        "Launchers"     : ["launchers"],
        "Widgets"       : ["demo", "demo2"],                                # ← external Widgets.py wins (L209)
        "Config"        : ["settings", "hyperparams"],                      # ← external Config.py
        "Pro"           : ["Armory.match_settings",
                           "Forge.workbench",
                           "Forge.preview"],                                # README L912
        "Hidden"        : ["hidden_pane"],
    }

    # ---------------- tab_on_change handler (README L951-955) ----------------

    def guard_tab_switch(self, name, current):                # README L951
        # Permissive: log every switch, never veto.
        print(f"[tab_on_change] {current!r} -> {name!r}")
        return True                                           # README L955

    # ---------------- Form-level lifecycle (README L685-695) ----------------

    def ip_setup(self, ip):                                   # README L686
        self.global_timer = 0                                 # README L687

    def ip_activated(self, ip):                               # README L689
        # Fires when IPUI.show() brings this form to the front (README L690)
        pass

    def ip_think(self, ip):                                   # README L693
        self.global_timer += ip.dt                            # README L694

    # ─────────────────────────────────────────────────────────────────
    # TAB 1: QuickStart  — README L83-101 + L141-145
    # ─────────────────────────────────────────────────────────────────
    def quickstart(self, parent):
        # README L96-99: SmokeTest body (verbatim widget calls)
        Banner(parent, "IPUI",                text_align=CENTER, glow=True)
        Title (parent, "Easy to get right!",  text_align=CENTER)
        Body  (parent, "Hard to get wrong.",  text_align=CENTER)
        Button(parent, "Click Me :)",
               on_click=lambda: self.show_modal("Hello"))                  # README L99

        # README L141-145: trimmed Widgets snippet
        Title (parent, "Widget Playground")                                # README L143
        Button(parent, "Test Me",                                          # README L144
               on_click=lambda: self.show_modal("Nice"))

    # ─────────────────────────────────────────────────────────────────
    # TAB 2: CoreConcepts  — README L173, L232-256, L283-289, L295-300
    # ─────────────────────────────────────────────────────────────────
    def core_layout(self, parent):
        # README L283-289: widget tree — construction-is-attachment
        card = CardCol(parent)                                # README L284
        Title(card, "Settings")                               # README L285
        Body (card, "Change stuff")                           # README L286
        Body (parent, "No add(). No pack(). No grid().")      # README L289

        # README L295-300: custom widget with build()
        MyWidget(parent)                                      # README L296

    def core_split(self, parent):
        # README L173: TAB_LAYOUT shape narration (the dict itself is on this form)
        Title(parent, "TAB_LAYOUT shape")
        Body (parent, '"Hello World"   : ["welcome"]')        # README L174
        Body (parent, '"Widgets"       : ["demo","demo2"]')   # README L175
        Body (parent, '"Bouncing Ball" : ["arena", None]')    # README L176

        # README L232-256: BouncingBall split (UI-build vs ip_* hooks)
        Heading(parent, "BouncingBall split:")
        Body   (parent, "pane method = builds UI")
        Body   (parent, "ip_setup    = init state")
        Body   (parent, "ip_think    = move ball")
        Body   (parent, "ip_draw     = paint ball")

    # ─────────────────────────────────────────────────────────────────
    # TAB 3: UpdateUI  — README L310-343
    # ─────────────────────────────────────────────────────────────────
    def reactive_demo(self, parent):
        # README L310-324: BINDINGS pattern (full demo lives in 'pipeline_demo')
        Title(parent, "Reactive")
        Body (parent, "BINDINGS at top of _BaseTab")
        Body (parent, "See the Pipeline tab for a live BINDINGS demo")

    def imperative_demo(self, parent):
        # README L328-334: store reference, call set_text on event
        Title(parent, "Imperative")
        self.lbl_imp = Body(parent, "Idle", name="lbl_status")             # README L330
        Button(parent, "Mark Epoch 5",                                     # README L333
               on_click=lambda: self.lbl_imp.set_text("Epoch 5"))

    def hybrid_demo(self, parent):
        # README L338-343: pipeline as KV store, read imperatively
        Title(parent, "Hybrid")
        Button(parent, "Run", on_click=self.on_run_clicked)

    def on_run_clicked(self):                                              # README L339
        active = self.pipeline_read("training_active")                     # README L340
        if active:                                                         # README L341
            self.show_modal("Already running!")                            # README L342
        else:
            self.show_modal("Started")

    # ─────────────────────────────────────────────────────────────────
    # TAB 4: IpPortal — README L356-368, L437-453, L464-466, L487-492, L498
    # ─────────────────────────────────────────────────────────────────
    def ip_portal(self, parent):
        Title(parent, "ip Service Portal")
        self.lbl_fps   = Body(parent, "FPS: --",       name="lbl_fps")
        self.lbl_mouse = Body(parent, "Mouse: --",     name="lbl_mouse")
        self.lbl_keys  = Body(parent, "Keys: press SPACE")
        self.lbl_cache = Body(parent, "Cache hits: 0")
        Button(parent, "ip.find('lbl_fps')", on_click=self.demo_find)      # README L498

    def demo_find(self):
        w = self.ip.find("lbl_fps")                                        # README L498
        self.show_modal(f"found: {w.display_name}" if w else "not found")

    # README L632-635: ip_draw_hud — also demos mouse/keyboard/cache portals
    def ip_draw_hud(self, ip):
        if ip.tab_name != "IpPortal": return
        # README L437-453: mouse readouts
        if hasattr(self, "lbl_mouse"):
            self.lbl_mouse.set_text(
                f"Mouse: ({ip.mouse_x},{ip.mouse_y}) "                     # README L439-440
                f"inside_pane={ip.mouse_inside_pane()}")                   # README L447
        # README L367: FPS
        if hasattr(self, "lbl_fps"):
            self.lbl_fps.set_text(f"FPS: {ip.fps}")
        # README L487-489: cache
        n = ip.cache_get("hits", 0)                                        # README L487
        ip.cache_set("hits", n + 1)                                        # README L488
        if hasattr(self, "lbl_cache"):
            self.lbl_cache.set_text(f"Cache hits: {n+1}")
        # README L464-466: keyboard
        if ip.key_pressed(Key.SPACE):                                      # README L465
            if hasattr(self, "lbl_keys"):
                self.lbl_keys.set_text("Space pressed!")

    # ─────────────────────────────────────────────────────────────────
    # TAB 5: StateMachine — README L522-568
    # ─────────────────────────────────────────────────────────────────
    def state_machine(self, parent):
        Title(parent, "State Machine")
        self.lbl_state = Body(parent, "state: --")
        # README L530, L565-566: transitions
        Button(parent, "go DEMO",     on_click=lambda: self.ip.state.go("DEMO"))
        Button(parent, "go READY",    on_click=lambda: self.ip.state.go("READY"))
        Button(parent, "go PLAYING",  on_click=lambda: self.ip.state.go("PLAYING"))
        Button(parent, "go LEVEL_UP", on_click=lambda: self.ip.state.go("LEVEL_UP"))
        Button(parent, "ui.MENU_OPEN",
               on_click=lambda: self.ip.state("ui").go("MENU_OPEN"))       # README L567
        Button(parent, "Configure states", on_click=self.configure_states)

    # README L524-530, L565-566: register states, named machines
    def configure_states(self):
        ip = self.ip
        ip.state.add("DEMO"     , None)                                    # README L525
        ip.state.add("READY"    , None)                                    # README L526
        ip.state.add("PLAYING"  , None)                                    # README L527
        ip.state.add("LEVEL_UP" , None, "READY", 1.5)                      # README L528
        ip.state.add("GAME_OVER", None, "DEMO" , 2.5)                      # README L529
        ip.state.go("DEMO")                                                # README L530
        ip.state("combat").add("IDLE", None)                               # README L565
        ip.state("combat").go("IDLE")                                      # README L566
        ip.state("ui").add("MENU_OPEN", None)
        self.show_modal("States configured")

    # ─────────────────────────────────────────────────────────────────
    # TAB 6: Lifecycle — README L584-635, L703-712
    # ─────────────────────────────────────────────────────────────────
    def lifecycle(self, parent):
        Title  (parent, "Lifecycle Hooks")                                 # README L578
        Heading(parent, "ip_setup")                                        # README L582
        Body   (parent, "Runs once at creation")
        Heading(parent, "ip_activated")                                    # README L595
        Body   (parent, "Runs on each visibility transition")
        Heading(parent, "ip_think")                                        # README L607
        Body   (parent, "Per-frame logic")
        Heading(parent, "ip_draw")                                         # README L620
        Body   (parent, "Paint behind widgets")
        Heading(parent, "ip_draw_hud")                                     # README L629
        Body   (parent, "Paint on top of widgets")
        Heading(parent, "THINK_ALWAYS = True")                             # README L705
        Body   (parent, "Opt-in to background thinking")

    # ─────────────────────────────────────────────────────────────────
    # TAB 7: WidgetCat — README L734-827
    # ─────────────────────────────────────────────────────────────────
    def widget_catalog(self, parent):
        scroll = CardCol(parent, scroll_v=True, height_flex=1)           # README L749
        # README L734-738: text hierarchy
        Banner (scroll, "NeuroForge", glow=True)                           # README L734
        Title  (scroll, "Settings", glow=True)                             # README L735
        Heading(scroll, "Hyperparams:")                                    # README L736
        Body   (scroll, "Configure your model.")                           # README L737
        Detail (scroll, "Last updated: 2:30pm")                            # README L738

        # README L744-750: layout containers
        row = Row(scroll, justify_spread=True)                             # README L746
        Body(row, "left"); Body(row, "right")

        # README L758-762: Button
        Button(scroll, "Launch",                                           # README L758
               color_bg   = Style.COLOR_BUTTON_CTA,
               on_click   = self.launch_training,
               width_flex = 2)

        # README L769-773: TextBox
        TextBox(scroll,                                                    # README L769
                placeholder  = "Enter learning rate",
                pipeline_key = "learning_rate",
                on_change    = self.rate_changed)

        # README L778-782: SelectionList
        SelectionList(scroll,                                              # README L778
                      data          = {"SGD": {}, "Adam": {}, "RMSProp": {}},
                      pipeline_key  = "optimizer",
                      single_select = True,
                      on_change     = self.optimizer_changed)

        # README L787-791: DropDown
        DropDown(scroll,                                                   # README L787
                 data          = {"SGD": {}, "Adam": {}, "RMSProp": {}},
                 pipeline_key  = "optimizer_dd",
                 single_select = True)

        # README L795-799: PowerGrid
        rows = [["run_a", 0.91, 0.32], ["run_b", 0.88, 0.41]]
        grid = PowerGrid(scroll, name="results_grid")                      # README L795
        grid.set_data(rows, columns=["Run", "Accuracy", "Loss"])           # README L796
        grid.set_column_max("Run", 200)                                    # README L797
        grid.set_page_size(50)                                             # README L798
        grid.on_row_click(self.on_row_selected, column="Run")              # README L799

        # README L821-827: Chart
        chart = Chart(scroll, width_flex=1, height_flex=1)                 # README L821
        chart.set_data(                                                    # README L822
            lines   = {"Train Loss": [(0, 0.9), (1, 0.7), (2, 0.5)],
                       "Val Loss":   [(0, 0.95),(1, 0.75),(2, 0.6)]},
            x_label = "Epoch",
            y_label = "Loss"
        )

    def launch_training(self):       self.show_modal("Launch!")            # README L760
    def rate_changed(self, val):     pass                                  # README L772
    def optimizer_changed(self, v):  pass                                  # README L782
    def on_row_selected(self, val):  self.show_modal(f"row: {val}")        # README L799

    # ─────────────────────────────────────────────────────────────────
    # TAB 8: Layout — README L837-848
    # ─────────────────────────────────────────────────────────────────
    def layout_demo(self, parent):
        # README L837-840: flex weights
        Title(parent, "Flex weights — 1/3 and 2/3")
        row = Row(parent)                                                  # README L837
        Col(row, width_flex=1).tap(lambda c: Body(c, "1/3"))               # README L838
        Col(row, width_flex=2).tap(lambda c: Body(c, "2/3"))               # README L839

        # README L846: scrollable
        Title(parent, "Scrollable container")
        sc = CardCol(parent, scrollable=True, height_flex=1)               # README L846
        for i in range(40):
            Body(sc, f"row {i}")

    # ─────────────────────────────────────────────────────────────────
    # TAB 9: Tabs — README L898 (this tab itself uses pane weights),
    #               L910-913 (Pro tab demonstrates dot-notation),
    #               L919-924 (runtime control buttons),
    #               L928-938 (early_load + hidden wired on form above)
    # ─────────────────────────────────────────────────────────────────
    def tabs_sidebar(self, parent):
        Title(parent, "Sidebar (weight 1)")                                # README L898
        # README L919-924: runtime tab control
        Button(parent, "switch_tab('WidgetCat')",
               on_click=lambda: self.switch_tab("WidgetCat"))              # README L919
        Button(parent, "hide_tab('Hidden')",
               on_click=lambda: self.hide_tab("Hidden"))                   # README L920
        Button(parent, "show_tab('Hidden')",
               on_click=lambda: self.show_tab("Hidden"))                   # README L921
        Button(parent, "refresh_pane(1)",
               on_click=lambda: self.refresh_pane(1))                      # README L923

    def tabs_main(self, parent):
        Title(parent, "Main pane (weight 3)")                              # README L898
        Body (parent, "Pane weight tuples: ('sidebar', 1), ('main', 3)")
        Body (parent, "Cross-tab share: see the 'Pro' tab")               # README L910
        Body (parent, "tab_early_load = ['Pipeline']")                    # README L930
        Body (parent, "tab_hidden = ['Hidden']")                          # README L937
        Body (parent, "tab_on_change wired permissively (see console)")   # README L949

    def hidden_pane(self, parent):
        Title(parent, "Hidden tab")                                        # README L935
        Body (parent, "I was hidden at startup; shown via show_tab()")

    # ─────────────────────────────────────────────────────────────────
    # TAB 10: Pipeline — README L1086-1131
    # ─────────────────────────────────────────────────────────────────
    # README L1094-1116: BINDINGS on a tab.  Since this pane lives on the form,
    # we wire BINDINGS as form-level demo via a sub-_BaseTab pattern below.
    BINDINGS = {                                                           # README L1096
        "lbl_epoch": {                                                     # README L1102
            "property": "text",                                            # README L1103
            "compute":  "compute_epoch_label",                             # README L1104
            "triggers": ["epoch"],                                         # README L1105
        },
    }

    def compute_epoch_label(self, epoch):                                  # README L1114
        return f"Epoch: {epoch}"                                           # README L1115

    def pipeline_demo(self, parent):
        Title(parent, "Pipeline (Reactive)")
        Body (parent, "PIPELINE_DEFAULTS seeded at startup")               # README L1126
        Detail(parent, f"  training_active = "
                       f"{self.pipeline_read('training_active')}")         # README L1089
        Detail(parent, f"  epoch           = "
                       f"{self.pipeline_read('epoch')}")
        Detail(parent, f"  config_valid    = "
                       f"{self.pipeline_read('config_valid')}")

        # Live BINDINGS display
        Body(parent, "Live derive (via BINDINGS):")
        Body(parent, "Epoch: 0", name="lbl_epoch")                         # README L1102

        # README L1086-1090: pipeline_set / pipeline_read
        Button(parent, "pipeline_set('epoch', epoch+1)",                   # README L1087
               on_click=self.bump_epoch)
        Button(parent, "pipeline_set('training_active', True)",
               on_click=lambda: self.pipeline_set("training_active", True))

    def bump_epoch(self):
        n = self.pipeline_read("epoch") or 0                               # README L1089
        self.pipeline_set("epoch", n + 1)                                  # README L1087

    # ─────────────────────────────────────────────────────────────────
    # TAB 11: Imperative — README L1140-1155
    # ─────────────────────────────────────────────────────────────────
    def imperative_full(self, parent):
        # README L1141-1145: store widget refs in pane builder
        self.lbl_count = Body(parent, "0 selected", name="lbl_count")     # README L1142
        self.btn_run   = Button(parent, "Run",                            # README L1143
                                color_bg = Style.COLOR_BUTTON_CTA,
                                on_click = self.on_run)
        # Trigger the imperative update path (README L1147-1152)
        Button(parent, "select 0", on_click=lambda: self.on_selection_changed(0))
        Button(parent, "select 3", on_click=lambda: self.on_selection_changed(3))
        # README L1155: access named widgets via form.widgets
        Button(parent, "form.widgets['lbl_count']",
               on_click=lambda: self.show_modal(
                   self.widgets["lbl_count"].display_name))

    def on_run(self): self.show_modal("Running")

    def on_selection_changed(self, count):                                 # README L1147
        self.lbl_count.set_text(f"{count} selected")                       # README L1148
        if count == 0:                                                     # README L1149
            self.btn_run.set_disabled("Select at least one item")          # README L1150
        else:
            self.btn_run.set_enabled()                                     # README L1152

    # ─────────────────────────────────────────────────────────────────
    # TAB 12: Styling — README L1199-1214
    # ─────────────────────────────────────────────────────────────────
    def styling_demo(self, parent):
        # README L1204-1206: import Style and use constants
        Button(parent, "Go", color_bg=Style.COLOR_BUTTON_CTA)              # README L1204
        Body  (parent, "Status", font=Style.FONT_BODY)                     # README L1205

        # README L1208: a sampler of the named color constants
        Body(parent, "COLOR_BUTTON_DANGER",    color_bg=Style.COLOR_BUTTON_DANGER)
        Body(parent, "COLOR_BUTTON_SECONDARY", color_bg=Style.COLOR_BUTTON_SECONDARY)
        Body(parent, "COLOR_BUTTON_ACCENT",    color_bg=Style.COLOR_BUTTON_ACCENT)
        Body(parent, "COLOR_BUTTON_WARNING",   color_bg=Style.COLOR_BUTTON_WARNING)

        # README L1210: font constants
        Body(parent, "FONT_BANNER",  font=Style.FONT_BANNER)
        Body(parent, "FONT_TITLE",   font=Style.FONT_TITLE)
        Body(parent, "FONT_HEADING", font=Style.FONT_HEADING)
        Body(parent, "FONT_DETAIL",  font=Style.FONT_DETAIL)
        Body(parent, "FONT_MONO",    font=Style.FONT_MONO)

    # ─────────────────────────────────────────────────────────────────
    # TAB 13: Launchers — README L1244-1253 (show / back)
    # ─────────────────────────────────────────────────────────────────
    def launchers(self, parent):
        Title(parent, "Launch other forms")                                # README L1244
        Body (parent, "show() switches active form; back() returns")       # README L1253

        Button(parent, "show(TablessMinimal)",                             # README L1250
               on_click=self.launch_tabless)
        Button(parent, "show(Dashboard)",
               on_click=self.launch_dashboard)

    def launch_tabless(self):
        from TablessMinimal import TablessMinimal
        show(TablessMinimal, "Tabless Minimal")                            # README L1250

    def launch_dashboard(self):
        from Dashboard import Dashboard
        show(Dashboard, "Dashboard")                                       # README L1250


# README L101: __name__ guard launching the form
if __name__ == "__main__":
    show(ReadmeTests, "Readme Tests")
