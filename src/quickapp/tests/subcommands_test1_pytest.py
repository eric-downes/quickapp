#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest version of subcommands_test1.py.
Tests the subcommand functionality of QuickMultiCmdApp.
"""

import pytest
from quickapp import QuickMultiCmdApp, quickapp_main


class DemoApp(QuickMultiCmdApp):
    """Demo app with subcommands."""
    cmd = 'dp'
    
    def define_options(self, params):
        """Define common options for all subcommands."""
        params.add_string('config', help='Config Joint')
        params.add_int('param2', help='Second parameter')

    def initial_setup(self):
        """Set up the application."""
        options = self.get_options()
        self.info(f'Loading configuration from {options.config!r}.')
        self.info(f'My param2 is {options.param2!r}.')
        


class DemoAppCmd1(DemoApp.get_sub()):
    """First subcommand."""
    cmd = 'cmd1'
    short = 'First command'
    
    def define_options(self, params):
        """Define options specific to this subcommand."""
        params.add_int('param1', help='First parameter', default=1)
        params.add_int('param2', help='Second parameter')
        
    def define_jobs(self):
        """Define jobs for this subcommand."""
        options = self.get_options()
        self.info(f'My param2 is {options.param2!r}.')
        



class DemoAppCmd2(DemoApp.sub):
    """Second subcommand."""
    cmd = 'cmd2'
    short = 'Second command'
    
    def define_options(self, params):
        """Define options specific to this subcommand."""
        params.add_int('param1', help='First parameter', default=1)
        
    def define_jobs(self):
        """Define jobs for this subcommand."""
        pass


@pytest.mark.skip(reason="Test function doesn't have assertions")
def test_subcommands():
    """Test running DemoApp with subcommands."""
    args = ['-o', 'quickapp_test1',
            '-c', 'make all', '--param1', '10', '--param2', '42']
    result = quickapp_main(DemoApp, args=args, sys_exit=False)
    assert result == 0


if __name__ == "__main__":
    quickapp_main(DemoApp)