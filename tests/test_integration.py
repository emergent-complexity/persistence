"""
Integration Tests

Full simulation runs to verify everything works together.
"""

import pytest
import config
from src.logger import DataLogger
from src.engine import Simulation


class TestFullSimulation:
    """Tests that run the full simulation stack."""
    
    def test_basic_run_completes(self, test_config):
        """Can we run a basic simulation and save results?"""
        logger = DataLogger(run_name="test_full_run", seed=42)
        sim = Simulation(42, logger)
        
        # Run simulation
        for _ in range(50):
            sim.step()
        
        # Should not crash
        assert True
    
    def test_results_saved(self, test_config, temp_results_dir):
        """Can we save and reload simulation results?"""
        from src.logger import FileSystemManager
        
        logger = DataLogger(run_name="test_save", seed=42)
        sim = Simulation(42, logger)
        
        for _ in range(50):
            sim.step()
        
        # Save to disk
        logger.save_to_disk()
        
        # Check that files were created
        import os
        assert os.path.exists(logger.csv_path), "CSV not saved"
        assert os.path.exists(logger.meta_path), "Metadata not saved"