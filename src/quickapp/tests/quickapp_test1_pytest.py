#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest version of quickapp_test1.py.
Note: This test is commented out in the original.
"""

import sys
import pytest
from quickapp import QuickApp
from reprep import Report


def actual_computation(param1, param2, iteration):
    """Compute something based on parameters and iteration."""
    pass


def report(param2, jobs):  # @UnusedVariable
    """Create a report based on param2 and jobs."""
    r = Report()
    return r


class QuickAppDemo1(QuickApp):
    """Demo QuickApp that demonstrates job groups and report manager usage."""
    
    def define_options(self, params):
        """Define command line options."""
        params.add_int('param1', help='First parameter', default=1)
        params.add_int_list('param2', help='Second parameter')
        
    def define_jobs_context(self, context):
        """Define jobs with parameter combinations."""
        options = self.get_options()
        
        jobs = self.comp_comb(actual_computation,
                              param1=options.param1,
                              param2=options.param2,
                              iteration=QuickApp.choice(range(4)))
        
        rm = self.get_report_manager()
        for param2, samples in jobs.groups_by_field_value('param2'):
            rj = self.comp(report, param2, samples)
            rm.add(rj, 'report', param2=param2)


@pytest.mark.skip(reason="Test is commented out in original")
def test_quickapp_demo1():
    """Test running QuickAppDemo1 with parameters."""
    args = ['-o', 'quickapp_test1',
            '-c', 'make all', '--param1', '10', '--param2', '1,2,3']
    result = QuickAppDemo1().main(args)
    assert result == 0


if __name__ == "__main__":
    sys.exit(QuickAppDemo1().main())