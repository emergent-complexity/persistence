# Persistence vAlpha - The Entropy Audit
# Copyright (C) 2026  emergent-complexity
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.

import numpy as np
from scipy.signal import convolve2d
import config

class FieldManager:
    def __init__(self, shape):
        self.shape = shape
        self.fields = {}
        self.kernels = {}
        
        # Initialize fields and their unique kernels based on config
        for name, specs in config.FIELD_CONFIGS.items():
            # Use float64 for thermodynamic precision
            self.fields[name] = np.full(shape, specs['init_value'], dtype=np.float64)
            self.kernels[name] = self._build_kernel(specs['diffusion'])

    def _build_kernel(self, rate):
        """Builds a 3x3 diffusion kernel that conserves mass."""
        diag = rate / 2
        center = 1.0 - (4 * rate) - (4 * diag)
        return np.array([
            [diag, rate,   diag],
            [rate, center, rate],
            [diag, rate,   diag]
        ])

    def update(self, sim):
        """Processes the physics of the world: Diffusion and Decay."""
        for name in self.fields:
            # 1. DIFFUSION
            self.fields[name] = convolve2d(
                self.fields[name], 
                self.kernels[name], 
                mode='same', 
                boundary='wrap'
            )
            
            # 2. DECAY / RADIATION
            decay_rate = config.FIELD_CONFIGS[name].get('decay', 0.0)
            if decay_rate > 0:
                pre_decay_sum = np.sum(self.fields[name])
                self.fields[name] *= (1 - decay_rate)
                loss = pre_decay_sum - np.sum(self.fields[name])
                
                if name == 'heat':
                    sim.heat_radiated += loss
                else:
                    sim.mass_decayed += loss
            
            # 3. FLOORING (The Ledger Guard)
            # If any negative values exist (precision errors), they must be accounted for
            neg_mask = self.fields[name] < 0
            if np.any(neg_mask):
                # Calculate the "phantom mass/energy" about to be floored to zero
                phantom_loss = -np.sum(self.fields[name][neg_mask])
                
                if name == 'heat':
                    sim.heat_radiated += phantom_loss
                else:
                    sim.mass_decayed += phantom_loss
                
                self.fields[name][neg_mask] = 0.0

class SourceController:
    def __init__(self, shape):
        self.shape = shape
        self.active_sources = []
        self._initialize_procedural_sources()

    def _initialize_procedural_sources(self):
        """Resolves config sources into fixed or global injection points."""
        for entry in config.SOURCES:
            field = entry['field']
            stype = entry['type']
            
            if stype == 'rain':
                self.active_sources.append(entry)
                
            elif stype == 'vent':
                count = entry.get('count', 1)
                for _ in range(count):
                    # Fixed position or random jitter
                    if count == 1 and 'pos' in entry:
                        pos = entry['pos']
                    else:
                        pos = (np.random.randint(0, self.shape[0]), 
                               np.random.randint(0, self.shape[1]))
                    
                    amount = entry['amount']
                    if 'range' in entry:
                        amount = np.random.uniform(*entry['range'])
                        
                    self.active_sources.append({
                        'field': field,
                        'type': 'vent',
                        'pos': pos,
                        'amount': amount
                    })

    def apply(self, fields_dict, sim):
        """Injects new mass/energy into the system and logs to ledger."""
        for src in self.active_sources:
            field_name = src['field']
            if field_name not in fields_dict:
                continue
            
            amount_to_add = 0.0
            
            if src['type'] == 'rain':
                # Rain adds amount to EVERY cell
                added = src['amount'] * self.shape[0] * self.shape[1]
                fields_dict[field_name] += src['amount']
                amount_to_add = added
                
            elif src['type'] == 'vent':
                r, c = src['pos']
                if 0 <= r < self.shape[0] and 0 <= c < self.shape[1]:
                    fields_dict[field_name][r, c] += src['amount']
                    amount_to_add = src['amount']
            
            # Update the ledger (exclude heat from mass sourcing)
            if field_name != 'heat':
                sim.mass_sourced += amount_to_add
            else:
                # If you decide to track heat sourcing later
                pass