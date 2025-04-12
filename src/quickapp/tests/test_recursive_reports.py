#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest version of test_recursive_reports.py.
Tests the recursive report functionality of quickapp.
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


def instance_reports(context):
    """Create instances of reports in multiple contexts."""
    param1s = ['a', 'b']
    param2s = [1, 2]
    for c1, param1 in iterate_context_names(context, param1s):
        c1.add_extra_report_keys(param1=param1)
        for c2, param2 in iterate_context_names(c1, param2s):
            c2.add_extra_report_keys(param2=param2)
            r = c2.comp(report_example1, param1=param1, param2=param2)
            c2.add_report(r, 'report_example1')
            r = c2.comp(report_example2, param1=param1, param2=param2)
            c2.add_report(r, 'report_example2')


class QuickAppDemoReport(QuickApp):
    """Demo QuickApp that creates reports in multiple contexts."""
    
    def define_options(self, params):
        """Define command line options."""
        pass
    
    def define_jobs_context(self, context):
        """Define jobs that create reports."""
        context.comp_dynamic(instance_reports)


class TestCompappReport(QuickappTestBase):
    """Test report generation in QuickApp."""
    
    def test_compapp1(self):
        """Test running QuickAppDemoReport with recursive reports."""
        self.run_quickapp(QuickAppDemoReport, cmd='ls') 
        self.assert_cmd_success('make recurse=1')


if __name__ == "__main__":
    # Run this test file directly with pytest
    pytest.main(["-xvs", __file__])