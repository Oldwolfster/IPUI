# Lists of shit - ToDoNF.md

## Project Summary —
### The shit this project does.

**NeuroForge** is the reason IPUI exists. Mission: do for FFNNs what VB did for Win32 —
invert the effort curve so building, training, *watching*, and understanding a neural net
is trivial for the 90% case, while the full power stays reachable. **It's for EVERYONE** —
newbs through Ng himself. The calibration persona is "Wolf, two years ago" (thinks in
functions and audit trails, would get it instantly if shown the numbers moving), but the
belief is universal: nobody needs the ∂ soup. A FFNN can get by on pure arithmetic —
a few exponents IF you want to get fancy.

**A FFNN is just a 3-step process:**
1. **Guess.** (Forward Pass)
2. **Look at how your guess pans out.** (Error Analysis Pass)
3. **Nudge so it pans out a bit better next time.** (Backward Pass)

Second-order Hessians and Jacobians are for people who don't realize that after all that
BS, you just plug in the best LR from the LR sweep — all the fancy math gets plugged.

### The Sacred Laws (official)

| Law                      | Scope                  |
|--------------------------|------------------------|
| 100% Auditable!          | ABSOLUTELY EVERYTHING  |
| 200% Deterministic!      | ABSOLUTELY EVERYTHING  |
| User Responsible for     | **ABSOLUTELY NOTHING** |
| But able to override     | ABSOLUTELY EVERYTHING  |

Two matched pairs:
- **Trust pair (1 & 2):** every number on screen can be traced (auditable) AND
  regenerated (deterministic). A run is a fact, not an anecdote. Idempotency, seeds,
  tie-outs, and the "only load-bearing numbers get screen space" display principle are
  all enforcement arms of these two laws.
- **VB pair (3 & 4):** sensible automation for everything (LR sweep, Auto ML
  Smart-Config, auto-scaling) so the user owes the machine nothing — while every single
  decision remains overridable (Your Settings outrank Base Gladiator outrank
  Smart-Config). Responsible for nothing, sovereign over everything. Either law alone
  is a toy or a chore; together they're the pit of success.

### Positioning: we don't compete with TensorFlow/PyTorch

NeuroForge is not an alternative to TensorFlow or PyTorch — it exists to make people
BETTER at them. Those are production engines; NeuroForge is where you build the mental
model that makes the engines make sense. Learn here, watch here, prototype here — then
take it to the big rigs. (The one-way export of NN configs to PyTorch is that handoff,
formalized: NeuroForge hands you off with a working net and a working understanding.)

The VB analogy holds here too: VB didn't compete with C++/Win32 — it made the same
platform accessible, and VB programmers who later graduated to the raw API arrived with
the mental model already installed. Same play: someone who has watched blame flow
through a NeuroForge net will read `loss.backward()` and know exactly what's happening
behind the curtain.

Corollary — the scope guard: feature requests get judged by "does this deepen
understanding?" never "does PyTorch have it?" When the honest answer to a capability
request is "do that in PyTorch," that's not a gap. That's the pipeline working.

**Three names, one system (official taxonomy — fluid, but current):**
- **NNA — Neural Network Arena (the engine/body):** Runs the actual training. Owns
  optimizers, loss functions, initializers, scalers, activations — all as Strategy
  objects. Training runs execute as **subprocess shards**, launched per batch, polled by
  the UI. Lives at `src.NNA.engine.*`.
- **NeuroForge (the head/brains):** The IPUI app. Design and build your model or sweep,
  launch batches, analyze results. Presents everything, decides nothing about training.
  Calls NNA for whatever the user needs.
- **NeuroScope (the visualizer):** Plays back the tape (see VCR principle below) — the
  animated network view with time-machine controls. Launched from NeuroForge, probably
  as another shard; can be manually launched from the engine side. Its code lives with
  NNA purely from inertia. Recently CSRed and strong — the weak joint is the LAUNCH
  path from NeuroForge (see Known gaps). Historically, NeuroScope's original hand-rolled
  UI is the reason IPUI was built.
- **The VCR principle (critical):** NNA has TWO jobs: (1) run the models, (2) record
  everything as it runs — like a VCR taping a show — into a SQL database. NeuroScope
  plays back that tape: it makes NO decisions, faithfully replaying every detail the
  engine produced. This is why the time machine works — scrubbing, reverse,
  jump-to-anything is tape navigation, not recomputation. It's the Sacred Laws made
  structural: the display can't lie about or alter training (auditable), and the tape
  replays identically forever (deterministic).
