#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest version of test_dynamic_1.py.
Tests the dynamic job creation functionality of quickapp.
"""

import pytest
from quickapp import QuickApp

from .quickappbase import QuickappTestBase


def f():
    """Simple test function that returns 1."""
    return 1


def define_jobs2(context):
    """Define a job in the context."""
    context.comp(f)


def define_jobs1(context):
    """Define a dynamic job in the context."""
    context.comp_dynamic(define_jobs2)


class QuickAppDemoChild1(QuickApp):
    """Demo QuickApp that creates dynamic jobs."""
    
    def define_options(self, params):
        """Define command line options."""
        pass
    
    def define_jobs_context(self, context):
        """Define dynamic jobs in the context."""
        context.comp_dynamic(define_jobs1)


class TestDynamic1(QuickappTestBase):
    """Test dynamic job creation in QuickApp."""
    
    def test_dynamic1(self):
        """Test running QuickAppDemoChild1 with dynamic jobs."""
        self.run_quickapp(qapp=QuickAppDemoChild1, cmd='ls')
        self.assert_cmd_success('make define_jobs1')
        self.assert_cmd_success('ls')
        
        self.assert_cmd_success('make')
        self.assert_cmd_success('make')
        self.assert_cmd_success('make')


if __name__ == "__main__":
    # Run this test file directly with pytest
    pytest.main(["-xvs", __file__])