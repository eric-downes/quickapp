#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest version of test_child_context.py.
Tests the child context functionality of quickapp.
"""

import pytest
from compmake.jobs import all_jobs
from quickapp import (CompmakeContext, QuickApp, quickapp_main,
                      iterate_context_names)

from .quickappbase import QuickappTestBase


def f(name):
    """Simple test function that returns its input."""
    print(name)
    return name


def define_jobs(context, id_name):
    """Define a job in the given context with the given id_name."""
    assert isinstance(context, CompmakeContext)
    context.comp(f, id_name)


class QuickAppDemoChild(QuickApp):
    """Demo QuickApp that creates child contexts."""
    
    def define_options(self, params):
        """Define command line options."""
        pass
    
    def define_jobs_context(self, context):
        """Define jobs in child contexts."""
        names = ['a', 'b', 'c']
        for c, id_name in iterate_context_names(context, names):
            define_jobs(c, id_name)


class TestCompappDynamic(QuickappTestBase):
    """Test dynamic job creation in child contexts."""
    
    def test_compapp1(self):
        """Test running QuickAppDemoChild with the make command."""
        args = f'--contracts -o {self.root0} -c make --compress'
        ret_found = quickapp_main(QuickAppDemoChild, args.split(), sys_exit=False)
        assert ret_found == 0
        print(f'jobs in {self.db}: {list(all_jobs(self.db))}')
        self.assertJobsEqual('all', ['a-f', 'b-f', 'c-f'])


class QuickAppDemoChild2(QuickApp):
    """Demo QuickApp that uses comp_dynamic in child contexts."""
    
    def define_options(self, params):
        """Define command line options."""
        pass
    
    def define_jobs_context(self, context):
        """Define dynamic jobs in child contexts."""
        names = ['a', 'b', 'c']
        for c, id_name in iterate_context_names(context, names):
            c.comp_dynamic(define_jobs, id_name)


class TestCompappDynamic2(QuickappTestBase):
    """Test dynamic job creation with comp_dynamic in child contexts."""
    
    def test_compapp1(self):
        """Test running QuickAppDemoChild2 with the ls command."""
        self.run_quickapp(qapp=QuickAppDemoChild2, cmd='ls')
        
        # These are the jobs currently defined
        self.assertJobsEqual('all', ['a-define_jobs',
                                     'b-define_jobs',
                                     'c-define_jobs',
                                     'a-context',
                                     'b-context',
                                     'c-context'])
        
        self.assert_cmd_success_script('make *-define_jobs; ls')
        
        self.assertJobsEqual('all', ['a-define_jobs',
                                     'b-define_jobs',
                                     'c-define_jobs',
                                     'a-context',
                                     'b-context',
                                     'c-context',
                                     'a-f', 'b-f', 'c-f'])
        
        self.assertJobsEqual('done', ['a-define_jobs',
                                      'b-define_jobs',
                                      'c-define_jobs',
                                      'a-context',
                                      'b-context',
                                      'c-context'])
        
        self.assert_cmd_success_script('make; ls')
        
        self.assertJobsEqual('done', ['a-define_jobs',
                                      'b-define_jobs',
                                      'c-define_jobs',
                                      'a-context',
                                      'b-context',
                                      'c-context',
                                      'a-f', 'b-f', 'c-f'])


if __name__ == "__main__":
    # Run this test file directly with pytest
    pytest.main(["-xvs", __file__])