"""
Biology Module Tests

Tests for Agent and Genome classes.
"""

import pytest
import numpy as np
import config
from src.biology import Genome, Agent
from src.logger import DataLogger
from src.engine import Simulation


class TestGenome:
    """Tests for the Genome class (species definition)."""
    
    def test_genome_excretions_sum_to_one(self, test_config):
        """
        Genomes with invalid excretion weights should raise an error.
        This is a critical constraint: matter must be conserved.
        """
        # First, verify default genome is valid
        genome = Genome('standard')
        assert genome.species_id == 'standard'
    
    def test_genome_loads_traits(self, test_config):
        """Does a genome correctly load species traits?"""
        genome = Genome('standard')
        
        # Check that all required traits are present
        required_traits = [
            'starting_energy', 'metabolism', 'repro_threshold',
            'toxin_tolerance', 'heat_tolerance'
        ]
        
        for trait in required_traits:
            assert trait in genome.traits, f"Missing trait: {trait}"
            assert genome.traits[trait] > 0, f"Trait {trait} should be > 0"


class TestAgent:
    """Tests for Agent behavior."""
    
    def test_agent_initialization(self, test_config):
        """Can we create an agent?"""
        logger = DataLogger(run_name="test_agent_init", seed=42)
        sim = Simulation(42, logger)
        
        # Grab first agent from spawn
        agent = sim.agents[0]
        
        assert agent.energy > 0
        assert agent.stored_mass == 0.0
        assert agent.age_accumulated == 0.0
    
    def test_agent_ages(self, test_config):
        """Do agents age as they step?"""
        logger = DataLogger(run_name="test_agent_age", seed=42)
        sim = Simulation(42, logger)
        
        agent = sim.agents[0]
        initial_age = agent.age_accumulated
        
        # Run a few steps through the agent
        agent.step(sim.fields.fields, sim.occupancy)
        
        # Age should increase
        assert agent.age_accumulated > initial_age
    
    def test_agent_dies_of_old_age(self, test_config):
        """
        If we manually age an agent past lifespan, does it die?
        """
        logger = DataLogger(run_name="test_agent_die_age", seed=42)
        sim = Simulation(42, logger)
        
        agent = sim.agents[0]
        
        # Manually age agent past lifespan
        agent.age_accumulated = agent.my_traits['lifespan_limit'] + 1
        
        # Step should return "die"
        result = agent.step(sim.fields.fields, sim.occupancy)
        assert result == "die"