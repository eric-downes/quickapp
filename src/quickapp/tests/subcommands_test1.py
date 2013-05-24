#!/usr/bin/env python
from quickapp import QuickMultiCmdApp, quickapp_main


class DemoApp(QuickMultiCmdApp):
    cmd = 'dp'
    
    def define_options(self, params):
        params.add_string('config', help='Config Joint')
        params.add_int('param2', help='Second parameter')

    def initial_setup(self):
        options = self.get_options()
        self.info('Loading configuration from %r.' % options.config)
        self.info('My param2 is %r.' % options.param2)
        


class DemoAppCmd1(DemoApp.get_sub()):
    cmd = 'cmd1'
    short = 'First command'
    
    def define_options(self, params):
        params.add_int('param1', help='First parameter', default=1)
        params.add_int('param2', help='Second parameter')
        
    def define_jobs(self):
        options = self.get_options()
        self.info('My param2 is %r.' % options.param2)
        



class DemoAppCmd2(DemoApp.sub):
    cmd = 'cmd2'
    short = 'Second command'
    
    def define_options(self, params):
        params.add_int('param1', help='First parameter', default=1)
        
    def define_jobs(self):
        pass

        

def subcommands_test1():
    args = ['-o', 'quickapp_test1',
            '-c', 'make all', '--param1', '10', '--param2', '42']
    quickapp_main(DemoApp, args=args)
    

if __name__ == '__main__':
    quickapp_main(DemoApp)
    
