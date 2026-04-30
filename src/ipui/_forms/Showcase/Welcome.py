from ipui import *
from ipui import *

class We_HopeYouLoveIPUI(_BaseTab):
    """Opening tab of showcase/documentation"""

    # ══════════════════════════════════════════════#
    #  The code that produces the left pane         #
    # ══════════════════════════════════════════════#

    def left_pane(self, parent):
        self.greet  (parent)
        self.summary(parent)
        self.code   (parent)

    def greet(self , parent):
        card        = Card(parent)
        Title       ( card, "Welcome to", text_align=CENTER)
        box         = Plate(card,text_align=CENTER,pad_x=30, border=6)
        Banner      ( box, "IPUI", text_align=CENTER, glow=True, hug_parent=True) #shrink the box down to child size
        Heading     ( card, "A python framework", text_align=CENTER)

    def summary(self, parent):
        card        = Card(parent)
        Heading     ( card, "- Declarative flex-based layout.")
        Heading     ( card, "- Multiple update styles.")
        Heading     ( card, "- Full pygame control.")

    def code(self, parent):
        card        = Card(parent)
        Title       ( card, "Code for this page", text_align=CENTER,glow=True,name="msg")
        this_code   = Card(parent, scrollable=True)

        # The below line creates the Widget you are reading right now!
        CodeBox     ( this_code,  data=__file__, start="# ═══════════", end="def detail_ez_err")

    #  ══════════════════════════════════════════════════════════════
    #  Middle Pane
    #  ══════════════════════════════════════════════════════════════
    def proud_features(self, parent):
        Body(parent, "")
        row=Row(parent)
        Title(parent, "Select a feature to view details", text_align=CENTER)
        Body(parent, " ")
        our_features_scroll_box = Card(parent, scrollable=True, name="ourfeatures",pad=10,gap=25)

        # Create about 20 feature cards
        for i, feature in enumerate(self.FEATURES, start=1):
            self.feature_card(our_features_scroll_box, i, feature)

    def need_delegate_from_json(self, feature):
        self.form.set_pane(2, feature["detail"])

    def feature_card(self, parent, number, feature):
        whole_card   = Plate(parent ,color_bg=Style.COLOR_PANEL_BG , on_click=lambda f=feature: self.need_delegate_from_json(f))
        title_row    = CardRow      (whole_card)
        Icon         ( title_row    ,feature["icon"])
        Heading      ( title_row    ,feature["title"],glow=True)
        Heading      ( title_row    ,text=f"{number}", text_align=RIGHT)
        summary_card = Card         (whole_card)
        Body         ( summary_card ,feature["summary"])
        joke_card    = Card         (whole_card)
        Body         ( joke_card,   feature["joke"])
        Heading      ( whole_card,  feature["tag"])

    def detail_debug_tools(self, parent):
        Title(parent, "Pro Level Debug Tools", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Widget Tree (F12)", glow=True)
        Body(card, "A live, interactive tree of every widget in your running app. "
                   "Click any node to inspect its properties, rect, flex settings, "
                   "and parent chain. Copy the full tree to clipboard with one click.")

        card = Card(scroll)
        Heading(card, "Layout Overlay (F11)", glow=True)
        Body(card, "Toggle translucent outlines on every widget to see exactly "
                   "where the layout engine placed them. Padding, gaps, alignment — "
                   "all visible instantly, right on your running app.")

        card = Card(scroll)
        Heading(card, "Widget Locator", glow=True)
        Body(card, "Click a widget in the tree and it pulses on screen. "
                   "Click on screen and the tree jumps to that node. "
                   "Two-way navigation between code and pixels.")

        card = Card(scroll)
        Heading(card, "Zero Setup", glow=True)
        Body(card, "No flags, no config, no imports. These tools ship with every "
                   "IPUI app automatically. Press F12 right now and see for yourself.")

    def detail_ez_err(self, parent):
        Title(parent, "EZ.err", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Clickable Error Links", glow=True)
        Body(card, "Every error message includes a PyCharm-clickable file:line reference "
                   "that points to YOUR code — the line where you made the mistake, "
                   "not some framework internal you've never seen.")

        card = Card(scroll)
        Heading(card, "Actionable Guidance", glow=True)
        Body(card, "Error messages don't just say what went wrong. They tell you how to fix it. "
                   "Wrong parameter? Here are the valid options. Missing method? "
                   "Here's the exact signature to add.")

        card = Card(scroll)
        Heading(card, "Construction-Time Catches", glow=True)
        Body(card, "Override __init__ in a widget? TypeError at class definition. "
                   "Pass text_align='x'? ValueError at construction. "
                   "Typo in widgets['name']? RuntimeError listing every valid name.")

        card = Card(scroll)
        Heading(card, "Houston, We Have a Problem", glow=True)
        Body(card, "Every IPUI error starts with this line so you can instantly tell "
                   "a framework diagnostic from a raw Python traceback. "
                   "Errors should be findable, not just readable.")

    def detail_icon_widget(self, parent):
        Title(parent, "Emotes in Pygame", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "One Line, Full Color", glow=True)
        Body(card, "Icon(parent, 'fire') — that's it. Full color emoji rendered as "
                   "a first-class widget. Drop them in cards, rows, titles, toolbars, "
                   "anywhere you'd put any other widget.")

        card = Card(scroll)
        Heading(card, "No Atlas Required", glow=True)
        Body(card, "No sprite sheets, no texture packing, no asset pipelines. "
                   "IPUI ships with the emoji set built in. "
                   "Pick a name, get a glyph.")

        card = Card(scroll)
        Heading(card, "Lazy Caching", glow=True)
        Body(card, "Each emoji is rendered once and cached. Use the same icon "
                   "a hundred times and it's still just one surface in memory. "
                   "Performance without effort.")

    def detail_tab_system(self, parent):
        Title(parent, "First-Class Tab System", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "One Dictionary, Entire App", glow=True)
        Body(card, "TAB_LAYOUT maps tab names to lists of pane builders. "
                   "That single declaration at the top of your Form defines "
                   "every screen, every column, every content area.")

        card = Card(scroll)
        Heading(card, "Automatic Pane Splitting", glow=True)
        Body(card, "Need three columns? List three method names. Need a wide center pane? "
                   "Add a weight tuple. The tab strip and pane containers are built for you.")

        card = Card(scroll)
        Heading(card, "Dynamic at Runtime", glow=True)
        Body(card, "set_pane() swaps content on the fly. hide_tab() and show_tab() "
                   "control visibility. switch_tab() navigates programmatically. "
                   "The structure is declarative but the behavior is fully dynamic.")

        card = Card(scroll)
        Heading(card, "Clean Modularity", glow=True)
        Body(card, "Each tab's logic lives in its own _BaseTab subclass. "
                   "The form doesn't know or care what's inside each tab. "
                   "Add a tab, write a class, done.")

    def detail_resolution_independent(self, parent):
        Title(parent, "Resolution Independent", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Automatic Scaling", glow=True)
        Body(card, "IPUI measures your physical screen height and scales every font, "
                   "padding token, and border thickness to match. "
                   "Your app looks proportional everywhere, automatically.")

        card = Card(scroll)
        Heading(card, "No Pixel Constants", glow=True)
        Body(card, "Style tokens like TOKEN_PAD and TOKEN_GAP are computed from "
                   "screen height, not hard-coded. Move your app between a laptop "
                   "and a 4K monitor and everything just works.")

        card = Card(scroll)
        Heading(card, "FONT_SCALE", glow=True)
        Body(card, "A single scaling factor controls the entire type hierarchy. "
                   "Banner, Title, Heading, Body, Detail — all derived from one "
                   "ratio so they stay in harmony at any resolution.")

    def detail_declarative_layout(self, parent):
        Title(parent, "Declarative Layout", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Width Down, Height Up", glow=True)
        Body(card, "Parents assign width to children. Children report their height "
                   "back up. This two-pass rule eliminates the circular dependencies "
                   "that make other layout engines unpredictable.")

        card = Card(scroll)
        Heading(card, "Flex Splits the Remainder", glow=True)
        Body(card, "After fixed-size children are measured, leftover space is divided "
                   "among flex children by weight. width_flex=2 gets twice the space "
                   "of width_flex=1. No pixel math required.")

        card = Card(scroll)
        Heading(card, "Cards Stack, Rows Flow", glow=True)
        Body(card, "Card stacks children vertically. Row lays them out horizontally. "
                   "Nest them freely. The engine handles the rest — padding, gaps, "
                   "borders, and alignment all come from the widget, not from you.")

        card = Card(scroll)
        Heading(card, "Text Wrapping Just Works", glow=True)
        Body(card, "Body text wraps to fit its container width automatically. "
                   "No manual line breaks, no width calculations, no viewport setup. "
                   "Resize the window and the text reflows.")

    def detail_built_to_extend(self, parent):
        Title(parent, "Built to Extend", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Inherit Everything", glow=True)
        Body(card, "Subclass _BaseWidget and your custom widget immediately gets "
                   "layout, clipping, scrolling, events, bevel styling, and the "
                   "debug inspector. You just write the part that's yours.")

        card = Card(scroll)
        Heading(card, "5-10 Lines Typical", glow=True)
        Body(card, "A standard IPUI widget is a build() method and maybe a measure(). "
                   "Label, Button, Spacer — none of them are magic. "
                   "They're just small classes using the same tools you have.")

        card = Card(scroll)
        Heading(card, "Complex Tools Stay Small", glow=True)
        Body(card, "The NetworkDiagram widget — a drag-and-drop node editor with "
                   "connections — is under 150 lines. PowerGrid with sorting, "
                   "pagination, and SQL support is one file. The framework does the heavy lifting.")

    def detail_one_touch_scrolling(self, parent):
        Title(parent, "One-Touch Scrolling", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "scrollable=True", glow=True)
        Body(card, "Add one parameter to any Card and it scrolls. Mouse wheel, "
                   "draggable scrollbar, styled automatically. "
                   "This detail pane you're reading right now is a scrollable Card.")

        card = Card(scroll)
        Heading(card, "No Viewport Plumbing", glow=True)
        Body(card, "No clip rects to manage, no scroll offsets to track, no "
                   "content-height calculations. The framework measures the content, "
                   "sizes the scrollbar, and clips the overflow. You just build.")

        card = Card(scroll)
        Heading(card, "Nested Scrolling", glow=True)
        Body(card, "Put a scrollable Card inside another scrollable Card and both work. "
                   "The input system routes scroll events to the deepest scrollable "
                   "widget under the mouse. No conflicts, no stealing.")

    def detail_construction_attachment(self, parent):
        Title(parent, "Construction IS Attachment", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Build It, It's Attached", glow=True)
        Body(card, "Button(card, 'Save') — the button exists and it belongs to card. "
                   "No add(), no append(), no parent.children.insert(). "
                   "The constructor IS the attachment call.")

        card = Card(scroll)
        Heading(card, "No Orphans Possible", glow=True)
        Body(card, "Every widget constructor requires a parent as the first argument. "
                   "You literally cannot create a widget that doesn't belong somewhere. "
                   "Floating widgets don't exist in IPUI.")

        card = Card(scroll)
        Heading(card, "Reads Like a Blueprint", glow=True)
        Body(card, "Your pane builder method reads top-to-bottom like the UI looks "
                   "top-to-bottom. Indentation shows nesting. "
                   "The code IS the layout.")

    def detail_multiple_update_styles(self, parent):
        Title(parent, "Multiple Update Styles", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Reactive DAG", glow=True)
        Body(card, "Declare DECLARATION_UPDATES on your pane and pipeline changes "
                   "automatically recompute derived values and push them to widgets. "
                   "Change one key, the whole chain updates.")

        card = Card(scroll)
        Heading(card, "Pipeline Sync", glow=True)
        Body(card, "Give a widget a pipeline_key and it stays in sync with the "
                   "pipeline store automatically. No manual reads, no callbacks. "
                   "The widget and the data are bound.")

        card = Card(scroll)
        Heading(card, "Direct Widget Access", glow=True)
        Body(card, "Sometimes you just need form.widgets['my_label'].set_text('done'). "
                   "That works too. No framework police, no pattern lectures. "
                   "Use what fits the problem.")

        card = Card(scroll)
        Heading(card, "Mix Freely", glow=True)
        Body(card, "Use reactive derives for complex calculations, pipeline sync for "
                   "form fields, and direct access for one-off updates. "
                   "All three work in the same pane, same frame, no conflicts.")

    def detail_data_pipeline(self, parent):
        Title(parent, "Data Pipeline", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Central Key-Value Store", glow=True)
        Body(card, "pipeline_set(key, value) writes. pipeline_read(key) reads. "
                   "One source of truth for your app's state, "
                   "visible and debuggable from the F12 tools.")

        card = Card(scroll)
        Heading(card, "Automatic Widget Sync", glow=True)
        Body(card, "Give a TextBox a pipeline_key and its value flows into the pipeline "
                   "on every keystroke. Read it from any tab with pipeline_read(). "
                   "No manual wiring between screens.")

        card = Card(scroll)
        Heading(card, "Derived Values", glow=True)
        Body(card, "Register a derive: when source keys change, a compute function "
                   "runs and pushes the result to a target widget. "
                   "Spreadsheet-style reactivity with zero boilerplate.")

        card = Card(scroll)
        Heading(card, "Cross-Tab Communication", glow=True)
        Body(card, "Tab A writes to the pipeline. Tab B reads from it. "
                   "No shared globals, no event buses, no import tangles. "
                   "The pipeline is the shared bus and it's already there.")

    def detail_lifecycle_hooks(self, parent):
        Title(parent, "Pygame Lifecycle Hooks", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "ip_think(ip)", glow=True)
        Body(card, "Runs every frame before layout. This is where your logic lives — "
                   "physics, AI, state machines, animation timers. "
                   "ip.dt gives you the delta time.")

        card = Card(scroll)
        Heading(card, "ip_draw(ip)", glow=True)
        Body(card, "Runs after layout, before the widget tree draws. "
                   "Paint backgrounds, game worlds, particle fields — anything "
                   "that should appear behind the UI widgets.")

        card = Card(scroll)
        Heading(card, "ip_draw_hud(ip)", glow=True)
        Body(card, "Runs after the widget tree draws. Custom cursors, score overlays, "
                   "selection highlights — anything that floats on top of the UI. "
                   "Full pygame surface access, no restrictions.")

        card = Card(scroll)
        Heading(card, "Framework Gets Out of the Way", glow=True)
        Body(card, "IPUI manages the game loop, input snapshot, and display flip. "
                   "You get clean hooks at the right moments. "
                   "Build a full game or a data dashboard — same three hooks.")

    def detail_multi_tier_tooltips(self, parent):
        Title(parent, "Multi-Tier Tooltips", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Standard Hover Tips", glow=True)
        Body(card, "Add tooltip='hint text' to any widget. A lightweight popup follows "
                   "the mouse on hover. Simple, non-invasive, zero setup.")

        card = Card(scroll)
        Heading(card, "Super Tooltips", glow=True)
        Body(card, "For deep data — full scrollable panels that expand after a brief "
                   "hover delay. They can contain tables, property lists, "
                   "and multi-column layouts.")

        card = Card(scroll)
        Heading(card, "Pin and Dock", glow=True)
        Body(card, "Super Tooltips can be pinned to either side of the screen. "
                   "Once pinned, they stay visible while you interact with the rest "
                   "of the app. Click to move, click to close.")

        card = Card(scroll)
        Heading(card, "Temporal Guardrails", glow=True)
        Body(card, "A staggered reveal prevents misclicks: hover triggers the tip, "
                   "a short delay expands it, another delay reveals the pin button. "
                   "Every transition is intentional, never accidental.")

    def detail_widget_registry(self, parent):
        Title(parent, "Automatic Widget Registry", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Name It, Find It", glow=True)
        Body(card, "Button(parent, 'Save', name='btn_save') — now it's in the registry. "
                   "Access it from anywhere: form.widgets['btn_save']. "
                   "No globals, no reference chains, no imports.")

        card = Card(scroll)
        Heading(card, "Cross-Pane Access", glow=True)
        Body(card, "A button on Tab A can read a TextBox on Tab B by name. "
                   "The registry spans the entire form. "
                   "No need to restructure your code to pass references around.")

        card = Card(scroll)
        Heading(card, "Typo Protection", glow=True)
        Body(card, "Access a name that doesn't exist and you get a RuntimeError "
                   "listing every valid registered name. "
                   "Typos fail loudly instead of returning None silently.")

    def detail_code_boxes(self, parent):
        Title(parent, "Beautiful Code Boxes", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "String or File Path", glow=True)
        Body(card, "Pass a string and it renders as formatted code. "
                   "Pass a file path and IPUI reads it for you. "
                   "One widget, two input modes, zero hassle.")

        card = Card(scroll)
        Heading(card, "Range Extraction", glow=True)
        Body(card, "Use start= and end= markers to show just a slice of a file. "
                   "Perfect for self-documenting apps that display their own source. "
                   "The Welcome tab you're looking at does exactly this.")

        card = Card(scroll)
        Heading(card, "Scrollable and Styled", glow=True)
        Body(card, "Long code blocks scroll automatically. Mono font, dark background, "
                   "proper padding — code looks like code, not like a paragraph "
                   "that got lost.")

    def detail_tab_map(self, parent):
        Title(parent, "Tab Map", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Bird's-Eye View", glow=True)
        Body(card, "See every tab and every pane in your application laid out "
                   "in a single scrollable list. Know your app's full structure "
                   "at a glance.")

        card = Card(scroll)
        Heading(card, "Click to Preview", glow=True)
        Body(card, "Select any pane from the map and see its content rendered "
                   "in a live preview. Navigate your app's structure "
                   "without switching tabs.")

        card = Card(scroll)
        Heading(card, "Structural Sanity Check", glow=True)
        Body(card, "As your app grows past a handful of tabs, the Tab Map "
                   "keeps you honest. Spot orphaned panes, uneven layouts, "
                   "and forgotten screens before your users do.")

    def detail_grid(self, parent):
        Title(parent, "PowerGrid", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Three Input Formats", glow=True)
        Body(card, "Feed it a list of lists, a list of dicts, or a SQLite query. "
                   "PowerGrid normalizes the data and renders it. "
                   "One widget, three on-ramps.")

        card = Card(scroll)
        Heading(card, "Sort Across Pages", glow=True)
        Body(card, "Click a column header to sort. Sorting operates on the full "
                   "dataset, not just the visible page. Pagination is automatic — "
                   "set page size and PowerGrid handles the rest.")

        card = Card(scroll)
        Heading(card, "SQL-Ready", glow=True)
        Body(card, "Point PowerGrid at a SQLite database and table name. "
                   "It reads the schema, builds the columns, and paginates the results. "
                   "From database to data grid in three lines.")

        card = Card(scroll)
        Heading(card, "Not a Demo Grid", glow=True)
        Body(card, "Handles thousands of rows, mixed types, missing values, "
                   "and column resizing. This is a working data grid, "
                   "not three hard-coded rows in a conference talk.")

    def detail_documenting(self, parent):
        Title(parent, "Self-Documenting", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Docs From Source", glow=True)
        Body(card, "IPUI's built-in reference reads widget docstrings and class "
                   "structure directly from the framework source code. "
                   "When the code changes, the docs change.")

        card = Card(scroll)
        Heading(card, "Widget Catalog", glow=True)
        Body(card, "Every widget's description, parameters, and usage example "
                   "are generated from its class definition. "
                   "No separate docs file to forget to update.")

        card = Card(scroll)
        Heading(card, "Searchable Reference", glow=True)
        Body(card, "The F12 debug tools include a full reference tab with "
                   "table of contents navigation and section rendering. "
                   "Find what you need without leaving your app.")

    def detail_live_charts(self, parent):
        Title(parent, "Live Matplotlib Charts", glow=True)
        scroll = Card(parent, scrollable=True)

        card = Card(scroll)
        Heading(card, "Real-Time Updates", glow=True)
        Body(card, "Chart renders a matplotlib figure directly onto a pygame surface. "
                   "Update the data every frame and the chart redraws live — "
                   "training curves, sensor data, experiment monitoring.")

        card = Card(scroll)
        Heading(card, "Full Matplotlib Power", glow=True)
        Body(card, "Anything matplotlib can draw, Chart can display. "
                   "Line charts, bar charts, scatter plots, heatmaps — "
                   "use the full matplotlib API, rendered inside your IPUI app.")

        card = Card(scroll)
        Heading(card, "No Window Juggling", glow=True)
        Body(card, "Most pygame apps that want charts pop open a separate matplotlib window. "
                   "Chart embeds the chart inline as a widget. "
                   "One app, one window, one focus.")

    FEATURES = [
            {
                "icon":    "boom",
                "title":   "Pro Level Debug Tools",
                "tag":     "Dev Tools, Widgets",
                "summary": "Hit F12 right now. Seriously.\n\nWe take 'making it easy for you to resolve issues' very seriously.  ",
                "joke":    "You get a live widget tree, property inspector, layout overlays, and a widget locator that pulses on screen. All built in, zero setup, and that is just the first tab.",
                "detail":  "detail_debug_tools",
            },
            {
                "icon":    "attachment",
                "title":   "Construction IS Attachment",
                "tag":     "Structure, UX",
                "summary": "Build a widget inside a container and it's attached. No floating widgets, no add() calls, no orphans. If it exists, it belongs somewhere.",
                "joke":    "A widget that exists but isn't attached is a ghost, not a feature.",
                "detail":  "detail_construction_attachment",
            },
            {
                "icon": "tab_system",
                "title": "First-Class Tab System",
                "tag": "Structure, Layout",
                "summary": "Define your entire app's tabs and pane layout from a single dictionary. IPUI scaffolds the structure and keeps each tab cleanly modular.",
                "joke": "Because manually wiring twelve screens together is how people end up muttering at monitors.",
                "detail": "detail_tab_system",
            },
            {
                "icon": "parachute",
                "title": "EZ.err",
                "tag": "Dev Tools, Structure",
                "summary": "As I built IPUI, when I hit an error I thought: if I just made this mistake, others will too. What hints can I give them? So I double-check the link points to the right line and send it to a custom error handler with real guidance.",
                "joke": "Because 'line 1 in some file somewhere' builds character, not software.",
                "detail": "detail_ez_err",
            },
        {
            "icon": "fire",
            "title": "Emotes in Pygame",
            "tag": "Widgets, UX",
            "summary": "Full color emoji as first-class widgets. Drop anywhere — cards, titles, rows, toolbars, with a SINGLE line of code.  ZERO atlas management required and lazy caching for performance.",
            "joke": "Because your pygame app deserves to express itself.",
            "detail": "detail_icon_widget",
        },

            {
                "icon":    "resolution",
                "title":   "Resolution Independent",
                "tag":     "Layout, UX",
                "summary": "UI scales automatically to physical screen height. Looks sharp on an old laptop or a 4K monitor with zero manual adjustment.",
                "joke":    "So your app doesn't look adorable on one screen and completely unhinged on another.",
                "detail":  "detail_resolution_independent",
            },
            {
                "icon":    "layout",
                "title":   "Declarative Layout",
                "tag":     "Layout, Structure",
                "summary": "Width flows down, height flows up. Flex splits remaining space. Simple rules, no pixel math, no fighting the engine.",
                "joke":    "Because life is too short to spend it negotiating with pixel coordinates.",
                "detail":  "detail_declarative_layout",
            },
            {
                "icon":    "extensible",
                "title":   "Built to Extend",
                "tag":     "Widgets, Structure",
                "summary": "Custom widgets inherit layout, events, and styling automatically. Standard widgets are 5-10 lines. Even complex tools like network diagrams come in under 150.",
                "joke":    "Write the widget you actually want, not the one your framework guilts you into accepting.",
                "detail":  "detail_built_to_extend",
            },
            {
                "icon":    "scroll",
                "title":   "One-Touch Scrolling",
                "tag":     "Layout, Widgets, UX",
                "summary": "Make any container scrollable with scrollable=True. Draggable scrollbars, styled automatically. This feature list is one scrollable Card.",
                "joke":    "Because 'just make it scroll' should not become a weekend project.",
                "detail":  "detail_one_touch_scrolling",
            },

            {
                "icon":    "reactive",
                "title":   "Multiple Update Styles",
                "tag":     "Data, Structure",
                "summary": "DAG-based reactivity, pipeline synchronization, or direct widget access. Pick what fits the job. Mix them freely in the same pane.",
                "joke":    "Because not every problem deserves the same hammer, sacred pattern, or architectural sermon.",
                "detail":  "detail_multiple_update_styles",
            },
            {
                "icon":    "pipeline",
                "title":   "Data Pipeline",
                "tag":     "Data, Widgets",
                "summary": "Bind widgets to pipeline keys and updates propagate automatically. Derives stay in sync across tabs with zero manual plumbing.",
                "joke":    "For when 'just update these six labels too' starts sounding less simple than it did five minutes ago.",
                "detail":  "detail_data_pipeline",
            },
            {
                "icon":    "gamepad",
                "title":   "Pygame Lifecycle Hooks",
                "tag":     "Rendering, Structure",
                "summary": "ip_think, ip_draw, and ip_draw_hud give you direct access to the game loop. Build particle systems, animations, or custom renderers without fighting the framework.",
                "joke":    "A framework that doesn't act personally offended when you want to draw something yourself.",
                "detail":  "detail_lifecycle_hooks",
            },
            {
                "icon":    "tooltip",
                "title":   "Multi-Tier Tooltips",
                "tag":     "Widgets, UX",
                "summary": "Lightweight hover tips for quick hints. Super Tooltips for pinnable, scrollable deep-dive panels with full widget content inside.",
                "joke":    "Sometimes a tooltip should whisper. Sometimes it needs to write a small novel.",
                "detail":  "detail_multi_tier_tooltips",
            },
            {
                "icon":    "registry",
                "title":   "Automatic Widget Registry",
                "tag":     "Data, Dev Tools",
                "summary": "Name a widget and it's instantly reachable from anywhere. No globals, no reference chains, no passing handles through four layers of code.",
                "joke":    "Because passing a button reference through four layers of code is not elegant. It's hostage negotiation.",
                "detail":  "detail_widget_registry",
            },
            {
                "icon":    "codebox",
                "title":   "Beautiful Code Boxes",
                "tag":     "Widgets, Rendering",
                "summary": "Pass a string or a file path and get formatted, readable source code display. Syntax-aware, scrollable, copy-ready.",
                "joke":    "Your code deserves better than being pasted into a sad little text blob.",
                "detail":  "detail_code_boxes",
            },
            {
                "icon":    "tabmap",
                "title":   "Tab Map",
                "tag":     "Dev Tools, UX",
                "summary": "A bird's-eye view of every tab and pane in your application. See the whole structure at a glance and jump anywhere.",
                "joke":    "Once your app grows past five tabs, confidence alone is no longer a navigation strategy.",
                "detail":  "detail_tab_map",
            },
            {
                "icon":    "grid",
                "title":   "PowerGrid",
                "tag":     "Widgets, Data",
                "summary": "Sortable across pages, paginated, SQL-ready. Feed it lists, dicts, or databases. Three input formats, one widget.",
                "joke":    "A fake grid with three happy-path rows is a demo, not a grid.",
                "detail":  "detail_grid",
            },
            {
                "icon":    "selfdoc",
                "title":   "Self-Documenting",
                "tag":     "Dev Tools, Structure",
                "summary": "Documentation reads the framework source code directly. Widget docs, API references, and examples that can't go stale.",
                "joke":    "Stale docs are just historical fiction with method names.",
                "detail":  "detail_documenting",
            },
            {
                "icon":    "chart",
                "title":   "Live Matplotlib Charts",
                "tag":     "Rendering, Data, Widgets",
                "summary": "Embed real-time updating charts directly in your pygame UI. Training curves, experiment monitoring, diagnostics — all live.",
                "joke":    "Sometimes the fastest way to understand your code is to make it draw its feelings.",
                "detail":  "detail_live_charts",
            },
        ]
    def detail(self, parent):
        Body(parent,"",name="IPUI Mantras")
        Title(parent, "Easy to get right - Hard to get wrong", text_align=CENTER)
