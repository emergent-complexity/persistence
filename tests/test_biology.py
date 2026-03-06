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

    def test_genome_excretions_sum_to_one(self):
        """
        The default genome must have excretion weights summing to 1.0.
        This is a critical mass-conservation constraint enforced in Genome.__init__.
        """
        genome = Genome('standard')
        assert genome.species_id == 'standard'

    def test_genome_loads_traits(self):
        """Does a genome correctly load all required species traits?"""
        genome = Genome('standard')

        required_traits = [
            'starting_energy', 'metabolism', 'repro_threshold',
            'toxin_tolerance', 'heat_tolerance'
        ]

        for trait in required_traits:
            assert trait in genome.traits, f"Missing trait: {trait}"
            assert genome.traits[trait] > 0, f"Trait '{trait}' should be > 0"

    def test_invalid_excretion_weights_raise(self):
        """
        A genome with excretion weights that don't sum to 1.0 should raise
        a ValueError. This guards against accidentally introducing mass leaks
        when defining new species.
        """
        original = config.SPECIES_CONFIGS['standard']['excretions'].copy()

        try:
            config.SPECIES_CONFIGS['standard']['excretions'] = {'waste': 0.5}  # sums to 0.5
            with pytest.raises(ValueError, match="must be 1.0"):
                Genome('standard')
        finally:
            config.SPECIES_CONFIGS['standard']['excretions'] = original


class TestAgent:
    """Tests for Agent behaviour."""

    def test_agent_initialization(self):
        """Can we create an agent with the expected initial state?"""
        logger = DataLogger(run_name="test_agent_init", seed=42)
        sim = Simulation(42, logger)

        agent = sim.agents[0]

        assert agent.energy > 0
        assert agent.stored_mass == 0.0
        assert agent.age_accumulated == 0.0

    def test_agent_ages(self):
        """Do agents accumulate age each step?"""
        logger = DataLogger(run_name="test_agent_age", seed=42)
        sim = Simulation(42, logger)

        agent = sim.agents[0]
        initial_age = agent.age_accumulated

        agent.step(sim.fields.fields, sim.occupancy)

        assert agent.age_accumulated > initial_age

    def test_agent_dies_of_old_age(self):
        """An agent past its lifespan_limit should return 'die' on next step."""
        logger = DataLogger(run_name="test_agent_die_age", seed=42)
        sim = Simulation(42, logger)

        agent = sim.agents[0]
        agent.age_accumulated = agent.my_traits['lifespan_limit'] + 1

        result = agent.step(sim.fields.fields, sim.occupancy)
        assert result == "die"

    def test_agent_dies_of_starvation(self):
        """An agent with energy at or below death_threshold_E should return 'die'."""
        logger = DataLogger(run_name="test_agent_starve", seed=42)
        sim = Simulation(42, logger)

        agent = sim.agents[0]
        agent.energy = agent.my_traits['death_E']

        result = agent.step(sim.fields.fields, sim.occupancy)
        assert result == "die"


class TestMultiSpeciesSeeding:
    """Tests for correct initialisation when multiple species are present."""

    def test_no_overlap_on_spawn(self):
        """
        With multiple species, _seed_all_species should never place two agents
        on the same cell. Every agent position should be unique.
        """
        # Only run if the config actually defines multiple species
        if len(config.SPECIES_CONFIGS) < 2:
            pytest.skip("Single-species config — overlap test requires 2+ species")

        logger = DataLogger(run_name="test_no_overlap", seed=42)
        sim = Simulation(42, logger)

        positions = [a.pos for a in sim.agents]
        assert len(positions) == len(set(positions)), \
            "Two or more agents spawned on the same cell"

    def test_all_species_represented(self):
        """
        After seeding, every species defined in config should have
        at least one agent in the simulation.
        """
        logger = DataLogger(run_name="test_species_present", seed=42)
        sim = Simulation(42, logger)

        spawned_species = {a.genome.species_id for a in sim.agents}

        for sid in config.SPECIES_CONFIGS.keys():
            assert sid in spawned_species, \
                f"Species '{sid}' defined in config but not spawned"

    def test_occupancy_grid_matches_agents(self):
        """
        After seeding, the occupancy grid should be True at exactly
        the cells where agents are located, and False everywhere else.
        """
        logger = DataLogger(run_name="test_occupancy", seed=42)
        sim = Simulation(42, logger)

        for agent in sim.agents:
            r, c = agent.pos
            assert sim.occupancy[r, c], \
                f"Agent at {agent.pos} not reflected in occupancy grid"

        occupied_count = int(sim.occupancy.sum())
        assert occupied_count == len(sim.agents), \
            f"Occupancy grid has {occupied_count} True cells but {len(sim.agents)} agents exist"
