"""
Environment Module Tests

Tests for field physics (diffusion, decay) and sources.
"""

import pytest
import numpy as np
import config
from src.environment import FieldManager, SourceController
from src.logger import DataLogger
from src.engine import Simulation


class TestFieldManager:
    """Tests for field creation and physics."""
    
    def test_fields_initialized(self, test_config):
        """Are all fields from config initialized?"""
        fm = FieldManager(config.GRID_SIZE)
        
        # Should have all fields from config
        for field_name in config.FIELD_CONFIGS.keys():
            assert field_name in fm.fields, f"Missing field: {field_name}"
    
    def test_diffusion_kernel_valid(self, test_config):
        """Does the diffusion kernel preserve mass?"""
        fm = FieldManager(config.GRID_SIZE)
        
        for field_name, kernel in fm.kernels.items():
            # Kernel should sum to 1.0 (mass-conserving)
            kernel_sum = np.sum(kernel)
            assert np.isclose(kernel_sum, 1.0, atol=1e-6), \
                f"Kernel for {field_name} sums to {kernel_sum}, not 1.0"


class TestSourceController:
    """Tests for environmental sources (vents, rain)."""
    
    def test_sources_initialized(self, test_config):
        """Are sources from config initialized?"""
        sc = SourceController(config.GRID_SIZE)
        
        # Should have some sources active
        assert len(sc.active_sources) > 0, "No sources created"