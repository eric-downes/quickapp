#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest version of test_reportmanager_1.py.
Tests the report manager functionality of quickapp.
"""

import pytest
from quickapp import QuickApp, iterate_context_names
from reprep import Report

from .pytest_base import QuickappTestBase


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


class QuickAppDemoReport(QuickApp):
    """Demo QuickApp that creates and manages reports with different parameters."""
    
    def define_options(self, params):
        """Define command line options."""
        pass
    
    def define_jobs_context(self, context):
        """Define jobs that create reports with different parameters."""
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


class TestReportManager(QuickappTestBase):
    """Test the report manager functionality in QuickApp."""
    
    def test_report_manager(self):
        """Test running QuickAppDemoReport with report generation."""
        self.run_quickapp(QuickAppDemoReport, cmd='ls')
        print('---- now make')
        self.assert_cmd_success('make')
        print('---- result of first make')
        self.assert_cmd_success('ls')
        print('---- result of remake')
        self.assert_cmd_success('ls')
        self.assert_cmd_success('make')
        self.assert_cmd_success('ls')
        # self.assert_cmd_success('make')


if __name__ == "__main__":
    # Run this test file directly with pytest
    pytest.main(["-xvs", __file__])