- **Rerun-at-detail (Law 2's dividend):** `RecordLevel.FULL` vs `SUMMARY` is taping
  fidelity — batch runs tape summaries (`nf_count`, max 2, get FULL). But ANY summary
  run can be pulled up in NeuroScope at full fidelity by simply rerunning it at a higher
  record level — same seed, identical show, better tape. Determinism converts storage
  into compute-on-demand: record everything OR keep detail forever is a false choice
  here; we get both.
- **The DB bridge:** A database transfers the latest strategy code/metadata from the engine
  to NeuroForge. The Armory's right-panel config options (Optimizer → AdaGrad/Adam/Fable/...
  menu + submenu) are populated FROM this DB, not hardcoded in the UI. New engine strategy →
  shows up in the UI. Naming IS wiring, cross-process edition.
- **Division of labor principle:** UI capability can lead engine capability. Example: the UI
  can be built ready for Dropout before the engine delivers it — "the engine delivering it is
  someone else's problem." Build the socket, plug arrives later.

**Stack: vanilla Python. Full stop.** No numpy, no pandas, no torch/tensorflow (except a
one-way export of NN configs TO pytorch). This is load-bearing, not a quirk: every number
on screen is a number our code computed in a line you can point at. You can't audit a BLAS
call. The `Leaky(-34.29) = -0.343` panel is only honest because nothing is vectorized out
of sight.


### The Mental Model (CRITICAL — differs from every textbook)

Textbook diagrams show **topology** (circles and lines, a static structural claim).
NeuroForge shows **execution**. Same left-to-right silhouette so textbook intuition
transfers for free, but the model underneath is inverted:

1. **A neuron is a function.** It has inputs, it does shit with them, it has an output.
   Not a dimensionless dot — an audit panel showing incoming weight bars, the raw sum,
   and the literal arithmetic (`Leaky(-34.29) = -0.343`). A debugger, not a diagram.
2. **A neuron OWNS its incoming weight vector.** Textbooks put weights on the edges,
   teaching the wrong data model. In the code (and on screen), weights live inside the
   receiving neuron. Matches reality: `neuron.optimizer_state['m'][weight_id]`.
3. **The lines/arrows are OUTPUTS (activations) traveling** from one neuron's output to
   the next neuron's input. One number per line. The connection is the dumbest thing in
   the system — a wire. All intelligence lives inside the box.
4. **It's a time machine, not a snapshot.** Every moment of training is scrubbable:
   play/pause/reverse, step, jump-to-sample, jump-to-epoch. Forward AND backward stories
   are rendered (blame arrows flow right-to-left through the loss and back).

### Blame, not the chain rule

The chain rule is BANNED here — well, not quite: the blame method's math is IDENTICAL to
the chain rule. But blame is the algorithm; the chain rule is merely the proof that the
local arithmetic is legal. Textbooks teach the proof as if it were the algorithm. That's
why grad students cry and become plumbers.

**The pie:** blame is a pie (like Thanksgiving, except made of blame). Everyone gets a
slice. The receivers rarely accept it all:

- Blame **originates** at the output: error → loss function → **Loss Gradient**
  (NOT to be confused with the loss VALUE, which backprop ignores — see below).
- Each neuron computes **Accepted Blame = incoming blame × Act Gradient**
  (Act Gradient = σ′(raw sum) = how much Raw Sum contributes to final prediction =
  how much blame this neuron accepts).
- Weight adjustments are doled out proportional to who fed you what; the rest of the
  pie is passed upstream.
- Entirely local arithmetic. Every column of it is displayed in the output neuron's
  Super Tooltip (Forward Pass table | Backward Pass table).
- Bonus: "receivers rarely accept it all" IS the vanishing gradient problem in plain
  English. Sigmoid's Act Gradient maxes at 0.25 — a picky eater; the pie shrinks every
  handoff. ReLU accepts its whole slice (Act Gradient 1.0 in its live region) — which
  is exactly why deep nets became trainable.

### The loss value is a SPECTATOR (hill we die on)

**Backprop never reads the loss value. Not once.** The gradient of the loss kicks off
blame; the scalar loss number participates in zero weight updates. Therefore:

