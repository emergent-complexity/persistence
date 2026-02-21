"""
Shared fixtures and configuration for tests.
Pytest automatically discovers and loads this file.
"""

import pytest
import sys
import os
import numpy as np
import tempfile
import shutil

# Add parent directory to path so we can import the main modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config


@pytest.fixture(autouse=True)
def test_config():
    """
    Automatically reset config before each test.
    'autouse=True' means this runs for EVERY test without needing to request it.
    
    This creates a safe test environment where we use a smaller grid and fewer steps.
    """
    # Store original values
    original_grid = config.GRID_SIZE
    original_steps = config.MAX_STEPS_HEADLESS
    original_audit_interval = config.AUDIT_INTERVAL
    
    # Use test values (small and fast)
    config.GRID_SIZE = (20, 20)
    config.MAX_STEPS_HEADLESS = 100
    config.AUDIT_INTERVAL = 50  # Run audits less frequently in tests
    
    yield  # Run the test with these config values
    
    # Restore originals after test completes
    config.GRID_SIZE = original_grid
    config.MAX_STEPS_HEADLESS = original_steps
    config.AUDIT_INTERVAL = original_audit_interval


@pytest.fixture
def temp_results_dir():
    """
    Create a temporary directory for test results.
    Cleaned up after test completes.
    """
    temp_dir = tempfile.mkdtemp(prefix="persistence_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)