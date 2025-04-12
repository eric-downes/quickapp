#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest version of test_dynamic_2_qa.py.
Tests nested dynamic job creation with context iteration.
"""

import pytest
from quickapp import QuickApp, iterate_context_names

from .quickappbase import QuickappTestBase


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
    """Demo QuickApp that creates nested dynamic jobs in multiple contexts."""
    
    def define_options(self, params):
        """Define command line options."""
        pass
    
    def define_jobs_context(self, context):
        """Define dynamic jobs in multiple contexts."""
        names = ['a', 'b']
        for c, id_name in iterate_context_names(context, names):
            c.comp_dynamic(define_jobs1, id_name)


class TestDynamic2(QuickappTestBase):
    """Test nested dynamic job creation in QuickApp."""
    
    def test_dynamic1(self):
        """Test running QuickAppDemoChild3 with nested dynamic jobs."""
        self.run_quickapp(qapp=QuickAppDemoChild3, cmd='ls')
        print('ls 1')
        self.assert_cmd_success('ls not *dynrep*')
        self.assertJobsEqual('all', ['a-context',
                                    'b-context',
                                    'a-define_jobs1',
                                    'b-define_jobs1'])
        print('make root') 
        self.assert_cmd_success('make a-define_jobs1 b-define_jobs1')
        print('ls 2')
        self.assert_cmd_success('ls not *dynrep*')
        
        self.assertJobsEqual('all', ['a-context',
                                    'b-context',
                                    'a-define_jobs1',
                                    'b-define_jobs1',
                                    'a-context-0',
                                    'b-context-0',
                                    'a-define_jobs2',
                                    'b-define_jobs2',
                                    ])
        print('make level1')
        self.assert_cmd_success('make level1 level2')
        print('ls 3')
        self.assert_cmd_success('ls not *dynrep*')

        self.assertJobsEqual('all', ['a-context',
                                    'b-context',
                                    'a-define_jobs1',
                                    'b-define_jobs1',
                                    'a-context-0',
                                    'b-context-0',
                                    'a-define_jobs2',
                                    'b-define_jobs2',
                                    'a-f',
                                    'b-f'
                                    ])
        self.assert_cmd_success('details a-f')


if __name__ == "__main__":
    # Run this test file directly with pytest
    pytest.main(["-xvs", __file__])