- The loss VALUE is never displayed at the forward→backward turnaround point. Displaying
  it there would teach a lie by placement. The Error History chart is the honest
  monitorable quantity.
- **Half Wit Loss** is the falsification experiment shipped as a menu item: its loss
  function returns `-55_555_555.404` unconditionally (`.404` = loss not found); its
  derivative is `(prediction - target)`. It trains fine. Pick it, watch error descend
  while "loss" sits at negative fifty-five million forever. The lie dies of empirical
  causes.
- Display principle (contrapositive of auditing): **only load-bearing numbers get
  screen space.** Every displayed value either flows forward, flows backward, or ties
  out to one that does.

### The war on MSE (and loss-name inversion)

- The names describe the spectator; the gradients — the only part that acts — behave
  like the OTHER name:
  - **MSE** ("squared!") gradient = `2·error` — perfectly **linear** blame.
  - **MAE** ("absolute", sounds proportional) gradient = `sign(error)` = **±1** —
    size of error has NO impact on the update. A flat tax with amnesia.
- MSE-on-classification is worse than wrong: through sigmoid, its gradient carries σ′,
  which vanishes exactly when the net is confidently wrong. It punishes confusion and
  forgives arrogance. BCE-through-sigmoid cancels the σ′ and collapses to clean
  `prediction − target` — loudest precisely when sure-but-wrong.
- The decorative `½` in `½(y−ŷ)²` exists solely so the derivative typesets prettily.
  A constant chosen for the proof's aesthetics, not the machine's behavior. Exhibit A
  for "deliberate obfuscation."
- Huber has the right idea (proportional near target, capped for outliers) — note it's
  a GRADIENT spec that had to be reverse-engineered into a loss shape to fit the
  official vocabulary.

### Auditing: EVERYTHING must be visible, and the numbers must TIE OUT

Second law of the motto. Examples of the standard:
- Output neuron header shows Epoch Avg of blame (e.g. 0.491); toggle to sample view and
  it reconciles to the sample's blame (0.519). No number on screen is allowed to be
  unexplainable from another number on screen.
