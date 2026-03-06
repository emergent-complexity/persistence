# --- SESSION & REPRODUCIBILITY ---
RANDOM_SEED = None            # None for stochastic runs (every run is uniquely stored in run logs)
RUN_NAME = "Baseline"         # Default label for the Results folder

# --- GRID & SPATIAL PHYSICS ---
GRID_SIZE = (50, 50)          # Dimensions of the Universe 

# --- FIELD PROPERTIES ---    # Initialize different fields of matter/energy that can exist

FIELD_CONFIGS = {
    'carbon': {               # Field Name
        'decay': 0.01,        # Decay Rate of the Field (matter/energy leaves the universe)
        'diffusion': 0.08,    # Diffusion Rate of the Field (matter/energy spreads)
        'init_value': 0.0     # Initial value of the Field at Genesis
    },
    'waste': {
        'decay': 0.01,    
        'diffusion': 0.08,   
        'init_value': 0.0
    },
    'heat': {                 # Represents entropy increase (COMPULSORY FIELD)
        'decay': 0.05,        # Thermal radiation (Heat escaping to space)
        'diffusion': 0.15,    # Energy spreads faster than matter
        'init_value': 20.0    # "Room temperature" baseline
    },
    'necromass': {	      # Dead organic matter (COMPULSORY FIELD)  			
        'decay': 0.001,       
        'diffusion': 0.001,   
        'init_value': 0.0
    }
}

# --- FIELD SOURCES ---       # Initialize Sources of Matter/Energy

SOURCES = [

    # Random vents of a field
    {   
        'field': 'carbon',    # Specify the field type of the source
        'type': 'vent',       # Specify the kind of source (This is a 'Vent')
        'amount': 3.0,
        'count': 20,
        'range': (5.0, 10.0)  # Optional: varied strengths
        
    },
    
    # Example of a "Toxic Leak" you could add:
    # { 'field': 'waste', 'type': 'vent', 'pos': (10, 10), 'amount': 1.0 }

    
    # Standard global rain

    {
        'field': 'carbon',
        'type': 'rain',
        'amount': 0.08
    },
    {
        'field': 'waste',
        'type': 'rain',
        'amount': 0.08
    }
    
]
SPECIES_CONFIGS = {
    'standard': {                    # Species Names
        
        # 1. --- MATTER INTERACTIONS ---
        # Substrates and efficiencies of energy extraction
        'intakes': {'carbon': 0.8, 'necromass': 0.1}, 
        # Distribution secretions (MUST SUM TO 1.0)
        'excretions': {'waste': 1.0},
        # Toxins and bio-accumulation multipliers
        'toxins': {'waste': 0.1}, 

        # 2. --- METABOLISM PARAMETERS ---
        'max_bite': 4.0,             # Max units of matter taken from tile per time step
        'starting_energy': 20.0,     # Units of Energy an agent starts with at Genesis
        'metabolic_cost': 1.0,       # Energy burned & heat released per step
        'entropy_coefficient': 0.5,  # Heat produced per unit of energy gained
        'growth_efficiency': 0.2,    # Percentage of intake mass stored
        
        # 3. --- REPRODUCTION PARAMETERS ---
        'repro_threshold': 40.0,     # Energy required to consider splitting
        'repro_prob': 0.10,          # Probability of reproduction if Mass and 
                                     # Energy requirements are met
        'repro_entropy_cost': 40.0,  # Wear and tear from birth

        # 4. --- AGING (ENTROPY TAX) ---
        'entropy_tax': 1.0,          # Age gain per step
            
        # 5. --- DEATH PARAMETERS  ---
        'death_threshold_E': 0.0,    # Minumum energy threshold
        'toxin_tolerance': 40.0,     # Bio accumulation limit
        'heat_tolerance': 40.0,      # Ambient heat limit
        'lifespan_limit': 400.0,     # Age (Entropy Limit)

        # 6. --- POPULATION PARAMETERS ---
        'init_count': 40,            # Initial Population of Species
        
    },
}

# --- SEEDING AGENT SETTINGS ---
SEED_STYLE = 'Grid'                  # Seeds agents of a species randomly or in a grid
# --- GLOBAL BIOLOGICAL SETTINGS --
REPRO_COST_RATIO = 0.5               # Parent gives 50% of internal energy to child
BASE_BODY_MASS = 2                   # Mass of an agent (Universal for now)

# --- SIMULATION SETTINGS ---
MAX_STEPS_HEADLESS = 20000                # Limit for --headless runs
AUDIT_INTERVAL = MAX_STEPS_HEADLESS/10.0  # Interval for thermodynamics audit


# --- VISUALIZATION SETTINGS ---
VISUAL_STYLE = 'TELEMETRIC'          # Two aesthetic available: TELEMETRIC/SCIENTIFIC              
RENDER_INTERVAL = 100                # How often to render frame ('Timelapse' Renders)

KEY_BINDINGS = {                     # Change view to different fields during Live Sim
    'y': 'carbon',
    'x': 'waste',
    'c': 'heat',
    'v': 'necromass'
}
INITIAL_VIEW = 'carbon'              # Which field to start with during Live Sim
# Visual parameters for each field
FIELD_VIZ_CONFIG = {
    'carbon': {'cmap': 'YlGn', 'vmax': 20.0, 'label': 'Food'},
    'waste':  {'cmap': 'Purples', 'vmax': 20.0, 'label': 'Pollution'},
    'heat':   {'cmap': 'inferno', 'vmax': 50.0, 'label': 'Temperature'},
    'necromass': {'cmap': 'copper', 'vmax': 30.0, 'label': 'Detritus'}
}
SPECIES_COLORS = {
    'standard': '#00BFFF',   # Deep Sky Blue (Standard Biota)
    'mutant':   '#FFD700',   # Gold (Slow Burners/Mutants)
    #'scavenger':'#FF4500'    # Orange Red (Future species)
}

