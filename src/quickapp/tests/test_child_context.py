#!/usr/bin/env python
from nose.tools import istest

from compmake.unittests.compmake_test import CompmakeTest
from quickapp import QuickApp, quickapp_main
from quickapp.app_utils import iterate_context_names
from quickapp.compmake_context import CompmakeContext


def f(name):
    print(name)
    return name

def define_jobs(context, id_name):
    print('in define_jobs(): executing: %s' % context.currently_executing)
    assert isinstance(context, CompmakeContext)
    context.comp(f, id_name)

class QuickAppDemoChild(QuickApp):

    def define_options(self, params):
        pass

    def define_jobs_context(self, context):
        names = ['a', 'b', 'c']
        for c, id_name in iterate_context_names(context, names):
            define_jobs(c, id_name)
# XXX
# @istest
class CompappTestDynamic(CompmakeTest):

    def compapp_test1(self):
        args = '--contracts -o %s -c make' % self.root0
        ret_found = quickapp_main(QuickAppDemoChild, args.split(), sys_exit=False)
        self.assertEqual(0, ret_found)
        self.assertJobsEqual('all', ['a-f', 'b-f', 'c-f'])


class QuickAppDemoChild2(QuickApp):

    def define_options(self, params):
        pass

    def define_jobs_context(self, context):
        names = ['a', 'b', 'c']
        for c, id_name in iterate_context_names(context, names):
            print('in define_jobs_context(): executing: %s' % context.currently_executing)
            c.comp_dynamic(define_jobs, id_name)


@istest
class CompappTestDynamic2(CompmakeTest):

    def compapp_test1(self):
        # Define and list
        args = ['-o', self.root0, '-c', 'ls']
        self.assertEqual(0, quickapp_main(QuickAppDemoChild2, args,
                                          sys_exit=False))

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


