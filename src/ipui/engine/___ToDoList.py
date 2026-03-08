"""
Clean up list

1) DONE: WidgetsDict.get() — raises RuntimeError on missing keys. That's the opposite of what .get() should do (return default). This will blow up in frmColosseum where you do form.widgets.get("grid_runs") etc. — if you ever call those before the Colosseum tab is built, it crashes instead of returning None.
2) DONE:ChartWidget.draw() — calls super().draw() but never re-renders when chart_dirty is True and rect is available. The set_data method sets chart_dirty = True but nothing ever checks it during draw to re-render.
3) DONE: Grid.row_index_at() — doesn't account for scroll_offset on the parent. If the grid is inside a scrollable CardCol, click detection will be off.
4) REMOVED: _BaseForm.render() has if 1==1 or self.dirty — the TODO for dirty flag optimization.
5) DONE: frmSubProcesses has a TODO about the frm prefix being confusing.
6) DONE: No way to remove manual seeds in the RNG picker.
8) DONE: add neuron layers to config options.
9) DONE: add config size to config options.
******************************************************************
*********** 2/22
******************************************************************
11) DONE: Find a way to track the meta data in 'Select Project'
13) DONE: BTN Disabled text not showing up well.
14) DONE: When running large batch, screen not updating even close to proper interval.
15) DONE: If setting random seed to 0 it resets it to 1.
16) DONE: first pop up is to quick on gladiators/options/etc
17) DONE Disable run while mission going.
18) DONE: Button Not showing disable text
19) DONE Create workbench point and click neuoron configuration
25) DONE: Organize Settings Pane.  put config options below spanning both columns
20) DONE:: autoload last project
27) DONE: fix width issue on tabstrip
******************************************************************
*********** 2/23
******************************************************************
31) DONE: in BaseWidget init move validation to method
32) DONE: Scrollbar draw is bit hanky.
34) DONE tabs should only show the number of panes we have.
7) DONE: compute_content_size() doesn't count flex children at all, which means scrollable containers with flex children will compute wrong content size for scrollbar.
24) Done: Scroll to config setting options
39) DONE GRID give scroll option.
40) DONE GRID use available width
41) DONE GRID fix unprintable characters
42) DONE hover - surpress color change
36) DONE Logs not showing up

******************************************************************
*********** 2/24
******************************************************************
40) Done: Add on_click to constructor of _BaseWidget
53) Done: Delete panesdelete, MgrUIDeleteme, and TabStripBEFOREBASE
54) Done: Made tabstrip and helper methods first class members of form.
55) Done: Add cards on pipeline and widgets to demo.
56) Done: Make tab early load work for string or list
57) Done: in Form NeuroForge update to if not hasattr(self, 'active_batch_id'):  OR IS FINISHED
58) Done: Check swap pane on work bench
59) DONE Moved tabstrip to be first class member of form
52) DONE tabstrip border = -5.  ugly in the api.
37) DONE show less tabs on startup.
47) Done: add init guard to _basePane
45) Done: remove closure factory from log
63) Done: Reorganize folders and package for PIP TOML, __init... all that bullshit
65) Done: on base widget is_disabled is not consistent with visible... prefer enabled
68) Done: Created Directed Acyclic Graph (DAG) to provide Declarative/Reactive option if desired over imperative.
37) Done:Fix header on Forge Prev+iew
30) Done:Fix funky text in workbench current design
71) Done:Network Diagram click not working
38) DONE: Grid change api from setdata to data.
61) DONE: Migrate everything to new Grid
33) DONE in colosseum put status up and remove that first card on left pane.
66) DONE not loving the Text's names for sizes.  label1,2,3,4,5 might work better...
71) DONE: Add Codebox
80) Improve (Scrollable containers forbidding width_flex/height_flex on children
71) DONE: Codebox not showing full length
73) DONE: 2nd registry by form.
75) DONE: Add DAG Info To WidgetTree
91) DONE: Fix issue where expected to scroll and it doesn't.
#******************************************************************
####################################################### 3/1
#******************************************************************
81) DONE: Fixed defect where fallback to create file if tab file doesn't exist only had one pane.
82) DONE: Fixed defect where if text had glow=true newline would fail
83) DONE: Allow tab dict to have single pane as value instead of requiring list notation.
87) DONE: Built X-Ray Diagnotstic tool.  F12 toggles to bring up widget tree and inspect the details of any object
88) DONE: Fix F12 toggle and form caption name issue
90) Tackle scrolling issue and ITERATIVE FLEX ALLOCATION
86) DONE: kill the log intercept
91) DONE: Fixed layout issue on widgets.
96) DONE: Rename width_flex and height_flex
112) DONE: Fixed defect with textbox not syncing to pyline on open.
97) DONE:Move src\forms to src\ipui\forms
35) DONE:Eliminate drift for printing newline. (example: parent.form.show_modal(f"Coming Soon:\n{sel[0]})
113) DONE: fix defect where network diagram collapsed
#******************************************************************
####################################################### 3/8
#******************************************************************
114) Done: Fixed he defect on the dropdown box
89)  Done fix name collision on tree
115) DONE:Put code on freebie tab.
116) DONE: finish dev tools
117) DONE: add to pitch... if your mssing a page, we don't throw an error. we offer to build it.
134) DONE: Create Name reference documentation
135) Done: Name audit with 55 updates.
67) DONE: clean up the files in docs/forms
102) wDONE: e should double check that it pulls from source code  quickly(wid catalog) and every time it print that...   i feel
50) CANCELED: Replace ProjectListItem with standard widget
79) DONE: Gracefully handle if the tab file exists but is missing the 'pane method'
69) Done: On neuroforge, change menu button in top left to "Back To Docs"
70) Done: On neuroforge, make header buttons same width.
72) DONE: need to resolve timing issue on firealltrigs
74) DONE: control is not consistent... widget every where else.
62) DONE: In widget do we need the name... it duplicates the class and could create drift.
93) DONE: Replace impossible with hard.
108) DONE:  Readme: he build() Not __init__ section appears before I know what a widget is — feels premature. I don't yet know why I'd care
109)  DONE: Readme: The "Two Ways to Update" section has a TODO comment left in (TODO show third way) — breaks the polished feel
110)  DONE: README:IPUI.show() vs IPUI(MyApp, "...") — the Quick Start uses one form, the "Launching Your App" section shows another. Which is canonical?
111)  DONE: Cap Tabl Layout like Declaration updates.

######################################################################
######################################################################
######################################################################





48) Colosseum has manual list of config cats
51) is frmPro needed?  If not, delete.
60) PART OF LAMBDA ELIMINATION: investigate swap_pane in forge and more generic alternatives uch as Button(header, "+New", on_click_args=(self.form.set_pane, 1, self.name_project))
76) Set Pane, instead of requiring lambda, use kwargs for params aka instead of #self.form.set_pane(1, lambda p: self.show_detail(p, item))   - how does this play with on_click_me
77) add email to metadata
78) add alpha classifier to package info.
83) we need TemplateShowcase.py OR FIX Button to temporarily show other file.
92) Fix readme in doc tools

94) ensure no reference to _ipui or _BaseForm
95) wid in widget overlay from tree is wrong - look at other example of tree where it is correct


98) Move docs\popups to ipui\popups
99) Move docs\forms to src\ipui\forms)
100) add to benfits in read me framework takes responsibility of flutters super.initstate and reacts dependency array.
101) Remember what 101 was...

103) add troubleshoot buttons on magic debugger tool.
104  Detail widget not working with 2 standard imports.............
105) add hooks for user to pygame updateloop
106) on freebies replace developer tools.
107) on tab map green indicator does not follow selected button

118) fix issue with space in tabname.
119) remove name drom doc strings.
120) add  third pane to paradigm explaining it.
130) Error on Percy's story
131) on neuroforge demo createback button
132) on particle life demo create back button
133) Both widget references must be changed to ignore name and use the class name.
134) matplotlib widget needs to be added to readme

######################
##########################################################
Punting until after IPUI is on PIP
##########################################################
42) modal choose your own adventure widget.
43) APPENDIX A:  Lambda-Free Callbacks for _BaseWidget
44) check Armory for unneeded lambdas
64) Add support for Noto Color Emoji
29) Add Output neuron automatically and add the words Output or Hidden
41) Protect our savants from Guido
21) Record LR Sweep to DB
22) Record AutoML to DB
23) Project overview tab.
26) Fix Analysis tab
12) Ensure everything important is being logged.
28) Add ability to store notes on Batch/Run
49) get rid of extra calc_total_runs
39) Add spot for them to store notes
84) Switch font Roboto → Noto Sans - better unicode coverage
85) in widget catalog name is redundnant.
112) network diagram must let it's children propogate down.
##########################################################
Punting to phase 2 of NeuroForge
##########################################################

10) add adam parameters to config options.  Do not show in middle panel




APPENDIX A:  Lambda-Free Callbacks for _BaseWidget
Every widget always passes form first, then whatever that widget naturally produces. No lambdas, no closures, no timing bugs. Form resolved at fire time from self.form.
WidgetWhat it knowsCallback signatureButtonnothingcallback(form)SelectionListselected itemscallback(form, selected)DataGridclicked row datacallback(form, value)
python# Before (lambda everywhere):
btn.on_click = lambda: frmMatch.on_paste_seeds(form)
sel = SelectionList(..., on_change=lambda selected: frmMatch.update_config_summary(form, selected))
grid... # 11 lines of plumbing

# After (just pass the function):
btn.on_click(frmMatch.on_paste_seeds)
sel = SelectionList(..., on_change=frmMatch.update_config_summary)
grid.on_row_click(frmLudus.load_batch_runs, "Batch")
Implementation: _BaseWidget stores callback + args. When firing, calls callback(self.form, *args). Validation at registration time. Affects on_click, on_change, on_hover.

APPENDIX B: FULL GRID LIST
DATAGRID TODO
✅ SHIPPED (v0.1 core)

Three input formats (list-of-lists, list-of-dicts, dict-of-lists)
First-class header row (no more manual skip-row-0)
Sortable columns (click header, ^ / v indicator)
Per-column alignment (auto-detected, duck-typed for SQLite strings)
Decimal alignment (normalized precision per column)
Zebra striping (on by default)
Auto-sized columns with optional max
Gap-based space distribution
Hover suppression
on_row_click(callback, column) API
Scroll via parent CardCol

🔨 v0.1 POLISH (before ship)

Lambda-free callbacks (separate effort, _BaseWidget level)
set_column for per-column format/color overrides
row_height / header_height properties
stripe_color property (currently hardcoded)
columns_order param for display reordering

🔥 v0.2 — DataGridSQL (the killer feature)
pythongrid = DataGridSQL(card,
    db="training.db",
    query="SELECT * FROM batches WHERE date > ? ORDER BY best_mae",
    params=("2024-02-20",),
    refresh_every=5000,
    name="live_grid")

Own connection per query (open/close, no shared state)
LIMIT/OFFSET paging at DB level
Click-to-sort rewrites ORDER BY
Right-click cell → filter (wraps original as subquery)
Clear filters reset
Parameterized queries (no SQL injection)
Auto-refresh timer

🚀 v0.3 — POWER FEATURES

Virtual scrolling for 100k+ rows
Export (CSV / JSON / Clipboard) header menu
Right-click context menu (Hide / Pin / Filter)
Draggable column reorder
on_cell_doubleclick callback
selected_rows multi-select property
Optional pandas=True mode for pd.read_sql integration

package setup to dos
# MgrFont.py method: FONT_DIR  Update: package-relative path
FONT_DIR = "src/assets/fonts"                              
FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")  # NEW

"""