"""
Physics Validation Tests

These tests verify that mass and energy are conserved in the simulation.
This is the core validation for a thermodynamic simulation.
"""

import pytest
import numpy as np
import config
from src.logger import DataLogger
from src.engine import Simulation


class TestMassConservation:
    """Tests that mass is conserved (Input + Initial = Output + Current)."""
    
    def test_mass_conservation_short_run(self):
        """
        Can we run 50 steps without mass conservation breaking?
        This is a SMOKE TEST - does the system stay stable?
        """
        logger = DataLogger(run_name="test_mass_50steps", seed=42)
        sim = Simulation(42, logger)
        
        # Run 50 steps
        for _ in range(50):
            sim.step()
        
        # Check mass balance
        mass_error = sim.check_mass_integrity()
        
        # For short runs, error should be very small
        # (allow for floating point drift)
        assert abs(mass_error) < 0.01, f"Mass error too large: {mass_error}"
    
    def test_mass_conservation_longer_run(self):
        """
        Can we run 200 steps without mass conservation breaking?
        This catches accumulated rounding errors.
        """
        logger = DataLogger(run_name="test_mass_200steps", seed=123)
        sim = Simulation(123, logger)
        
        for _ in range(200):
            sim.step()
        
        mass_error = sim.check_mass_integrity()
        
        # Longer runs will have slightly larger error
        assert abs(mass_error) < 1.0, f"Mass error accumulated: {mass_error}"
    
    def test_mass_conservation_until_extinction(self):
        """
        Run the simulation until all agents naturally die from starvation.
        This tests mass conservation through a complete lifecycle.
        
        Key insight: We don't artificially kill agents. We let the system
        run naturally. When agents die, _handle_death() converts their
        biomass to necromass fields, properly tracking it in the ledger.
        """
        logger = DataLogger(run_name="test_extinction_mass", seed=999)
        sim = Simulation(999, logger)
        
        # Run until extinction or max steps
        max_steps = 500
        for step in range(max_steps):
            sim.step()
            
            # If all agents dead, we're done
            if not sim.agents:
                print(f"All agents extinct at step {step}")
                break
        
        # After natural extinction, mass should be conserved
        mass_error = sim.check_mass_integrity()
        
        assert abs(mass_error) < 1.0, \
            f"Mass not conserved after extinction. Error: {mass_error}\n" \
            f"Initial bio mass: {sim.initial_bio_mass}\n" \
            f"Sourced: {sim.mass_sourced}, Decayed: {sim.mass_decayed}"


class TestEnergyConservation:
    """Tests that energy is conserved (heat + agent energy is accounted for)."""
    
    def test_energy_conservation_short_run(self):
        """
        Does energy balance at end of 50 steps?
        Energy = agent internal energy + heat in the field
        """
        logger = DataLogger(run_name="test_energy_50steps", seed=42)
        sim = Simulation(42, logger)
        
        for _ in range(50):
            sim.step()
        
        energy_error = sim.check_energy_integrity()
        
        # Energy accounting should be very tight
        assert abs(energy_error) < 1.0, f"Energy error: {energy_error}"
    
    def test_energy_conservation_longer_run(self):
        """
        Does energy stay balanced over 200 steps?
        """
        logger = DataLogger(run_name="test_energy_200steps", seed=123)
        sim = Simulation(123, logger)
        
        for _ in range(200):
            sim.step()
        
        energy_error = sim.check_energy_integrity()
        
        assert abs(energy_error) < 5.0, f"Energy drift: {energy_error}"


class TestSimulationStability:
    """Tests that the simulation can run without crashing."""
    
    def test_can_initialize(self):
        """Can we create a simulation without errors?"""
        logger = DataLogger(run_name="test_init", seed=42)
        sim = Simulation(42, logger)
        
        assert len(sim.agents) > 0, "No agents spawned"
        assert len(sim.fields.fields) > 0, "No fields created"
    
    def test_can_run_to_extinction(self):
        """Can we run until all agents die?"""
        logger = DataLogger(run_name="test_extinction", seed=42)
        sim = Simulation(42, logger)
        
        max_steps = 1000
        for step in range(max_steps):
            sim.step()
            
            # Stop if all agents dead
            if not sim.agents:
                break
        
        # Should NOT crash
        assert True, "Simulation crashed"
    
    def test_physics_audits_complete(self):
        """Do physics audits run without error?"""
        logger = DataLogger(run_name="test_audits", seed=42)
        sim = Simulation(42, logger)
        
        for _ in range(50):
            sim.step()
        
        # These should not raise exceptions
        mass_error = sim.check_mass_integrity()
        energy_error = sim.check_energy_integrity()
        
        # Both should return floats
        assert isinstance(mass_error, (float, np.floating))
        assert isinstance(energy_error, (float, np.floating))