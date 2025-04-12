#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest version of quickapp_test2.py.
Tests error handling and return codes in quickapp.
"""

import os
import pytest
from shutil import rmtree
from tempfile import mkdtemp

from quickapp import (QuickApp, QUICKAPP_USER_ERROR, QUICKAPP_COMPUTATION_ERROR,
                     quickapp_main)
from reprep import Report

from .pytest_base import QuickappTestBase


def actual_computation(param1, param2):
    """Compute something based on parameters."""
    print(f'computing ({param1} {param2})')
    return [1, 2, 3, 4]


def report_example(param2, samples):
    """Create a report with samples or raise an exception based on param2."""
    print(f'report_example({param2}, {samples})')
    if param2 == -1:
        print('generating exception')
        raise Exception('fake exception')
    r = Report()
    r.text('samples', str(samples))
    print('creating report')
    return r


class QuickAppDemo2(QuickApp):
    """Demo QuickApp that tests error handling."""
    cmd = 'quick-app-demo'

    def define_options(self, params):
        """Define command line options."""
        params.add_int('param1', help='First parameter', default=1)
        params.add_int('param2', help='Second parameter')

    def define_jobs_context(self, context):
        """Define jobs that may raise errors based on parameters."""
        options = self.get_options()
        param1 = options.param1
        param2 = options.param2
        samples = context.comp(actual_computation, param1=param1, param2=param2)

        rj = context.comp(report_example, param2, samples)
        context.add_report(rj, 'report_example')


class TestQuickAppErrors(QuickappTestBase):
    """Test error handling in QuickApp."""
    
    def test_return_codes(self):
        """Test that quickapp returns the expected error codes in various situations."""
        cases = []

        def add(args, ret):
            cases.append(dict(args=args, ret=ret))

        # Successful case
        add('--compress --contracts -c clean;make --param1 10 --param2 1', 0)

        # Parse error
        add('--compress --contracts -c clean;make  --param1 10 --parm2 1 ',
            QUICKAPP_USER_ERROR)

        # Computation exception
        add('--compress --contracts  -c clean;make  --param1 10 --param2 -1 ',
            QUICKAPP_COMPUTATION_ERROR)

        for c in cases:
            args = c['args']

            if isinstance(args, str):
                args = args.split()
            tmpdir = mkdtemp()
            args = ['-o', tmpdir] + args
            ret = c['ret']
            with open(os.path.join(tmpdir, '.compmake.rc'), 'w') as f:
                f.write('config echo 1\n')
            ret_found = quickapp_main(QuickAppDemo2, args, sys_exit=False)
            msg = f'Expected {ret}, got {ret_found}.\nArguments: {c["args"]}'
            assert ret == ret_found, msg
            rmtree(tmpdir)


if __name__ == "__main__":
    # Run this test file directly with pytest
    pytest.main(["-xvs", __file__])