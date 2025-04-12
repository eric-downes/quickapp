#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest version of subcontexts_test.py.
Tests the minimal_names functionality in app_utils.
"""

import pytest
from quickapp.app_utils.minimal_name import minimal_names_at_boundaries, minimal_names


class TestMinimal:
    """Test the minimal_names functionality."""

    def test_minimal_names_at_boundaries(self):
        """Test minimal_names_at_boundaries returns correct prefix, minimal names, and postfix."""
        objects = ['test_random_dpx1_64_10', 'test_random_drob1_64_10']
        
        prefix, minimal, postfix = minimal_names_at_boundaries(objects)
        
        assert prefix == 'test_random_'
        assert postfix == '_64_10'
        
        assert minimal == ['dpx1', 'drob1']


    def test_minimal_names(self):
        """Test minimal_names returns correct prefix, minimal names, and postfix."""
        objects = ['test_random_dpx1_64_10', 'test_random_drob1_64_10']
        
        prefix, minimal, postfix = minimal_names(objects)
        
        assert prefix == 'test_random_d'
        assert postfix == '1_64_10'
        
        assert minimal == ['px', 'rob']


if __name__ == "__main__":
    # Run this test file directly with pytest
    pytest.main(["-xvs", __file__])