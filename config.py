# --- SESSION & REPRODUCIBILITY ---
RANDOM_SEED = None
RUN_NAME = "Boom_and_Bust"

# --- GRID & SPATIAL PHYSICS ---
GRID_SIZE = (50, 50)

# --- FIELD PROPERTIES ---
FIELD_CONFIGS = {
    'carbon': {
        'decay': 0.01,
        'diffusion': 0.08,
        'init_value': 0.0
    },
    'waste': {
        'decay': 0.01,
        'diffusion': 0.08,
        'init_value': 0.0
    },
    'heat': {
        'decay': 0.05,
        'diffusion': 0.15,
        'init_value': 20.0
    },
    'necromass': {
        'decay': 0.001,
        'diffusion': 0.001,
        'init_value': 0.0
    }
}

# --- FIELD SOURCES ---
SOURCES = [
    {
        'field': 'carbon',
        'type': 'rain',
        'amount': 0.5
    },
    {
        'field': 'waste',
        'type': 'rain',
        'amount': 0.0
    }
]

SPECIES_CONFIGS = {

    # --- THE BLOOMER (r-strategist) ---
    # Burns hot, reproduces fast, depletes resources aggressively.
    # Will likely boom early and crash hard.
    'bloomer': {
        'intakes': {'carbon': 0.8, 'necromass': 0.1},
        'excretions': {'waste': 1.0},
        'toxins': {'waste': 0.05},          # Low waste sensitivity — doesn't care about pollution

        'max_bite': 6.0,                    # Greedy — takes more per step
        'starting_energy': 100.0,
        'metabolic_cost': 2.0,              # Burns energy fast
        'entropy_coefficient': 0.6,         # Generates more heat
        'growth_efficiency': 0.15,          # Less efficient at storing mass

        'repro_threshold': 25.0,            # Reproduces at low energy — doesn't wait
        'repro_prob': 0.30,                 # High reproduction probability
        'repro_entropy_cost': 30.0,         # Low wear from reproduction

        'entropy_tax': 1.2,                 # Ages faster
        'death_threshold_E': 0.0,
        'toxin_tolerance': 60.0,            # Tolerates pollution well
        'heat_tolerance': 50.0,
        'lifespan_limit': 350.0,            # Shorter natural lifespan

        'init_count': 40,
    },

    # --- THE BROODER (K-strategist) ---
    # Slow metabolism, waits for the right moment to reproduce.
    # Will likely be outcompeted early but outlast the bloomer.
    'brooder': {
        'intakes': {'carbon': 0.8, 'necromass': 0.1},
        'excretions': {'waste': 1.0},
        'toxins': {'waste': 0.1},           # More sensitive to waste

        'max_bite': 3.0,                    # Conservative — takes less per step
        'starting_energy': 20.0,
        'metabolic_cost': 0.8,              # Burns energy slowly
        'entropy_coefficient': 0.3,         # Generates less heat
        'growth_efficiency': 0.30,          # More efficient at storing mass

        'repro_threshold': 60.0,            # Waits until well-fed to reproduce
        'repro_prob': 0.05,                 # Low reproduction probability
        'repro_entropy_cost': 50.0,         # Higher wear from reproduction

        'entropy_tax': 0.8,                 # Ages slower
        'death_threshold_E': 0.0,
        'toxin_tolerance': 30.0,            # Less pollution tolerant
        'heat_tolerance': 40.0,             # Less heat tolerant — avoids crowded tiles
        'lifespan_limit': 500.0,            # Longer natural lifespan

        'init_count': 40,
    },
}

# --- SEEDING AGENT SETTINGS ---
SEED_STYLE = 'Grid'

# --- GLOBAL BIOLOGICAL SETTINGS ---
REPRO_COST_RATIO = 0.5
BASE_BODY_MASS = 2

# --- SIMULATION SETTINGS ---
MAX_STEPS_HEADLESS = 20000
AUDIT_INTERVAL = MAX_STEPS_HEADLESS / 10.0

# --- VISUALIZATION SETTINGS ---
VISUAL_STYLE = 'TELEMETRIC'
RENDER_INTERVAL = 100

KEY_BINDINGS = {
    '1': 'carbon',
    '2': 'waste',
    '3': 'heat',
    '4': 'necromass'
}
INITIAL_VIEW = 'carbon'

FIELD_VIZ_CONFIG = {
    'carbon':    {'cmap': 'YlGn',   'vmax': 20.0, 'label': 'Food'},
    'waste':     {'cmap': 'Purples','vmax': 20.0, 'label': 'Pollution'},
    'heat':      {'cmap': 'inferno','vmax': 50.0, 'label': 'Temperature'},
    'necromass': {'cmap': 'copper', 'vmax': 30.0, 'label': 'Detritus'}
}

SPECIES_COLORS = {
    'bloomer': '#FF4500',   # Orange Red — aggressive, hot
    'brooder': "#005EFF",   # Deep Sky Blue — calm, patient
}