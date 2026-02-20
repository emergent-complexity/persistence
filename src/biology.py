# Persistence vAlpha - The Entropy Audit
# Copyright (C) 2026  emergent-complexity
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.

import numpy as np
import random
import config

class Genome:
    def __init__(self, species_id):
        self.species_id = species_id
        spec = config.SPECIES_CONFIGS[species_id]
        
        # Mapping dictionaries
        self.intakes = spec.get('intakes', {})           # {field: efficiency}
        self.excretions = spec.get('excretions', {})     # {field: weight}
        self.toxin_sens = spec.get('toxins', {})         # {field: multiplier}

        # Ensure mass conservation on excretion
        weight_sum = sum(self.excretions.values())
        if not np.isclose(weight_sum, 1.0):
            raise ValueError(f"Species {species_id} leak! Excretion weights sum to {weight_sum}, must be 1.0")
        
        # General Traits
        self.traits = {
            'starting_energy': spec['starting_energy'],
            'growth_efficiency': spec['growth_efficiency'],
            'metabolism': spec['metabolic_cost'],
            'max_bite': spec.get('max_bite', 1.0),
            'toxin_tolerance': spec.get('toxin_tolerance', 20.0),
            'heat_tolerance': spec.get('heat_tolerance', 100.0),
            'entropy_coeff': spec.get('entropy_coefficient', 0.5),
            'repro_threshold': spec['repro_threshold'],
            'repro_prob': spec['repro_prob'],
            'death_E': spec['death_threshold_E'],
            'entropy_tax': spec.get('entropy_tax', 1.0),
            'lifespan_limit': spec.get('lifespan_limit', 400.0)
        }

class Agent:
    def __init__(self, pos, genome, sim, energy=None, parent_traits=None):
        self.pos = pos
        self.genome = genome
        self.sim = sim # Reference to access fields
        
        # 1. INITIALIZE ENERGY & TOXINS
        self.energy = energy if energy is not None else self.genome.traits['starting_energy']
        self.stored_mass = 0.0
        self.internal_toxins = 0.0
        self.age_accumulated = 0.0 

        # 2. INHERITANCE
        self.my_traits = parent_traits.copy() if parent_traits else self.genome.traits.copy()
        
    def step(self, fields_dict, occupancy_grid):
        r, c = self.pos
        t = self.my_traits
        
        # --- PHASE 1: SENILITY ---
        self.age_accumulated += t['entropy_tax']
        if self.age_accumulated >= t['lifespan_limit']:
            return "die"

        # --- PHASE 2: INTAKE & SELECTIVE PROCESSING ---
        interact_fields = list(set(list(self.genome.intakes.keys()) + 
                                   list(self.genome.toxin_sens.keys()) + 
                                   list(self.genome.excretions.keys())))
        
        total_matter_on_tile = sum(fields_dict[f][r, c] for f in interact_fields)
        harvest_ratio = min(1.0, t['max_bite'] / max(1e-6, total_matter_on_tile))
        
        intake_mass_processable = 0.0
        energy_gain = 0.0
        
        for f in interact_fields:
            before = fields_dict[f][r, c]
            grabbed = before * harvest_ratio
            fields_dict[f][r, c] -= grabbed
            
            # 1. Handle Toxins (Internalized)
            toxin_part = 0.0
            if f in self.genome.toxin_sens:
                toxin_part = grabbed * self.genome.toxin_sens[f]
                self.internal_toxins += toxin_part
            
            remaining_mass = grabbed - toxin_part
            
            # 2. Handle Processable vs. Inert
            if f in self.genome.intakes:
                # This stays in the agent for the "Growth/Waste" phase
                intake_mass_processable += remaining_mass
                energy_gain += remaining_mass * self.genome.intakes[f]
            else:
                # REJECTION: Put it back immediately. No transformation.
                fields_dict[f][r, c] += remaining_mass

        # --- PHASE 3: THERMODYNAMICS ---
        maintenance_cost = t['metabolism']
        conversion_heat = energy_gain * t['entropy_coeff']
        
        # 1. Internal Energy Change
        # Net change to agent is gain minus what was spent to stay alive
        self.energy += (energy_gain - maintenance_cost)
        
        # 2. External Heat Change
        # The world gets the maintenance cost plus the tax of conversion
        fields_dict['heat'][r, c] += (conversion_heat + maintenance_cost)

        # 3. THE AUDIT LOG (The Fix)
        # Total energy entering the universe this step is the 
        # metabolic gain PLUS the heat byproduct generated.
        self.sim.total_energy_generated += (energy_gain + conversion_heat)

        # --- PHASE 4: GROWTH AND EXCRETION (MASS ONLY) ---
        # Matter is NEVER destroyed here. It is either stored or excreted.
        
        # 1. Structural Growth: Structural mass comes from processable intake.
        growth_ratio = t.get('growth_efficiency', 0.1) 
        kept_mass = intake_mass_processable * growth_ratio
        self.stored_mass += kept_mass

        # 2. Excretion: Everything not kept goes back to the fields.

        metabolic_waste = intake_mass_processable - kept_mass
        for f, weight in self.genome.excretions.items():
            fields_dict[f][r, c] += metabolic_waste * weight

        # --- PHASE 5: SURVIVAL FILTERS ---
        if self.energy <= t['death_E']: return "die"
        if self.internal_toxins > t['toxin_tolerance']: return "die"
        if fields_dict['heat'][r, c] > t['heat_tolerance']: return "die"
        
        # --- PHASE 6: REPRODUCTION (MASS TRANSFER) ---
        # Only here does structural mass leave the parent.
        if self.energy >= t['repro_threshold'] and self.stored_mass >= config.BASE_BODY_MASS:
            if random.random() < t['repro_prob']:
                self.stored_mass -= config.BASE_BODY_MASS
                return "reproduce"
                
        return "stay"