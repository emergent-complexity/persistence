# Persistence vAlpha - The Entropy Audit
# Copyright (C) 2026  emergent-complexity
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.

import os
import sys
import time
import config
import numpy as np

from src.logger import DataLogger
from src.biology import Agent, Genome
from src.environment import FieldManager,SourceController
class Simulation:
    def __init__(self, seed, logger, run_name=None):
        
        # --- Random Seeding ---
        self.active_seed = seed    
        np.random.seed(self.active_seed)
        
        # --- Initialize Infrastructure ---
        #self.logger = DataLogger(run_name=run_name, seed=self.active_seed) 
        self.logger = logger
        self.shape = config.GRID_SIZE
        self.fields = FieldManager(self.shape)
        self.sources = SourceController(self.shape)
        self.agents = []
        self.occupancy = np.zeros(self.shape, dtype=bool)
        self.frame_count = 0
        
        # --- LEDGERS ---
        self.mass_sourced = 0.0
        self.mass_decayed = 0.0
        self.heat_radiated = 0.0
        self.total_energy_generated = 0.0
        
        self.initial_env_mass = self._get_current_env_mass()
        
        # Stats
        #self.deaths = {"starve": 0, "toxic": 0, "senility": 0, "heat": 0}
        self.deaths = {
            sid: {"starve": 0, "toxic": 0, "senility": 0, "heat": 0} 
            for sid in config.SPECIES_CONFIGS.keys()
        }

        #for species_id in config.SPECIES_CONFIGS.keys():
        #    self._seed_species(species_id)
        self._seed_all_species()
        
        self.initial_bio_mass = self._get_current_bio_mass()
        self.initial_heat = np.sum(self.fields.fields['heat'])
        self.initial_agent_energy = sum(a.energy for a in self.agents)

    def _get_current_env_mass(self):
        return sum(np.sum(f) for name, f in self.fields.fields.items() if name != 'heat')

    def _get_current_bio_mass(self):
        return sum(config.BASE_BODY_MASS + a.stored_mass + a.internal_toxins for a in self.agents)

    def _seed_all_species(self):
        """
        Seeds species in local 'clusters' across the grid to ensure 
        each species has identical access to local resource patches.
        """
        species_keys = list(config.SPECIES_CONFIGS.keys())
        # We'll use the count of the first species to define the number of 'Twin Sites'
        # Assuming for a baseline they have the same init_count
        site_count = config.SPECIES_CONFIGS[species_keys[0]]['init_count']
        
        if config.SEED_STYLE == 'Grid':
            # 1. Calculate the number of 'Spawn Sites'
            cols = int(np.ceil(np.sqrt(site_count * (self.shape[1] / self.shape[0]))))
            rows = int(np.ceil(site_count / cols))
            x_space = self.shape[1] / cols
            y_space = self.shape[0] / rows

            # 2. Iterate through sites
            for idx in range(site_count):
                r_idx = idx // cols
                c_idx = idx % cols
                
                # Base coordinate for the 'Twin Site'
                base_r = int((r_idx * y_space) + (y_space / 2)) % self.shape[0]
                base_c = int((c_idx * x_space) + (x_space / 2)) % self.shape[1]
                
                # 3. Place one of EACH species at this site (in immediate neighborhood)
                # Offset list: [Center, East, South, West, North...]
                offsets = [(0,0), (0,1), (1,0), (0,-1), (-1,0)]
                
                for s_idx, species_id in enumerate(species_keys):
                    dr, dc = offsets[s_idx % len(offsets)]
                    r = (base_r + dr) % self.shape[0]
                    c = (base_c + dc) % self.shape[1]
                    
                    # Safety check for overlap
                    if not self.occupancy[r, c]:
                        spec_genome = Genome(species_id)
                        self.agents.append(Agent((r, c), spec_genome, self))
                        self.occupancy[r, c] = True
        else:
            # Random fallback
            for sid in species_keys:
                self._seed_species_random(sid)

    def _handle_death(self, agent):
        r, c = agent.pos
        sid = agent.genome.species_id

        # Necroburst
        self.fields.fields['heat'][r, c] += agent.energy
        total_burst_mass = config.BASE_BODY_MASS + agent.stored_mass + agent.internal_toxins
        share = total_burst_mass / 9.0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = (r + dr) % self.shape[0], (c + dc) % self.shape[1]
                self.fields.fields['necromass'][nr, nc] += share
        
        # Log cause specifically for THIS species
        if agent.age_accumulated >= agent.my_traits['lifespan_limit']: 
            self.deaths[sid]["senility"] += 1
        elif agent.energy <= agent.my_traits['death_E']: 
            self.deaths[sid]["starve"] += 1
        elif self.fields.fields['heat'][r, c] > agent.my_traits['heat_tolerance']: 
            self.deaths[sid]["heat"] += 1
        else: 
            self.deaths[sid]["toxic"] += 1

    def step(self):
        self.frame_count += 1
        self.fields.update(sim=self)
        self.sources.apply(self.fields.fields, sim=self)

        next_agents = []
        new_occupancy = np.zeros(self.shape, dtype=bool)
        np.random.shuffle(self.agents)

        for agent in self.agents:
            action = agent.step(self.fields.fields, self.occupancy)
            
            if action == "die":
                self._handle_death(agent)
                continue 
            
            if action == "reproduce":
                if self._attempt_repro(agent, next_agents, new_occupancy):
                    pass # Success handled in method
                else:
                    agent.stored_mass += config.BASE_BODY_MASS # Refund

            next_agents.append(agent)
            new_occupancy[agent.pos] = True

        self.agents = next_agents
        self.occupancy = new_occupancy
        self._log_metrics()

    def _attempt_repro(self, agent, next_agents, new_occupancy):
        r, c = agent.pos
        neighbors = [
            (dr, dc) for dr in [-1, 0, 1] for dc in [-1, 0, 1] 
            if not (dr == 0 and dc == 0) # Can't spawn on yourself
        ]
        np.random.shuffle(neighbors)
        for dr, dc in neighbors:
            nr, nc = (r + dr) % self.shape[0], (c + dc) % self.shape[1]
            if not self.occupancy[nr, nc] and not new_occupancy[nr, nc]:
                e_half = agent.energy * 0.5
                agent.energy -= e_half
                agent.age_accumulated += agent.my_traits.get('repro_entropy_cost', 40.0)
                child = Agent((nr, nc), agent.genome, self, energy=e_half, parent_traits=agent.my_traits)
                next_agents.append(child)
                new_occupancy[nr, nc] = True
                return True
        return False

    def check_mass_integrity(self):
        """Verifies if (Initial + In) == (Current + Out) with  dusting for floatpoint drift"""
        current_env = self._get_current_env_mass()
        current_bio = self._get_current_bio_mass()
        
        total_start = self.initial_env_mass + self.initial_bio_mass + self.mass_sourced
        total_end = current_env + current_bio + self.mass_decayed
        
        mass_error = total_start - total_end
        
        # --- THE SAFETY VALVE ---
        DUST_THRESHOLD = 1e-5
        
        if abs(mass_error) < DUST_THRESHOLD and mass_error != 0:
            # Small drift? Dust it into Necromass at the center of the grid
            r, c = self.shape[0] // 2, self.shape[1] // 2
            # Subtracting the error from the field effectively reconciles the ledger
            self.fields.fields['necromass'][r, c] += mass_error 
            
            # Re-calculate for the printout
            current_env = self._get_current_env_mass()
            mass_error = total_start - (current_env + current_bio + self.mass_decayed)
            dusting_status = " (Dusting Applied 🧹)"
        else:
            dusting_status = ""

        status = "✅" if abs(mass_error) < 1e-8 else "❌"
        
        # ALARM: If the error was too big to dust, print a warning
        if status == "❌":
            print(f"🚨 ALERT: SIGNIFICANT MASS LEAK DETECTED!")
        
        print(f"--- ⚖️ MASS AUDIT [Step {self.frame_count}] ---")
        print(f"Status: {status} | Error: {mass_error:.10f} units{dusting_status}")
        
        return mass_error

    def check_energy_integrity(self):
        current_agent_energy = sum(a.energy for a in self.agents)
        current_env_heat = np.sum(self.fields.fields['heat'])
        
        # Energy produced by agents + starting energy
        total_in = self.initial_agent_energy + self.initial_heat+self.total_energy_generated
        # Energy currently in bodies + energy currently in the heat field + radiated loss
        total_out = current_agent_energy + current_env_heat + self.heat_radiated
        
        energy_error = total_in - total_out
        print(f"--- ⚡ ENERGY AUDIT [Step {self.frame_count}] ---")
        print(f"Status: {'✅' if abs(energy_error) < 1e-4 else '❌'} | Error: {energy_error:.4f}")

        return energy_error
        
    def save_audit_report(self, mass_error, energy_error):
        """Saves a detailed thermodynamic report to the run folder."""
        report_path = os.path.join(self.logger.run_dir, "physics_audit.txt")
        
        # Calculate current states for the report
        cur_env_mass = self._get_current_env_mass()
        cur_bio_mass = self._get_current_bio_mass()
        cur_heat = np.sum(self.fields.fields['heat'])
        cur_agent_e = sum(a.energy for a in self.agents)

        with open(report_path, "a") as f:
            f.write(f"--- ⚖️ PHYSICS AUDIT [Step {self.frame_count}] ---\n")
            
            # MASS SECTION
            f.write(f"  [MASS]\n")
            f.write(f"    Error:     {mass_error:.12f}\n")
            f.write(f"    Breakdown: Env: {cur_env_mass:.4f} | Bio: {cur_bio_mass:.4f}\n")
            f.write(f"    Flow:      Sourced: {self.mass_sourced:.4f} | Decayed: {self.mass_decayed:.4f}\n")
            
            # ENERGY SECTION
            f.write(f"  [ENERGY]\n")
            f.write(f"    Error:     {energy_error:.12f}\n")
            f.write(f"    Breakdown: Heat Field: {cur_heat:.4f} | Bio Energy: {cur_agent_e:.4f}\n")
            f.write(f"    Flow:      Generated: {self.total_energy_generated:.4f} | Radiated: {self.heat_radiated:.4f}\n")
            
            f.write("-" * 40 + "\n")

    def _log_metrics(self):
        # 1. Population Counts
        species_stats = {}
        for sid in config.SPECIES_CONFIGS.keys():
            # Filter agents once per species for efficiency
            s_agents = [a for a in self.agents if a.genome.species_id == sid]
            count = len(s_agents)

            species_stats[f"pop_{sid}"] = count
            
            # Averages
            if count > 0:
                species_stats[f"{sid}_avg_energy"] = np.mean([a.energy for a in s_agents])
                species_stats[f"{sid}_avg_stored_mass"] = np.mean([a.stored_mass for a in s_agents])
                species_stats[f"{sid}_avg_age"] = np.mean([a.age_accumulated for a in s_agents])
            else:
                species_stats[f"{sid}_avg_energy"] = 0
                species_stats[f"{sid}_avg_stored_mass"] = 0
                species_stats[f"{sid}_avg_age"] = 0
            
            # 2. Add per-species death metrics to the log
            for cause, count in self.deaths[sid].items():
                species_stats[f"{sid}_{cause}"] = count

        # 3. Aggregate Global Log Data
        log_data = {
            "step": self.frame_count,
            "total_population": len(self.agents),
            "avg_age": np.mean([a.age_accumulated for a in self.agents]) if self.agents else 0
        }
        
        # Merge species-specific data into the main log
        log_data.update(species_stats)
        self.logger.log_step(log_data)

    @classmethod
    def from_history(cls, run_folder):
        """Reconstructs a simulation instance from a past run's metadata."""
        import json
        meta_path = os.path.join(run_folder, "metadata.json")
        
        with open(meta_path, 'r') as f:
            meta = json.load(f)
            
        # 1. Temporarily set the global seed BEFORE creating the instance
        # This ensures any random calls inside __init__ match the history
        active_seed = meta['seed']
        np.random.seed(active_seed)
        
        # 2. Create instance (This will run __init__ and _seed_species)
        sim = cls(run_name=f"Replay_{meta['run_id']}")
        
        # 3. Explicitly ensure the instance seed matches
        sim.active_seed = active_seed
        
        # NOTE: We no longer need to manually reset agents and re-call _seed_species
        # because the __init__ call above already did it using the freshly set seed.
            
        print(f"--- Replay Initialized from Seed: {sim.active_seed} ---")
        return sim
    
    # ... (Include check_mass_integrity, check_energy_integrity, save_audit_report here) ...