#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest version of test_recursive_reports2.py.
Tests more complex recursive report functionality with deeply nested contexts.
"""

import pytest
from quickapp import QuickApp, iterate_context_names
from reprep import Report

from .quickappbase import QuickappTestBase


def report_example1(param1, param2):
    """Create an example report with the given parameters."""
    r = Report()
    r.text('type', 'This is one report')
    r.text('param1', f'{param1}')
    r.text('param2', f'{param2}')
    return r


def report_example2(param1, param2):
    """Create another example report with the given parameters."""
    r = Report()
    r.text('type', 'This is another report')
    r.text('param1', f'{param1}')
    r.text('param2', f'{param2}')
    return r


def instance_reports1(context):
    """Create the first level of report contexts."""
    param1s = ['a', 'b']
    for c1, param1 in iterate_context_names(context, param1s, key='param1'):
        c1.comp_dynamic(instance_reports2, param1=param1)


def instance_reports2(context, param1):
    """Create the second level of report contexts."""
    param2s = [1, 2]
    for c2, param2 in iterate_context_names(context, param2s, key='param2'):
        c2.comp_dynamic(instance_reports3, param1=param1, param2=param2)   
     

def instance_reports3(context, param1, param2):
    """Create the third level of report contexts."""
    context.comp(dummy)

    r = context.comp(report_example2, param1=param1, param2=param2)
    context.add_report(r, 'report_example2')

    context.comp_dynamic(instance_reports4, param1=param1, param2=param2)
    

def instance_reports4(context, param1, param2):
    """Create the fourth level of report contexts."""
    r = context.comp(report_example1, param1=param1, param2=param2)
    context.add_report(r, 'report_example1')


def dummy():
    """A dummy function that does nothing."""
    pass


class QuickAppDemoReport2(QuickApp):
    """Demo QuickApp that creates deeply nested report contexts."""
    
    def define_options(self, params):
        """Define command line options."""
        pass
    
    def define_jobs_context(self, context):
        """Define jobs that create reports in nested contexts."""
        context.comp_dynamic(instance_reports1)


class TestCompappReport2(QuickappTestBase):
    """Test deeply nested report generation in QuickApp."""
    
    def test_compapp1(self):
        """Test running QuickAppDemoReport2 with recursive reports."""
        self.run_quickapp(QuickAppDemoReport2, cmd='make recurse=1')


if __name__ == "__main__":
    # Run this test file directly with pytest
    pytest.main(["-xvs", __file__])