- Super Tooltips (pinnable, scrollable) show the EXACT code that runs (e.g. Adam's
  `adam_popup_info` / `adam_calculate_adjustment`) — and sneak the Pin button under the
  hover point (Fitts's Law as a weapon).


### Vocabulary (the gladiator metaphor is structural, not decorative)

| Term          | Meaning                                                                     |
|---------------|------------------------------------------------------------------------------|
| **Gladiator** | A model/config that fights. e.g. AutoForge.                                  |
| **Arena**     | A dataset/problem (XOR, Titanic8, SingleInput_CreditScore...). BaseArena subclass; `generate_training_data()` returns (data, field labels, outcome labels). |
| **Match**     | Gladiators duking it out side-by-side in IDENTICAL environments (same seed). |
| **Armory**    | Tab: equip the match — gladiators, arenas, seeds, hyperparam/config lists.   |
| **Forge**     | Tab: the model workbench (info / workbench / preview).                       |
| **Colosseum** | Hidden tab, revealed on launch: live fight status, runs, analysis. Polls shards. |
| **Blame**     | What textbooks call the gradient flowing backward. See pie.                  |
| **Fable**     | Our custom optimizer. Dusted RAdam on early Titanic8 tests. Uses `avg_leverage` where Adam uses the gradient. Details: ask Wolf. |
| **TRI**       | **TrainingRunInfo** — training-run context object passed to strategies (`TRI.timestep`, `TRI.hyper.optimizer_beta1`, ...). |
| **MoonPhase** | Optimizer that genuinely incorporates the phase of the moon — wrapped inside one of the best optimizers, so it outperforms most of the list and blows the doors off SGD. A shipped lesson in optimizer attribution: the wrapper does the work, the moon gets the credit. |
| **LR Sweep**  | Nobody sets learning rates here (2.5 years and counting). Every run auto-sweeps LR by decades (1e-06 → 1e+03, then probes further down if the bottom edge wins), scores a short probe per LR, tracks a No-Improve counter, picks the winner. `lr_specified: False` is the norm. Motto: "Because setting learning rate manually stinks." (v3 "crater walk" now live: start at 1.0, descend by decades, 3 literal rises in a row = past the dip; ties are no-info.) |
| **NNA**       | Neural Network Arena — the engine. See taxonomy above.                        |
| **NeuroScope**| The tape-playback visualizer. See taxonomy above.                             |
| **ArenaSettings** | `arenasettings.py` — where all configuration lived for 3 years before IPUI. `HyperParameters` still imports from it. The ancestral config home. |

**Why side-by-side matches exist (origin):** testing a modification (e.g. change
`delta = input*error` to `delta = error`) requires two models in IDENTICAL environments —
same seed, same samples, same everything except the one change. **IDEMPOTENCY is a core
tenet.** One run = one reproducible fact.


### App structure & flow (FormNeuroForge)

- Whole app declared in `TAB_LAYOUT` dict: Home, Dashboard, Lab, Armory, Forge,
  Colosseum (hidden), Pro, Export, Log.
- **Pro tab composes panes from other tabs** via dotted names
  (`"Armory.match_settings"`, `"Forge.workbench"`) — cross-tab pane reuse.
- **Settings come from 3 places, in priority order:**
  1. Your Settings (what the user touched)
  2. Base Gladiator
  3. Auto ML Smart-Config (for anything not specified above)
- **Launch button shows the cost of your choices live:** `calc_total_runs` takes the
  Cartesian product across every config list with >1 entry (gladiators × arenas × seeds
  × optimizer list × ... ). "Launch (36 runs)" — you know what you asked for BEFORE you
  commit.
- **Launch flow:** `write_launch_config` (GUID) → `launch_prepare_batch` (batch_id) →
  reveal Colosseum → `launch_shards` (subprocesses) → UI polls shards.
- Strategies self-register: `__all__` scans globals for `StrategyLossFunction` instances.
  Drop a file in, it appears in the picker. C(1) per strategy.


### History (why it is the way it is)

- ~18 months living with the single perceptron (Progressive Anchoring: one anchor driven
  until it burns). First arena: SingleInput_CreditScore — synthetic credit scores where
  score = repayment probability. Running it was a slot machine (85... 75... 77...) until
  the law of large numbers ruined the fun.
- XOR was the burn: MLP debugging was impossible to keep straight in your head → hence
  render EVERYTHING. And the first convergence triggered "wait... this can't be right...
  it doesn't have the loss" → hence the loss-is-a-spectator doctrine.
- Encountering standard presentations (Ng's course) after building the correct mechanical
  model produced consistent confusion — the lectures describe the justification, not the
  machine. NeuroForge exists so the next Wolf doesn't lose two years to that.
- **NeuroScope predates IPUI** — its hand-rolled UI was the reason IPUI got built.
  Verdict after the fact: 4 months building a UI framework beat what was hand-rolled for
  NeuroScope. For ~3 years, everything now done in IPUI was done in `arenasettings.py`.


### Known gaps / current state markers

- **The fragile part is the BRIDGE, not the components.** NNA and NeuroScope are both
  recently CSRed and strong. What needs work: launching NeuroScope FROM NeuroForge/IPUI,
  and the batch → analyze-in-IPUI → rerun-at-detail → NeuroScope flow around it. The only
  way to harden the bridge is hands-on use: run real experiments end-to-end and see
  where the friction lives.
- **Pre/post data pipelines** are on the horizon (data prep before the arena, results
  analysis after the run). Baseball's RAW → ETL → FOREST → PREDICT pipeline is the
  working prototype for these patterns.

- **No Dropout yet** — UI socket can be built ahead of engine delivery.
- **Fable** needs formalizing. Score so far: Fable 3, field 0. Note on the RAdam Titanic8
  comparison: LR=1.0 was sweep-selected AND vindicated — RAdam's curve is a roller coaster
  (flat ~0.5 for ~13 epochs, then a plunge to ~0.37). The early "flatline" verdict came
  from a 5-epoch run that ended before the plunge. Lesson (cuts both ways): probe horizon
  and run horizon must agree, or one of them lies. Fable still wins — converges by ~epoch 8
  and lands lower (0.143 vs 0.366 epoch avg err; 90.91% vs 81.82% accuracy).
- `updateDEKETENE` in FormNeuroForge — typo'd DELETEME; it's the Colosseum shard-polling
  hook. Confirm live-with-typo vs dead-with-purpose before touching.
- MoonPhase and Coverless Adam exist in the optimizer list. Yes, really. Ask Wolf.
- Project files uploaded to Claude lag the local working copy — verify before asserting
  file contents.


1) Add hold out vs test cycle.
2) Add drop out with arena demonstrating