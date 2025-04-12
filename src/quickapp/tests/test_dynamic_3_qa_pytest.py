#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest version of test_dynamic_3_qa.py.
Tests multi-level nested dynamic job creation with context iteration.
"""

import pytest
from quickapp import QuickApp, iterate_context_names

from .pytest_base import QuickappTestBase


def f(name):
    """Simple test function that returns its input."""
    print(name)
    return name


def define_jobs2(context, id_name):
    """Define a job in the given context with the given id_name."""
    context.comp(f, id_name)


def define_jobs1(context, id_name):
    """Define a dynamic job in the given context with the given id_name."""
    context.comp_dynamic(define_jobs2, id_name)


class QuickAppDemoChild3(QuickApp):
    """Demo QuickApp that creates multi-level nested dynamic jobs in multiple contexts."""
    
    def define_options(self, params):
        """Define command line options."""
        pass
    
    def define_jobs_context(self, context):
        """Define dynamic jobs in multiple nested contexts."""
        names1 = ['a', 'b']
        names2 = ['m', 'n']
        for c1, name1 in iterate_context_names(context, names1):
            for c2, name2 in iterate_context_names(c1, names2):
                c2.comp_dynamic(define_jobs1, name1 + name2)


class TestDynamic3(QuickappTestBase):
    """Test multi-level nested dynamic job creation in QuickApp."""

    def test_dynamic1(self):
        """Test running QuickAppDemoChild3 with nested dynamic jobs."""
        self.run_quickapp(qapp=QuickAppDemoChild3, cmd='ls')
        
        self.assert_cmd_success('check_consistency')

        self.assertJobsEqual('all', ['a-m-context',
                                     'a-n-context',
                                     'b-m-context',
                                     'b-n-context',
                                     'a-m-define_jobs1',
                                     'b-m-define_jobs1',
                                     'a-n-define_jobs1',
                                     'b-n-define_jobs1'])
        self.assert_cmd_success('make *-define_jobs1')

        self.assert_cmd_success('ls')
        self.assertJobsEqual('all', ['a-m-context',
                                     'a-n-context',
                                     'b-m-context',
                                     'b-n-context',
                                     'a-m-define_jobs1',
                                     'b-m-define_jobs1',
                                     'a-n-define_jobs1',
                                     'b-n-define_jobs1',
                                     'b-m-context-0',
                                     'a-n-context-0',
                                     'a-m-context-0',
                                     'b-n-context-0',
                                     'a-m-define_jobs2',
                                     'b-m-define_jobs2',
                                     'a-n-define_jobs2',
                                     'b-n-define_jobs2',
                                     ])
        self.assert_cmd_success('make;ls')
        self.assertJobsEqual('all', ['a-m-context',
                                     'a-n-context',
                                     'b-m-context',
                                     'b-n-context',
                                     'a-m-define_jobs1',
                                     'b-m-define_jobs1',
                                     'a-n-define_jobs1',
                                     'b-n-define_jobs1',
                                     'b-m-context-0',
                                     'a-n-context-0',
                                     'a-m-context-0',
                                     'b-n-context-0',
                                     'a-m-define_jobs2',
                                     'b-m-define_jobs2',
                                     'a-n-define_jobs2',
                                     'b-n-define_jobs2',
                                     'a-m-f',
                                     'a-n-f',
                                     'b-m-f',
                                     'b-n-f',
                                     ])
        self.assert_cmd_success('details a-m-f')
        self.assert_defined_by('a-m-f', ['root', 'a-m-define_jobs1', 'a-m-define_jobs2'])


if __name__ == "__main__":
    # Run this test file directly with pytest
    pytest.main(["-xvs", __file__])