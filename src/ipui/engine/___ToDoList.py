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
3/10
######################################################################
99) DONE: Move docs\forms to src\ipui\forms)
94) DONE: ensure no reference to _ipui or _BaseForm
77) DONE:add email to metadata
78) DONE:add alpha classifier to package info.
119) DONE: remove name from doc strings.
98)  DONE: Move docs\popups to ipui\popups
51) DONE: is frmPro needed?  If not, delete.
156) DONE: Make NeuroForge Pro a combo of armory and Forge.
133) DONE: Both widget references must be changed to ignore name and use the class name.
100) DONE: add to benfits in read me framework takes responsibility of flutters super.initstate and reacts dependency array.
134) DONE: matplotlib widget needs to be added to readme
131) DONE: on neuroforge demo createback button
118) DONE: fix issue with space in tabname.
160) DONE: scroll bar must be draggable
162) DONE: Fixed Pipeline → TextBox sync (Clear button works)
163) DONE: Trimmed the Paradigm tab
164) DONE: Added scroll_top_inset + private_handle_rect to base scroll
165) DONE: Built PowerGrid2 with proper child architecture — header, scroller, body, record selector all as real widgets
166) DONE: Unified scrollbar — deleted all custom scroll code from PowerGrid
167) DONE: Added scrollbar drag to _BaseWidget — every scrollable widget gets it for free
######################################################################
3/11
######################################################################
105) DONE: add hooks for user to pygame updateloop
132) DONE:  DP on particle life demo create back button
157) DONE: Grid blows up when sorting mixed data types.  Name in tree for example.
162)  DONE: in ctx reverse events.... we want to encourage the small list.
159) DONE: BEFORE ANYTHING.  Standardize label and textbox printing.
135. DONE:Click-to-position cursor — ours always puts cursor at the end
136. DONE:Left/Right arrow keys to move cursor within text
137. DONE:Home/End keys to jump to start/end
138. DONE:Ctrl+Left/Right to jump word-by-word
139) DONE:Shift+Arrow to select a range
140) DONE:Shift+Home/End for select-to-boundary
141) DONE:Ctrl+A to select all
142) DONE:Click-and-drag to select with mouse
143) DONE:Double-click to select a word
144) DONE:Visual highlight rendering of selected text
145) DONE:Ctrl+C copy selection
146) DONE:Ctrl+V paste (replacing selection if any)
147) DONE:Ctrl+X cut selection
148) DONE: (Cross-platform — currently Windows-only)
149) DONE:Delete key (forward delete)
150) DONE:Ctrl+Backspace delete word backward
151) DONE:Typing replaces selection when text is selected
152) DONE:Overflowing text scrolls horizontally — currently text just renders off the right edge
153) DONE:Text clipping — long text shouldn't bleed outside the box
154) Scroll offset so cursor is always visible when text exceeds box width
######################################################################
3/12
######################################################################
169) Created IP.   One stop shopping for IPUI api
######################################################################
3/13
######################################################################
168) DONE: Created TabArea  as first class widget
169) DONE: Created Pane as first class widget
171) DONE: None gaps work — renderpre shows through
172) DONE: Tab switching works
173) DONE: set_pane with args works
174) DONE: Data is cleaned once at startup
175) DONE: 4th pane bug fixed — deleted the rogue Col in TabStrip's None branch that was giving Armory (and Breakout) an extra phantom pane
176) DONE: Full Breakout game — arcade game running inside a None pane, all normalized coordinates, every method under 10 lines, playable and fun
177) DONE: Tree debugger widget_type fix — self.widget_type → widget.widget_type
178) DONE: display_name property — single source of truth on _BaseWidget for human-readable identity, kills my_name references everywhere
179) DONE: gather_properties cleanup — my_name → widget_type + class + proper registry name
180) DONE: ix — same my_name / type() drift issue
181) DONE: draw_diagnostic_widget fix — uses display_name now
182) DONE: TabButtons naming — "TabButtons Border" / "TabButtons Content" for debugger clarity
183) DONE: Auto-refresh Tree — ip_think refreshes when active, no stale data
184) DONE: PowerGrid scroll preservation — commented out the reset-to-top in set_data
185) DONE: API design work — ip.every_seconds(0.5, callback) designed, ready to build
190) DONE: MarkdownTOC.py — New widget. Scans a markdown file, extracts TOC entries (explicit - [Title](#anchor) format or fallback to ## headings), strips emojis, renders as a single-select SelectionList with sunken/glow selection pattern. Supports initial_value for persistence across tab switches. Passes slugs via on_change for reliable section matching.
191) DONE: MarkdownBody.py — New widget. Renders a single ## section from a markdown file, matched by slug. Handles headings, bullets, code blocks, spacers. Strips emojis from display text. CodeBox trailing newline fix prevents single-line code strings from being treated as file paths.
192) DONE: Reference.py — Rewritten. Renamed class Ref → Reference. One pane method per mode (pane_widgets, pane_markdown). Shared build_menu helper with green highlight on active mode button. Pane state stored as instance attributes (active_mode, active_toc_slug) instead of polluting the pipeline. TOC selection persists across tab switches. Widget catalog still fully functional.
193) DONE: general_text.py — Added EMOJI_PATTERN, strip_emojis(), and strip_for_md_toc() as shared utilities.
194) DONE: Slug matching system — TOC display titles and ## headings matched via GitHub-style slug generation. Handles emoji stripping, backtick stripping, and leading dash edge case.
195) DONE: Deprecated MarkdownView
######################################################################




60) PART OF LAMBDA ELIMINATION: investigate swap_pane in forge and more generic alternatives uch as Button(header, "+New", on_click_args=(self.form.set_pane, 1, self.name_project))
76) Set Pane, instead of requiring lambda, use kwargs for params aka instead of #self.form.set_pane(1, lambda p: self.show_detail(p, item))   - how does this play with on_click_me
83) we need TemplateShowcase.py OR FIX Button to temporarily show other file.
92) Fix readme in doc tools
95) wid in widget overlay from tree is wrong - look at other example of tree where it is correct
101) Remember what 101 was...
103) add troubleshoot buttons on magic debugger tool.
104  Detail widget not working with 2 standard imports.............

106) on freebies replace developer tools.
107) on tab map green indicator does not follow selected button



155) Armory needs 3rd pane.
120) add  third pane to paradigm explaining it.
130) Error on Percy's story
158) Tab Order
159) 86 the friggen set_enable set_disable.

161) debug tools must auto-refresh


163) move double click detect to base wid
164) If autoscaffold tab with space in name itmesses up file and class
165 screw our shitty text align... create string :(
167) SQL recordselector behaving off. compare it to tree
170) Remove all the references to my_name
186) Read me should mention debug tools
187) Read me should mention f11 - rect shower
188) MD viewer should respect bold tag.
189) MD viewer shuold render table.
196) create table widget.
197) Scrollbar should not honor the token to the right.(leaves a gap)





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
48) Colosseum has manual list of config cats
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