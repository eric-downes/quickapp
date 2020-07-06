from compmake.jobs.storage import all_jobs
from compmake.unittests.compmake_test import CompmakeTest
from quickapp import quickapp_main


class QuickappTest(CompmakeTest):
    """ Utilities for quickapp testing """

    def run_quickapp(self, qapp, cmd: str):
        args = ['-o', self.root0, '-c', cmd, '--compress']
        self.assertEqual(0, quickapp_main(qapp, args, sys_exit=False))

        # tell the context that it's all good
        jobs = all_jobs(self.db)
        self.cc.reset_jobs_defined_in_this_session(jobs)
