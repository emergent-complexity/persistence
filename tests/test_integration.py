"""
Integration Tests

Full simulation runs to verify everything works together.
"""

import pytest
import os
import config
from src.logger import DataLogger
from src.engine import Simulation


class TestFullSimulation:
    """Tests that run the full simulation stack."""

    def test_basic_run_completes(self):
        """Can we run a basic simulation for the expected number of steps?"""
        logger = DataLogger(run_name="test_full_run", seed=42)
        sim = Simulation(42, logger)

        for _ in range(50):
            sim.step()

        assert sim.frame_count == 50, \
            f"Expected 50 steps, got {sim.frame_count}"

    def test_results_saved(self, temp_results_dir):
        """Can we save simulation results to disk?"""
        logger = DataLogger(run_name="test_save", seed=42)
        sim = Simulation(42, logger)

        for _ in range(50):
            sim.step()

        logger.save_to_disk()

        assert os.path.exists(logger.csv_path), "CSV not saved"
        assert os.path.exists(logger.meta_path), "Metadata not saved"
