# Persistence — Scenarios

Pre-configured universes to explore different ecological dynamics.
Each scenario is a complete `config.py` you can drop in and run immediately.

## How to Use

1. Pick a scenario below
2. Copy its config file into the project root and rename it `config.py`
3. Run the simulation: `python main.py`
4. Observe. Then tinker.

---

## 🧫 Self-Inhibiting Species

**File:** `self_inhibiting_species.py`

**Question:** What if a species is poisoned by its own waste?

**What you'll likely see:**
- Population grows slowly as agents near resource vents accumulate enough energy to reproduce
- A brief population boom — then toxicity catches up
- A steady-state population settles around ~60 agents

**Key insights:**
- *Ecological Cybernetics* — a negative feedback loop between metabolism and environment. The more they eat, the more they poison themselves.
- *The Metabolic Catch-22* — too far from food and they starve. Too close and they excrete themselves to death.
- *Recycle!* — a comment on what happens when waste has nowhere to go.

**Tinkering recommendations:**
- *Hardiness* — raise or lower `toxin_tolerance` or the `waste` accumulation multiplier. Watch the population swing between extinction and explosion.
- *Flushing Rate* — increase `waste` diffusion to flush toxins away faster, or reduce it to let them pool. How much pollution can a population survive?

---

## 🔄 Metabolic Mirrors

**File:** `metabolic_mirrors.py`

**Question:** I eat your waste and you eat mine. Your food is my toxin and mine is yours. Can we survive together?

**What you'll likely see:**
- The two species don't compete directly — they occupy complementary niches
- Populations stabilize through mutual dependence
- The system is fragile: a single death can trigger a cascade of local collapses as waste accumulates unchecked

**Key insights:**
- *Emergent cooperation* — neither species is programmed to help the other. Mutualism arises purely from metabolic complementarity.
- *Fragility of interdependence* — when a neighbor dies, their waste stops being cleared. The resulting toxin buildup can kill adjacent agents, spreading the collapse outward.

**Tinkering recommendations:**
- *Toxin Multipliers* — make one species slightly more or less sensitive to its own waste. Does the system compensate, or does one species collapse and take the other with it?
- *Intake Efficiency* — make one species better or worse at eating the other's waste. At what point does the mutualism break down into parasitism?

---

## 💥 Boom and Bust

**File:** `boom_and_bust.py`

**Question:** Two species. One resource. The *Bloomer* lives fast and dies young. The *Brooder* plays the long game. Who wins?

**What you'll likely see:**
- Bloomers explode early — aggressive reproduction, high resource consumption
- Brooders struggle to keep up initially
- The Bloomer's own heat and waste depletes the environment it depends on
- Whether the Brooder makes a comeback depends on the seed — run it a few times

**Key insights:**
- *Efficiency vs. Speed* — the winner isn't always the fastest. Long-term survival requires managing the environment you live in.
- *The tragedy of the commons* — a species that overexploits shared resources can destroy the conditions for its own survival.

**Tinkering recommendations:**
- *Don't tinker yet.* Let them fight it out across a few seeds first — outcomes vary significantly. Once you have an intuition for the baseline, try nudging `repro_prob` or `metabolic_cost` on the Bloomer and see how much advantage is too much.

---

## 🧪 Create Your Own

The real experiment is the one you design. Here's where to start:

- `GRID_SIZE` — larger world, more resources, more room for complexity
- `SPECIES_CONFIGS` — define metabolism, reproduction strategy, tolerances
- `SOURCES` — control how much food enters the world, and from where
- `FIELD_CONFIGS` — change how fast matter diffuses or decays

Run headless for speed: `python main.py --headless`

Share interesting runs in [Discussions](#) — what dynamics did you find?