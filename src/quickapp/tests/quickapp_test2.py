#!/usr/bin/env python
from quickapp import QuickApp, QUICKAPP_USER_ERROR, QUICKAPP_COMPUTATION_ERROR
from reprep import Report
from quickapp.library.app.quickapp_imp import quickapp_main
from unittest.case import TestCase

def actual_computation(param1, param2):
    print('computing (%s %s)' % (param1, param2))
    return [1, 2, 3, 4]

def report_example(param2, samples):
    print('report_example(%s, %s)' % (param2, samples))
    if param2 == -1:
        print('generating exception')
        raise Exception('fake exception')
    r = Report()
    r.text('samples', str(samples))
    print('creating report')
    return r

class QuickAppDemo2(QuickApp):
    
    cmd = 'quick-app-demo'
    
    def define_options(self, params):
        params.add_int('param1', help='First parameter', default=1)
        params.add_int('param2', help='Second parameter', compulsory=True)
        
    def define_jobs_context(self, context):
        options = self.get_options()
        param1 = options.param1
        param2 = options.param2
        samples = context.comp(actual_computation, param1=param1, param2=param2)
        
        rj = context.comp(report_example, param2, samples)
        context.add_report(rj, 'report_example')
        
        
class CompappTest1(TestCase):
    
    def compapp_test1(self):
        cases = []
        
        def add(args, ret):
            cases.append(dict(args=args, ret=ret))
            
        add('--contracts -o quickapp_test1 -c clean;make --param1 10 --param2 1', 0)

        # parse error
        add('--contracts -o quickapp_test2 -c clean;make  --param1 10 --parm2 1',
            QUICKAPP_USER_ERROR)  

        # computation exception
        add('--contracts -o quickapp_test2 -c clean;make  --param1 10 --param2 -1',
            QUICKAPP_COMPUTATION_ERROR)  

        for c in cases:
            args = c['args']
            if isinstance(args, str):
                args = args.split()
            ret = c['ret']
            ret_found = quickapp_main(QuickAppDemo2, args, sys_exit=False)
            msg = 'Expected %d, got %d.\nArguments: %s ' % (ret, ret_found, c['args'])   
            self.assertEqual(ret, ret_found, msg)    

if __name__ == '__main__':
    quickapp_main(QuickAppDemo2)
    

