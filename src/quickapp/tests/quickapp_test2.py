#!/usr/bin/env python
from quickapp import QuickApp
from reprep import Report
import sys

def actual_computation(param1, param2):
    pass

def report(param2, jobs):
    r = Report()
    
    return r

class QuickAppDemo2(QuickApp):
    
    def define_options(self, params):
        params.add_int('param1', help='First parameter', default=1)
        params.add_int('param2', help='Second parameter', compulsory=True)
        
    def define_jobs(self):
        options = self.get_options()
        param1 = options.param1
        param2 = options.param2
        samples = self.comp(actual_computation, param1=param1, param2=param2)
        
        rj = self.comp(report, param2, samples)
        self.add_report(rj, report)
        
def compapp_test1():
    args = ['-o', 'quickapp_test1',
            '-c', 'make all', '--param1', '10', '--param2', '1,2,3']
    QuickAppDemo2().main(args)
    

if __name__ == '__main__':
    sys.exit(QuickAppDemo2().main())
    
