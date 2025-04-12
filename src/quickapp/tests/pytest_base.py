#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest-compatible base class for QuickApp tests, replacing the nose-based QuickappTest.
This file adapts CompmakeTest to work with pytest fixtures instead of unittest's setUp/tearDown.
"""

import os
import pytest
from shutil import rmtree
from tempfile import mkdtemp

from compmake import set_compmake_config, logger
from compmake.context import Context
from compmake.exceptions import CommandFailed, MakeFailed
from compmake.jobs import get_job, parse_job_list
from compmake.jobs.storage import all_jobs
from compmake.scripts.master import compmake_main
from compmake.storage import StorageFilesystem
from compmake.structures import Job
from quickapp import quickapp_main
from contracts import contract


class CompmakeTestBase:
    """
    Base class for compmake tests, adapted for pytest.
    This replaces the unittest.TestCase-based CompmakeTest with pytest fixtures.
    """
    
    @pytest.fixture(autouse=True)
    def setup_compmake(self):
        """Setup compmake test environment before each test."""
        # Create test directory
        self.root0 = mkdtemp()
        self.root = os.path.join(self.root0, 'compmake')
        self.db = StorageFilesystem(self.root, compress=True)
        self.cc = Context(db=self.db)
        
        # Configure compmake
        set_compmake_config('interactive', False)
        set_compmake_config('console_status', False)
        
        from compmake.constants import CompmakeConstants
        CompmakeConstants.debug_check_invariants = True
        
        # Call custom setup if defined
        self.mySetUp()
        
        yield  # This is where the test runs
        
        # Teardown after test completes
        if True:
            print(f'not deleting {self.root0}')
        else:
            rmtree(self.root0)
            
        from multiprocessing import active_children
        c = active_children()
        print(f'active children: {c}')
        if c:
            if True:
                msg = f'Still active children: {c}'
                logger.warning(msg)
            else:
                raise Exception(msg)
    
    def mySetUp(self):
        """Custom setup method that can be overridden by subclasses."""
        pass
    
    # Utility methods
    def comp(self, *args, **kwargs):
        """Invoke comp in the current context."""
        return self.cc.comp(*args, **kwargs)
    
    @contract(job_id=str, returns=Job)
    def get_job(self, job_id):
        """Get a job by ID."""
        db = self.cc.get_compmake_db()
        return get_job(job_id=job_id, db=db)
    
    def get_jobs(self, expression):
        """Returns the list of jobs corresponding to the given expression."""
        return list(parse_job_list(expression, context=self.cc))
    
    def assert_cmd_success(self, cmds):
        """Executes the (list of) commands and checks it was successful."""
        print(f'@ {cmds}')
        try:
            self.cc.batch_command(cmds)
        except MakeFailed as e:
            print('Detected MakeFailed')
            print(f'Failed jobs: {e.failed}')
            for job_id in e.failed:
                self.cc.interpret_commands_wrap(f'details {job_id}')
            raise  # Re-raise to fail the test
        except CommandFailed:
            raise
        
        self.cc.interpret_commands_wrap('check_consistency raise_if_error=1')
    
    def assert_cmd_fail(self, cmds):
        """Executes the (list of) commands and checks it fails as expected."""
        print(f'@ {cmds}     [supposed to fail]')
        try:
            self.cc.batch_command(cmds)
        except CommandFailed:
            pass
        else:
            msg = f'Command {cmds!r} did not fail.'
            raise Exception(msg)
    
    @contract(cmd_string=str)
    def assert_cmd_success_script(self, cmd_string):
        """Runs the "compmake_main" script which recreates the DB and context from disk."""
        ret = compmake_main([self.root, '--nosysexit', '-c', cmd_string])
        assert ret == 0, f"Command {cmd_string} failed with return code {ret}"
    
    # Other utility methods
    def assert_defined_by(self, job_id, expected):
        """Assert that a job is defined by the expected value."""
        assert self.get_job(job_id).defined_by == expected
    
    def assertEqualSet(self, a, b):
        """Assert that two iterables contain the same elements (regardless of order)."""
        assert set(a) == set(b), f"Sets differ: {set(a)} != {set(b)}"
    
    @contract(expr=str)
    def assertJobsEqual(self, expr, jobs, ignore_dyn_reports=True):
        """Assert that the jobs matching an expression equal the expected list."""
        js = self.get_jobs(expr)
        if ignore_dyn_reports:
            js = [x for x in js if 'dynreports' not in x]
        try:
            self.assertEqualSet(js, jobs)
        except AssertionError:
            print(f'expr {expr!r} -> {js}')
            print(f'differs from {jobs}')
            raise
    
    def assertMakeFailed(self, func, nfailed, nblocked):
        """Assert that a function raises MakeFailed with the expected number of failures."""
        try:
            func()
            pytest.fail("Expected MakeFailed but no exception was raised")
        except MakeFailed as e:
            if len(e.failed) != nfailed:
                msg = f'Expected {nfailed} failed, got {len(e.failed)}: {e.failed}'
                raise Exception(msg)
            if len(e.blocked) != nblocked:
                msg = f'Expected {nblocked} blocked, got {len(e.blocked)}: {e.blocked}'
                raise Exception(msg)
        except Exception as e:
            raise Exception(f'unexpected: {e}')
    
    def assert_job_uptodate(self, job_id, status):
        """Assert that a job's up-to-date status matches expectations."""
        res = self.up_to_date(job_id)
        assert res == status, f'Want {job_id!r} uptodate? {status}, got {res}'
    
    @contract(returns=bool)
    def up_to_date(self, job_id):
        """Check if a job is up to date."""
        from compmake.jobs.uptodate import CacheQueryDB
        cq = CacheQueryDB(db=self.db)
        up, reason, timestamp = cq.up_to_date(job_id)
        print(f'up_to_date({job_id!r}): {up}, {reason!r}, {timestamp}')
        return up


class QuickappTestBase(CompmakeTestBase):
    """Utilities for quickapp testing with pytest, replacing QuickappTest."""
    
    def run_quickapp(self, qapp, cmd: str):
        """Run a quickapp with the given command."""
        args = ['-o', self.root0, '-c', cmd, '--compress']
        result = quickapp_main(qapp, args, sys_exit=False)
        assert result == 0, f"Quickapp command failed with return code {result}"
        
        # tell the context that it's all good
        jobs = all_jobs(self.db)
        self.cc.reset_jobs_defined_in_this_session(jobs)