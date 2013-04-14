#!/usr/bin/env python
from quickapp.library.app_commands.app_with_commands import (QuickMultiCmdApp,
    add_subcommand, QuickMultiCmd)
from quickapp.library.app.quickapp_imp import quickapp_main


class DemoApp(QuickMultiCmdApp):
    cmd = 'dp'
    
    def define_options(self, params):
        params.add_string('config', help='Config Joint')
        params.add_int('param2', help='Second parameter', compulsory=True)

    def initial_setup(self):
        options = self.get_options()
        self.info('Loading configuration from %r.' % options.config)
        self.info('My param2 is %r.' % options.param2)
        


class DemoAppCmd1(QuickMultiCmd):
    cmd = 'cmd1'
    short = 'First command'
    
    def define_options(self, params):
        params.add_int('param1', help='First parameter', default=1)
        params.add_int('param2', help='Second parameter', compulsory=True)
        
    def define_jobs(self):
        options = self.get_options()
        self.info('My param2 is %r.' % options.param2)
        
add_subcommand(DemoApp, DemoAppCmd1)



class DemoAppCmd2(QuickMultiCmd):
    cmd = 'cmd2'
    short = 'Second command'
    
    def define_options(self, params):
        params.add_int('param1', help='First parameter', default=1)
        
    def define_jobs(self):
        pass

add_subcommand(DemoApp, DemoAppCmd2)
        

def subcommands_test1():
    args = ['-o', 'quickapp_test1',
            '-c', 'make all', '--param1', '10', '--param2', '42']
    quickapp_main(DemoApp, args=args)
    

if __name__ == '__main__':
    quickapp_main(DemoApp)
    
