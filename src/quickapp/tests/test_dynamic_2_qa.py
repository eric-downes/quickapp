from nose.tools import istest

from quickapp import QuickApp, iterate_context_names
from .quickappbase import QuickappTest


def f(name):
    print(name)
    return name

def define_jobs2(context, id_name):
    print('in define_jobs(): executing: %s' % context.currently_executing)
    context.comp(f, id_name)

def define_jobs1(context, id_name):
    print('in define_jobs(): executing: %s' % context.currently_executing)
    context.comp_dynamic(define_jobs2, id_name)

class QuickAppDemoChild3(QuickApp):

    def define_options(self, params):
        pass

    def define_jobs_context(self, context):
        names = ['a', 'b']
        for c, id_name in iterate_context_names(context, names):
            c.comp_dynamic(define_jobs1, id_name)

@istest
class TestDynamic2(QuickappTest):

    howmany = None  # used by cases()

    def test_dynamic1(self):
        self.run_quickapp(qapp=QuickAppDemoChild3, cmd='ls')
        self.assertJobsEqual('all', ['a-context',
                                     'b-context',
                                     'a-define_jobs1',
                                     'b-define_jobs1'])
        self.assert_cmd_success('make;ls')
        self.assertJobsEqual('all', ['a-context',
                                     'b-context',
                                     'a-define_jobs1',
                                     'b-define_jobs1',
                                     'a-define_jobs2',
                                     'b-define_jobs2',
                                     ])
        self.assert_cmd_success('make;ls')
        self.assertJobsEqual('all', ['a-context',
                                     'b-context',
                                     'a-define_jobs1',
                                     'b-define_jobs1',
                                     'a-define_jobs2',
                                     'b-define_jobs2',
                                     'a-f',
                                     'b-f'
                                     ])
        self.assert_cmd_success('details a-f')


