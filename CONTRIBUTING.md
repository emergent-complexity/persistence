# Contributing to Persistence

First of all - thank you for being here. Whether you're filing a bug, designing a new species, or improving the docs, you're contributing to a shared exploration of what life is and how it persists.

This document explains how to get set up and what kinds of contributions are welcome.

---

## What kinds of contributions are welcome?

**All of the following:**

- 🐛 Bug reports and fixes
- 🧫 New scenarios (`scenarios/` configs with a good question behind them)
- 📖 Documentation improvements - clearer explanations, better examples
- 🔬 New tests, especially physics conservation edge cases
- 💡 Ideas and proposals - open a Discussion, no code required
- 🎨 Visualisation improvements
- ⚙️ Performance improvements for large grids or long runs

If you're unsure whether your idea fits, open a Discussion first and ask. There are no bad questions.

---

## Setting up for development

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/<your-username>/persistence.git
cd persistence

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify everything works
pytest tests/ -v
```

All tests should pass before you start making changes.

---

## Making a contribution

```bash
# 1. Create a branch for your work
git checkout -b your-branch-name

# 2. Make your changes

# 3. Run the tests to make sure nothing is broken
pytest tests/ -v

# 4. Commit and push
git add .
git commit -m "Short description of what you changed"
git push origin your-branch-name

# 5. Open a Pull Request on GitHub
```

There's no strict branch naming convention yet - just keep it descriptive (e.g. `fix-mass-leak`, `scenario-predator-prey`, `improve-readme`).

---

## Adding a scenario

Scenarios are the most accessible contribution and a great place to start. A good scenario has:

- A clear **question** it's trying to answer
- A config that reliably produces interesting dynamics
- A short write-up for `scenarios/README.md` covering what to expect and what to tinker with

Copy an existing scenario file as a starting point, design your species and fields, run it a few times to make sure the dynamics are interesting, then open a PR with both the config file and the README addition.

---

## A note on the physics

*Persistence* is built around strict mass and energy conservation. If you modify `biology.py` or `environment.py`, please run the full test suite - especially `test_physics_conservation.py` - and make sure all audits pass. A contribution that introduces a mass or energy leak will not be merged, no matter how interesting the dynamics.

---

## Questions?

Open a [Discussion](../../discussions) - that's what it's there for.
