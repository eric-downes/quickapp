#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest version of test_dynamic_4_qa.py.
Tests dynamic job creation with nested context iteration defined within a dynamic function.
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
    """Define dynamic jobs in nested contexts."""
    names2 = ['m', 'n']
    for c2, name2 in iterate_context_names(context, names2):
        # assert c2.currently_executing == context.currently_executing
        c2.comp_dynamic(define_jobs2, id_name + name2)


class QuickAppDemoChild4(QuickApp):
    """Demo QuickApp that creates dynamic jobs with nested context iteration."""
    
    def define_options(self, params):
        """Define command line options."""
        pass
    
    def define_jobs_context(self, context):
        """Define dynamic jobs in the context with dynamic nested iteration."""
        names1 = ['a', 'b']
        for c1, name1 in iterate_context_names(context, names1):
            c1.comp_dynamic(define_jobs1, name1)


class TestDynamic4(QuickappTestBase):
    """Test dynamic job creation with nested context iteration in QuickApp."""

    def test_dynamic4(self):
        """Test running QuickAppDemoChild4 with dynamic nested context iteration."""
        self.run_quickapp(qapp=QuickAppDemoChild4, cmd='ls')
        self.assertJobsEqual('all', ['a-context',
                                     'b-context',
                                     'a-define_jobs1',
                                     'b-define_jobs1', ])
        self.assert_cmd_success('make *define_jobs1;ls')
        self.assertJobsEqual('all', ['a-context',
                                     'b-context',
                                     'a-define_jobs1',
                                     'b-define_jobs1',
                                     'a-m-context',
                                     'a-n-context',
                                     'b-m-context',
                                     'b-n-context',
                                     'a-m-define_jobs2',
                                     'b-m-define_jobs2',
                                     'a-n-define_jobs2',
                                     'b-n-define_jobs2', ])


        self.assert_cmd_success('details a-define_jobs1')
        self.assert_defined_by('a-define_jobs1', ['root'])

        self.assert_cmd_success('make;ls')
        self.assertJobsEqual('all', ['a-context',
                                     'b-context',
                                     'a-define_jobs1',
                                     'b-define_jobs1',
                                     'a-m-context',
                                     'a-n-context',
                                     'b-m-context',
                                     'b-n-context',
                                     'a-m-define_jobs2',
                                     'b-m-define_jobs2',
                                     'a-n-define_jobs2',
                                     'b-n-define_jobs2',
                                     'a-m-f',
                                     'a-n-f',
                                     'b-m-f',
                                     'b-n-f',
                                     ])

        self.assert_cmd_success('details a-m-define_jobs2')
        self.assert_defined_by('a-m-define_jobs2', ['root', 'a-define_jobs1'])


        self.assert_cmd_success('details a-m-f')
        self.assert_defined_by('a-m-f', ['root', 'a-define_jobs1', 'a-m-define_jobs2'])


if __name__ == "__main__":
    # Run this test file directly with pytest
    pytest.main(["-xvs", __file__])