from contracts import contract
from compmake.unittests.compmake_test import CompmakeTest
from quickapp.quick_app import quickapp_main

class QuickappTest(CompmakeTest):
    """ Utilities for quickapp testing """

    @contract(cmd=str)
    def run_quickapp(self, qapp, cmd):
        args = ['-o', self.root0, '-c', cmd]
        self.assertEqual(0, quickapp_main(qapp, args, sys_exit=False))
